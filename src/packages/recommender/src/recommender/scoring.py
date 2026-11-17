"""Weighted evidence scoring and similarity metrics for recommendations."""

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from math import exp, isfinite
from typing import Any, Final

import msgspec
import numpy as np

from anime_catalogue.demographics import DEMOGRAPHIC_AFFINITY, parse_demographic
from anime_catalogue.subsumption import (
    ALL_ANCESTOR_TOKENS,
    NON_THEMATIC_ORTHOGONAL_TAGS,
    SIBLING_TRANSFER_FACTOR,
    SIBLINGS_BY_TOKEN,
    TaxonomyToken,
    prune_ancestor_tokens,
)
from anime_catalogue.taxonomy import (
    SETTING_BACKDROP_THEMES,
    Genre,
    Theme,
    safe_parse_genre,
    safe_parse_theme,
)
from features.tags import (
    Tag,
    get_tag_salience,
    similarity_tag_ids,
)
from normalization.metadata import AnimeType
from recommender.clash_rules import (
    ClashFlag,
    compile_anchor_clash_rules,
    evaluate_compiled_clash_rules,
    evaluate_compiled_clash_rules_batch,
    extract_clash_flags,
    normalize_clash_tokens,
)
from recommender.contracts import RecommendationItem
from recommender.guards import (
    GENERIC_BROAD_GENRE_DAMPING_FACTOR,
    GENERIC_BROAD_GENRE_NARRATIVE_THRESHOLD,
    GENERIC_BROAD_GENRES,
    GENERIC_BROAD_THEME_DAMPING_FACTOR,
    GENERIC_BROAD_THEME_NARRATIVE_THRESHOLD,
    HOOK_TAG_SALIENCE_MULTIPLIER,
    MIN_SHARED_HOOK_TAGS_FOR_PROMOTION,
    NON_NARRATIVE_TAGS,
    PERSONA_ONLY_DAMPING_COSINE_THRESHOLD,
    PERSONA_ONLY_DAMPING_FACTOR,
    SPARSE_ANCHOR_GENRE_DAMPING_FACTOR,
    SPARSE_ANCHOR_NARRATIVE_THRESHOLD,
    SPECIFIC_HOOK_AND_TONE_TAGS,
    STORYLINE_ENTRYPOINT_COHERENCE_COSINE_THRESHOLD,
    STORYLINE_ENTRYPOINT_COHERENCE_DAMPING_FACTOR,
)
from recommender.language_policy import (
    LanguageCompatibilityPolicy,
)
from recommender.metrics import idf_tversky
from recommender.ranking import RankingPolicy, ScoredCandidate, ScoreDescending
from recommender.rating_policy import RatingPolicy
from recommender.structure_policy import (
    NarrativeProfile,
    NarrativeStructurePolicy,
    resolve_narrative_profile,
)
from recommender.union import UnionCandidate

SYNOPSIS_WEIGHT = 0.41
TAG_WEIGHT = 0.20
THEME_WEIGHT = 0.17
GENRE_WEIGHT = 0.16
DEMOGRAPHIC_WEIGHT = 0.06
CROSS_GROUP_CONFIDENCE_MULTIPLIER = 0.04
NEIGHBOURHOOD_QUALIFICATION_MAX_RANK = 35
EVIDENCE_SYNOPSIS_THRESHOLD = 0.08
EVIDENCE_TAG_THRESHOLD = 0.22
EVIDENCE_THEME_THRESHOLD = 0.15
EVIDENCE_GENRE_THRESHOLD = 0.28
GATED_TRANSFER_THRESHOLD = 0.08
GATED_TRANSFER_FACTOR = 0.50
EMBEDDING_GATE_LOW = 0.42
EMBEDDING_GATE_HIGH = 0.54
EMBEDDING_CONFIDENCE_GATE = EMBEDDING_GATE_HIGH
SIGMOID_GATE_SLOPE = 8.0
SIGMOID_GATE_CENTER = 0.35
SYNOPSIS_FUSION_EPSILON = 0.02
GEOMETRIC_FUSION_WEIGHT = 0.65
ARITHMETIC_FUSION_WEIGHT = 0.35
DEFAULT_SYNOPSIS_SCORING_PATHS = ('bm25', 'lsa', 'embedding')
LOW_SEMANTIC_SOFT_FLOOR_COSINE_THRESHOLD: Final[float] = 0.38
LOW_SEMANTIC_SOFT_FLOOR_FACTOR: Final[float] = 0.60
TIER1_CORROBORATION_SYNERGY_COSINE_THRESHOLD: Final[float] = 0.40
TIER1_CORROBORATION_SYNERGY_FACTOR: Final[float] = 1.15
DEFAULT_SYNOPSIS_PATH_WEIGHTS: Final[Mapping[str, float]] = {
    'embedding': 0.55,
    'lsa': 0.25,
    'bm25': 0.20,
}
BM25_SCALE_FACTOR: Final[float] = 2.0
LEAF_SPORT_TAGS: Final[frozenset[Tag]] = frozenset(
    {Tag.BASEBALL, Tag.BASKETBALL, Tag.VOLLEYBALL, Tag.SOCCER, Tag.TENNIS}
)


def fuse_synopsis_scores(
    bm25: float,
    lsa: float,
    embedding: float,
    *,
    eps: float = SYNOPSIS_FUSION_EPSILON,
    geom_weight: float = GEOMETRIC_FUSION_WEIGHT,
    arith_weight: float = ARITHMETIC_FUSION_WEIGHT,
    active_paths: Sequence[str] = DEFAULT_SYNOPSIS_SCORING_PATHS,
    path_weights: Mapping[str, float] = DEFAULT_SYNOPSIS_PATH_WEIGHTS,
    bm25_scale_factor: float = BM25_SCALE_FACTOR,
) -> float:
    """Fuse active synopsis similarities using calibrated Blend 25% geometric/arithmetic fusion.

    Blends 75% smoothed geometric mean with 25% arithmetic mean across the weighted channels.
    BM25 is pre-scaled by bm25_scale_factor (default 2.0) to align with dense semantic ranges.
    Inputs are clipped to non-negative finite values.
    """
    scaled_bm25 = min(1.0, max(0.0, bm25 if isfinite(bm25) else 0.0) * bm25_scale_factor)
    values = {
        'bm25': scaled_bm25,
        'lsa': max(0.0, lsa if isfinite(lsa) else 0.0),
        'embedding': max(0.0, embedding if isfinite(embedding) else 0.0),
    }
    selected_paths = [p for p in active_paths if p in values]
    if not selected_paths or not any(values[p] > 0.0 for p in selected_paths):
        return 0.0

    raw_weights = [path_weights.get(p, 1.0 / len(selected_paths)) for p in selected_paths]
    total_weight = sum(raw_weights)
    if total_weight <= 0.0:
        return 0.0
    normalized_weights = [w / total_weight for w in raw_weights]

    arithmetic_score = sum(w * values[p] for w, p in zip(normalized_weights, selected_paths, strict=True))
    product = 1.0
    for w, p in zip(normalized_weights, selected_paths, strict=True):
        product *= (values[p] + eps) ** w
    geometric_score = max(0.0, product - eps)
    return geom_weight * geometric_score + arith_weight * arithmetic_score


def fuse_synopsis_vectors(
    bm25: np.ndarray,
    lsa: np.ndarray,
    embedding: np.ndarray,
    *,
    eps: float = SYNOPSIS_FUSION_EPSILON,
    geom_weight: float = GEOMETRIC_FUSION_WEIGHT,
    arith_weight: float = ARITHMETIC_FUSION_WEIGHT,
    active_paths: Sequence[str] = DEFAULT_SYNOPSIS_SCORING_PATHS,
    path_weights: Mapping[str, float] = DEFAULT_SYNOPSIS_PATH_WEIGHTS,
    bm25_scale_factor: float = BM25_SCALE_FACTOR,
) -> np.ndarray:
    """Vectorized active-path calibrated Blend 25% geometric/arithmetic fusion matching fuse_synopsis_scores."""
    b_clean = np.minimum(1.0, np.maximum(0.0, np.nan_to_num(bm25, nan=0.0, posinf=0.0, neginf=0.0)) * bm25_scale_factor)
    l_clean = np.maximum(0.0, np.nan_to_num(lsa, nan=0.0, posinf=0.0, neginf=0.0))
    e_clean = np.maximum(0.0, np.nan_to_num(embedding, nan=0.0, posinf=0.0, neginf=0.0))
    values = {'bm25': b_clean, 'lsa': l_clean, 'embedding': e_clean}
    selected_paths = [p for p in active_paths if p in values]
    if not selected_paths:
        return np.zeros_like(b_clean)

    raw_weights = [path_weights.get(p, 1.0 / len(selected_paths)) for p in selected_paths]
    total_weight = sum(raw_weights)
    if total_weight <= 0.0:
        return np.zeros_like(b_clean)
    normalized_weights = [w / total_weight for w in raw_weights]

    a_sims = sum(w * values[p] for w, p in zip(normalized_weights, selected_paths, strict=True))
    product = np.ones_like(b_clean)
    for w, p in zip(normalized_weights, selected_paths, strict=True):
        product *= (values[p] + eps) ** w
    g_sims = np.maximum(0.0, product - eps)

    all_zero_mask = np.logical_and.reduce([values[p] == 0.0 for p in selected_paths])
    return np.where(
        all_zero_mask,
        0.0,
        geom_weight * g_sims + arith_weight * a_sims,
    )


ANIME_TYPE_AFFINITY: Mapping[tuple[str, str], float] = {
    (AnimeType.TV, AnimeType.TV): 1.00,
    (AnimeType.ONA, AnimeType.ONA): 1.00,
    (AnimeType.MOVIE, AnimeType.MOVIE): 1.00,
    (AnimeType.TV, AnimeType.ONA): 0.88,
    (AnimeType.ONA, AnimeType.MOVIE): 0.75,
    (AnimeType.TV, AnimeType.MOVIE): 0.60,
}

SEMANTIC_GROUP_PATHS = frozenset({'bm25', 'lsa', 'embedding', 'char_3_5g_tfidf', 'char_tfidf', 'char'})
STRUCTURED_GROUP_PATHS = frozenset({'genres', 'themes', 'tags'})
NEIGHBOURHOOD_GROUP_PATHS = frozenset({'weighted-v2'})


ScoringMetric = Callable[[frozenset[str], Sequence[str] | frozenset[str]], float]
PropertyValues = Mapping[int, Sequence[str] | frozenset[str]]


def sigmoid_embedding_gate(
    similarity: float,
    *,
    slope: float = SIGMOID_GATE_SLOPE,
    center: float = SIGMOID_GATE_CENTER,
) -> float:
    """Continuously attenuate embedding confidence via logistic sigmoid without a hard-zero cutoff.

    g(e) = e / (1 + exp(-slope * (e - center)))
    """
    if not isfinite(similarity) or similarity <= 0.0:
        return 0.0
    weight = 1.0 / (1.0 + exp(-slope * (similarity - center)))
    return weight * similarity


def soft_embedding_gate(
    similarity: float,
    low: float = EMBEDDING_GATE_LOW,
    high: float = EMBEDDING_GATE_HIGH,
    *,
    use_sigmoid: bool | None = None,
    slope: float = SIGMOID_GATE_SLOPE,
    center: float = SIGMOID_GATE_CENTER,
) -> float:
    """Scale embedding confidence using continuous sigmoid attenuation (or legacy linear ramp)."""
    should_use_sigmoid = (
        use_sigmoid if use_sigmoid is not None else (low == EMBEDDING_GATE_LOW and high == EMBEDDING_GATE_HIGH)
    )
    if should_use_sigmoid:
        return sigmoid_embedding_gate(similarity, slope=slope, center=center)
    if similarity < low:
        return 0.0
    if similarity >= high:
        return similarity
    weight = (similarity - low) / (high - low)
    return weight * similarity


def demographic_piecewise_affinity(
    source_demographics: frozenset[str],
    candidate_demographics: Sequence[str] | frozenset[str] | None,
) -> float:
    """Calculate demographic affinity using canonical cohort proximity from anime_catalogue."""
    if not source_demographics or not candidate_demographics:
        return 0.0
    candidate_list = tuple(parse_demographic(c) for c in candidate_demographics if c)
    if not candidate_list:
        return 0.0

    max_affinities: list[float] = []
    for source_demographic in source_demographics:
        source_row = DEMOGRAPHIC_AFFINITY.get(parse_demographic(source_demographic), {})
        best_affinity = max(source_row.get(candidate_demographic, 0.0) for candidate_demographic in candidate_list)
        max_affinities.append(best_affinity)

    return sum(max_affinities) / len(max_affinities) if max_affinities else 0.0


def anime_type_piecewise_affinity(
    source_types: frozenset[str],
    candidate_types: Sequence[str] | frozenset[str] | None,
) -> float:
    """Calculate anime format affinity across TV, ONA, and MOVIE cohorts."""
    if not source_types or not candidate_types:
        return 0.0
    candidate_list = tuple(c.upper() for c in candidate_types if c)
    if not candidate_list:
        return 0.0

    max_affinities: list[float] = []
    for source_type in source_types:
        s_norm = source_type.upper()
        best_affinity = max(
            ANIME_TYPE_AFFINITY.get((s_norm, candidate_type)) or ANIME_TYPE_AFFINITY.get((candidate_type, s_norm), 0.0)
            for candidate_type in candidate_list
        )
        max_affinities.append(best_affinity)

    return sum(max_affinities) / len(max_affinities) if max_affinities else 0.0


class ScoringProperty(msgspec.Struct, frozen=True):
    """Describe one metadata contribution and its replaceable metric."""

    name: str
    weight: float
    metric: ScoringMetric
    metric_identity: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError('scoring property name cannot be empty')
        if not isfinite(self.weight) or self.weight < 0.0:
            raise ValueError('scoring property weight cannot be negative')
        if self.metric_identity is not None and not self.metric_identity.strip():
            raise ValueError('metric identity cannot be empty')


def make_idf_tversky(
    *,
    alpha: float = 0.8,
    beta: float = 0.2,
    idf_map: Mapping[str, float] | None = None,
) -> ScoringMetric:
    """Create an IDF-weighted Tversky scoring metric."""
    if not isfinite(alpha) or not isfinite(beta) or alpha < 0.0 or beta < 0.0:
        raise ValueError('Tversky alpha and beta must be finite and non-negative')
    if idf_map is not None and any(not isfinite(value) or value < 0.0 for value in idf_map.values()):
        raise ValueError('IDF weights must be finite and non-negative')

    def metric(source: frozenset[str], candidate: Sequence[str] | frozenset[str]) -> float:
        return idf_tversky(source, candidate, alpha=alpha, beta=beta, idf_map=idf_map)

    return metric


def make_salience_weighted_tag_metric(*, idf_map: Mapping[str, float] | None = None) -> ScoringMetric:
    """Create a salience- and IDF-weighted Tversky metric combining narrative tiers with corpus frequency."""
    salience_cache: dict[str, float] = {}

    def metric(left: Iterable[str], right: Iterable[str]) -> float:
        set_left = frozenset(similarity_tag_ids(left))
        set_right = frozenset(similarity_tag_ids(right))
        if not set_left or not set_right:
            return 0.0
        matched = set_left & set_right
        if not matched:
            return 0.0
        for tag in set_left | set_right:
            if tag not in salience_cache:
                tier_w = get_tag_salience(tag)
                if idf_map is not None:
                    raw_idf = idf_map.get(tag, 1.0)
                    tier_w = tier_w * (raw_idf**0.5)
                salience_cache[tag] = tier_w
        matched_weight = sum(salience_cache[t] for t in matched)
        left_only = sum(salience_cache[t] for t in (set_left - set_right))
        right_only = sum(salience_cache[t] for t in (set_right - set_left))
        denom = matched_weight + 0.8 * left_only + 0.2 * right_only
        return matched_weight / denom if denom > 0.0 else 0.0

    return metric


def default_scoring_properties(
    *,
    tag_idf: Mapping[str, float] | None = None,
    theme_idf: Mapping[str, float] | None = None,
    genre_idf: Mapping[str, float] | None = None,
) -> tuple[ScoringProperty, ...]:
    """Return the default metadata scoring policy in stable order."""
    tag_metric = make_salience_weighted_tag_metric(idf_map=tag_idf)
    tag_identity = 'salience-weighted-tversky-82-content-v2'
    return (
        ScoringProperty(
            'tags',
            TAG_WEIGHT,
            tag_metric,
            tag_identity,
        ),
        ScoringProperty(
            'themes',
            THEME_WEIGHT,
            make_idf_tversky(alpha=0.75, beta=0.25, idf_map=theme_idf),
            'idf-tversky-7525-v1',
        ),
        ScoringProperty(
            'genres',
            GENRE_WEIGHT,
            make_idf_tversky(alpha=0.6, beta=0.4, idf_map=genre_idf),
            'idf-tversky-64-v1',
        ),
        ScoringProperty(
            'demographics',
            DEMOGRAPHIC_WEIGHT,
            demographic_piecewise_affinity,
            'piecewise-affinity-v1',
        ),
    )


def to_recommendation_item(anime_id: int, score: float) -> RecommendationItem:
    """Map a scored candidate to the lightweight result contract."""
    return RecommendationItem(
        anime_id=anime_id,
        score=score,
        contributions=(('normalized_fusion', score),),
    )


@dataclass(frozen=True, slots=True)
class _SourceScoringContext:
    """Resolved source-anime properties, taxonomy tokens, and compiled guard state."""

    active_properties: tuple[ScoringProperty, ...]
    candidate_values: dict[str, PropertyValues]
    source_values: dict[str, frozenset[str]]
    source_genres: frozenset[Genre]
    source_themes: frozenset[Theme]
    source_tags: frozenset[Tag]
    source_all_tokens: frozenset[TaxonomyToken]
    source_thematic_leaves: frozenset[TaxonomyToken]
    anchor_sibling_hypernyms: dict[object, list[tuple[object, object]]]
    source_struct: NarrativeProfile | None
    source_clash_mask: ClashFlag
    anchor_clash_rules: tuple[tuple[int, float, float | None], ...]
    source_language: str | None
    source_rating: str | None
    source_demos: Sequence[str] | frozenset[str]
    source_raw_themes: frozenset[str]
    source_clean_tags: frozenset[str]


@dataclass(frozen=True, slots=True)
class _BaseSimilarityResult:
    """Vectorized synopsis and metadata similarity scores across candidates."""

    synopsis_scores: np.ndarray
    content_scores: np.ndarray
    prop_sim_arrays: dict[str, np.ndarray]
    cand_indices: list[int]
    batch_tone_multipliers: np.ndarray | None


def _prepare_source_scoring_context(
    source_anime_id: int,
    *,
    genres_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    themes_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    tags_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    demographics_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    ratings_by_id: Mapping[int, str] | None,
    properties: Sequence[ScoringProperty] | None,
    property_values: Mapping[str, PropertyValues] | None,
    clash_masks_by_id: Mapping[int, ClashFlag] | None,
    structure_policy: NarrativeStructurePolicy | None,
    narrative_profiles_by_id: Mapping[int, NarrativeProfile] | None,
    languages_by_id: Mapping[int, str] | None,
    synopses_by_id: Mapping[int, str | None] | None,
    taxonomy_tokens_by_id: Mapping[int, frozenset[TaxonomyToken]] | None,
    thematic_leaf_tokens_by_id: Mapping[int, frozenset[TaxonomyToken]] | None,
    similarity_tags_by_id: Mapping[int, frozenset[str]] | None,
    parsed_genres_by_id: Mapping[int, frozenset[Genre]] | None,
    parsed_themes_by_id: Mapping[int, frozenset[Theme]] | None,
    tag_enums_by_id: Mapping[int, frozenset[Tag]] | None,
) -> _SourceScoringContext:
    """Validate scoring properties and resolve precomputed source metadata."""
    default_values: dict[str, PropertyValues] = {
        'tags': tags_by_id,
        'themes': themes_by_id,
        'genres': genres_by_id,
        'demographics': demographics_by_id,
    }
    candidate_values = {**default_values, **(property_values or {})}
    active_properties = tuple(properties) if properties is not None else default_scoring_properties()
    property_names = tuple(property_spec.name for property_spec in active_properties)
    if len(set(property_names)) != len(property_names):
        raise ValueError('scoring property names must be unique')
    unknown_properties = set(property_names) - set(candidate_values)
    if unknown_properties:
        raise ValueError(f'unsupported scoring properties: {", ".join(sorted(unknown_properties))}')

    source_values = {
        name: (
            similarity_tags_by_id[source_anime_id]
            if name == 'tags' and similarity_tags_by_id is not None and source_anime_id in similarity_tags_by_id
            else frozenset(similarity_tag_ids(values.get(source_anime_id, ())))
            if name == 'tags'
            else frozenset(values.get(source_anime_id, ()))
        )
        for name, values in candidate_values.items()
    }
    if parsed_genres_by_id is not None and source_anime_id in parsed_genres_by_id:
        source_genres = parsed_genres_by_id[source_anime_id]
    else:
        source_genres = frozenset(g for label in source_values.get('genres', ()) if (g := safe_parse_genre(label)))

    if parsed_themes_by_id is not None and source_anime_id in parsed_themes_by_id:
        source_themes = parsed_themes_by_id[source_anime_id]
    else:
        source_themes = frozenset(th for label in source_values.get('themes', ()) if (th := safe_parse_theme(label)))

    if tag_enums_by_id is not None and source_anime_id in tag_enums_by_id:
        source_tags = tag_enums_by_id[source_anime_id]
    else:
        source_tags = frozenset(
            Tag(t) for t in source_values.get('tags', frozenset()) if isinstance(t, Tag) or t in Tag._value2member_map_
        )

    if taxonomy_tokens_by_id is not None and source_anime_id in taxonomy_tokens_by_id:
        source_all_tokens = taxonomy_tokens_by_id[source_anime_id]
    else:
        source_all_tokens = frozenset(source_genres | source_themes | source_tags)

    if thematic_leaf_tokens_by_id is not None and source_anime_id in thematic_leaf_tokens_by_id:
        source_thematic_leaves = thematic_leaf_tokens_by_id[source_anime_id]
    else:
        source_thematic_leaves = (source_all_tokens - NON_THEMATIC_ORTHOGONAL_TAGS) - ALL_ANCESTOR_TOKENS

    anchor_sibling_hypernyms: dict[object, list[tuple[object, object]]] = {}
    for anchor_token in source_all_tokens:
        token_siblings = SIBLINGS_BY_TOKEN.get(anchor_token)
        if token_siblings:
            for candidate_token, hypernym in token_siblings.items():
                anchor_sibling_hypernyms.setdefault(candidate_token, []).append((anchor_token, hypernym))

    source_struct = (
        (narrative_profiles_by_id.get(source_anime_id) if narrative_profiles_by_id is not None else None)
        or resolve_narrative_profile(
            frozenset(tags_by_id.get(source_anime_id, ())),
            synopses_by_id.get(source_anime_id) if synopses_by_id else None,
        )
        if structure_policy is not None
        else None
    )
    source_clash_mask = (
        clash_masks_by_id[source_anime_id]
        if clash_masks_by_id is not None and source_anime_id in clash_masks_by_id
        else extract_clash_flags(
            normalize_clash_tokens(
                (
                    *genres_by_id.get(source_anime_id, ()),
                    *themes_by_id.get(source_anime_id, ()),
                    *tags_by_id.get(source_anime_id, ()),
                )
            )
        )
    )
    anchor_clash_rules = compile_anchor_clash_rules(source_clash_mask)
    if similarity_tags_by_id is not None:
        source_clean_tags = similarity_tags_by_id.get(source_anime_id, frozenset())
    else:
        source_clean_tags = frozenset(similarity_tag_ids(tags_by_id.get(source_anime_id, ())))

    return _SourceScoringContext(
        active_properties=active_properties,
        candidate_values=candidate_values,
        source_values=source_values,
        source_genres=source_genres,
        source_themes=source_themes,
        source_tags=source_tags,
        source_all_tokens=source_all_tokens,
        source_thematic_leaves=source_thematic_leaves,
        anchor_sibling_hypernyms=anchor_sibling_hypernyms,
        source_struct=source_struct,
        source_clash_mask=source_clash_mask,
        anchor_clash_rules=anchor_clash_rules,
        source_language=languages_by_id.get(source_anime_id) if languages_by_id else None,
        source_rating=ratings_by_id.get(source_anime_id) if ratings_by_id is not None else None,
        source_demos=demographics_by_id.get(source_anime_id, ()),
        source_raw_themes=frozenset(themes_by_id.get(source_anime_id, ())),
        source_clean_tags=source_clean_tags,
    )


def _compute_base_similarity(
    source_anime_id: int,
    candidates: Sequence[UnionCandidate],
    source_ctx: _SourceScoringContext,
    *,
    property_values: Mapping[str, PropertyValues] | None,
    synopsis_pairwise_dense: Mapping[int, float] | None,
    rating_embedding_cosine: Mapping[int, float] | None,
    embedding_gate_low: float,
    embedding_gate_high: float,
    gated_synopsis_transfer: bool,
    pure_tone_contradiction_guard: bool,
    clash_masks_by_id: Mapping[int, ClashFlag] | None,
    synopsis_scoring_paths: Sequence[str],
    similarity_tags_by_id: Mapping[int, frozenset[str]] | None,
    tags_csr: tuple[Any, dict[str, int], np.ndarray] | None,
    themes_csr: tuple[Any, dict[str, int], np.ndarray] | None,
    genres_csr: tuple[Any, dict[str, int], np.ndarray] | None,
    index_by_id: Mapping[int, int] | None,
) -> _BaseSimilarityResult:
    """Compute vectorized synopsis, CSR metadata, and gated base content similarity."""
    num_candidates = len(candidates)
    batch_tone_multipliers: np.ndarray | None = None
    if pure_tone_contradiction_guard and clash_masks_by_id is not None and candidates:
        get_clash = clash_masks_by_id.get
        cand_masks = np.array([int(get_clash(c.anime_id, 0)) for c in candidates], dtype=np.int64)
        if rating_embedding_cosine is not None:
            get_cos = rating_embedding_cosine.get
            cand_cos = np.array([float(get_cos(c.anime_id, 0.50)) for c in candidates], dtype=np.float64)
        else:
            cand_cos = np.array(
                [next((float(e.score) for e in c.evidence if e.path == 'embedding'), 0.50) for c in candidates],
                dtype=np.float64,
            )
        batch_tone_multipliers = evaluate_compiled_clash_rules_batch(
            source_ctx.anchor_clash_rules, cand_masks, cand_cos, anchor_mask=int(source_ctx.source_clash_mask)
        )

    if synopsis_pairwise_dense is not None:
        synopsis_scores = np.array(
            [synopsis_pairwise_dense.get(c.anime_id, 0.0) for c in candidates],
            dtype=np.float64,
        )
    elif candidates:
        bm25_scores = np.zeros(num_candidates, dtype=np.float64)
        lsa_scores = np.zeros(num_candidates, dtype=np.float64)
        embedding_scores = np.zeros(num_candidates, dtype=np.float64)
        for index, candidate in enumerate(candidates):
            for item in candidate.evidence:
                if item.path == 'bm25':
                    bm25_scores[index] = item.score
                elif item.path == 'lsa':
                    lsa_scores[index] = item.score
                elif item.path == 'embedding':
                    embedding_scores[index] = soft_embedding_gate(
                        item.score, low=embedding_gate_low, high=embedding_gate_high
                    )
        synopsis_scores = fuse_synopsis_vectors(
            bm25_scores,
            lsa_scores,
            embedding_scores,
            active_paths=synopsis_scoring_paths,
        )
    else:
        synopsis_scores = np.zeros(num_candidates, dtype=np.float64)

    batch_prop_sims: dict[str, np.ndarray] = {}
    cand_indices: list[int] = []
    if index_by_id is not None and candidates:
        cand_indices = [index_by_id.get(c.anime_id, -1) for c in candidates]
        src_idx = index_by_id.get(source_anime_id)
        if src_idx is not None and all(idx >= 0 for idx in cand_indices):
            active_props_by_name = {prop.name: prop for prop in source_ctx.active_properties}
            overridden_properties = frozenset(property_values) if property_values is not None else frozenset()
            csr_configs: tuple[
                tuple[str, tuple[Any, dict[str, int], np.ndarray] | None, float, float, frozenset[str]], ...
            ] = (
                (
                    'tags',
                    tags_csr,
                    0.8,
                    0.2,
                    frozenset({'salience-weighted-tversky-82-content-v2', 'salience-weighted-tversky-82-v1'}),
                ),
                ('themes', themes_csr, 0.75, 0.25, frozenset({'idf-tversky-7525-v1'})),
                ('genres', genres_csr, 0.6, 0.4, frozenset({'idf-tversky-64-v1'})),
            )
            for prop_name, csr_bundle, a_w, b_w, expected_identities in csr_configs:
                prop_spec = active_props_by_name.get(prop_name)
                if (
                    csr_bundle is None
                    or prop_spec is None
                    or prop_name in overridden_properties
                    or prop_spec.metric_identity not in expected_identities
                ):
                    continue
                csr_mat, _, row_totals = csr_bundle
                inter_w = np.asarray((csr_mat[cand_indices] @ csr_mat[src_idx].T).toarray()).ravel()
                src_tot = float(row_totals[src_idx])
                cand_tots = row_totals[cand_indices]
                denom = inter_w + a_w * (src_tot - inter_w) + b_w * (cand_tots - inter_w)
                batch_prop_sims[prop_name] = np.divide(inter_w, denom, out=np.zeros_like(inter_w), where=denom > 0.0)

    raw_metadata_scores = np.zeros(num_candidates, dtype=np.float64)
    unavailable_weights = np.zeros(num_candidates, dtype=np.float64)
    prop_sim_arrays: dict[str, np.ndarray] = {}
    for property_spec in source_ctx.active_properties:
        name = property_spec.name
        source_property_values = source_ctx.source_values[name]
        if not source_property_values:
            unavailable_weights += property_spec.weight
            continue
        cand_map = source_ctx.candidate_values[name]
        if name == 'tags':
            cand_vals_list = [
                (
                    similarity_tags_by_id[c.anime_id]
                    if similarity_tags_by_id is not None and c.anime_id in similarity_tags_by_id
                    else similarity_tag_ids(cand_map.get(c.anime_id, ()))
                )
                if cand_map.get(c.anime_id, ())
                else ()
                for c in candidates
            ]
        else:
            cand_vals_list = [cand_map.get(c.anime_id, ()) for c in candidates]
        has_cand = np.fromiter((bool(v) for v in cand_vals_list), dtype=bool, count=num_candidates)
        batch_arr = batch_prop_sims.get(name)
        if batch_arr is not None:
            sims_arr = np.where(has_cand, batch_arr, 0.0)
        else:
            sims_arr = np.array(
                [
                    property_spec.metric(source_property_values, cand_vals_list[i]) if has_cand[i] else 0.0
                    for i in range(num_candidates)
                ],
                dtype=np.float64,
            )
        prop_sim_arrays[name] = sims_arr
        raw_metadata_scores += property_spec.weight * sims_arr
        unavailable_weights += np.where(has_cand, 0.0, property_spec.weight)

    if gated_synopsis_transfer:
        transfer_gates = np.minimum(1.0, synopsis_scores / GATED_TRANSFER_THRESHOLD)
        effective_synopsis_weights = np.where(
            unavailable_weights > 0.0,
            SYNOPSIS_WEIGHT + GATED_TRANSFER_FACTOR * unavailable_weights * transfer_gates,
            SYNOPSIS_WEIGHT,
        )
    else:
        effective_synopsis_weights = np.full(num_candidates, SYNOPSIS_WEIGHT, dtype=np.float64)

    content_scores = effective_synopsis_weights * synopsis_scores + raw_metadata_scores
    return _BaseSimilarityResult(
        synopsis_scores=synopsis_scores,
        content_scores=content_scores,
        prop_sim_arrays=prop_sim_arrays,
        cand_indices=cand_indices,
        batch_tone_multipliers=batch_tone_multipliers,
    )


def _compute_cross_group_score(
    candidate: UnionCandidate,
    candidate_index: int,
    synopsis_score: float,
    content_score: float,
    *,
    evidence_qualified_multiplier: bool,
    tags_sim_arr: np.ndarray | None,
    themes_sim_arr: np.ndarray | None,
    genres_sim_arr: np.ndarray | None,
) -> tuple[float, set[str]]:
    """Apply cross-group corroboration multiplier and collect candidate evidence paths."""
    candidate_paths: set[str] = set()
    has_neighbourhood = False
    for item in candidate.evidence:
        candidate_paths.add(item.path)
        if item.path in NEIGHBOURHOOD_GROUP_PATHS and item.rank <= NEIGHBOURHOOD_QUALIFICATION_MAX_RANK:
            has_neighbourhood = True
    has_semantic = bool(candidate_paths & SEMANTIC_GROUP_PATHS)
    has_structured = bool(candidate_paths & STRUCTURED_GROUP_PATHS)

    if evidence_qualified_multiplier:
        sem_qual = synopsis_score >= EVIDENCE_SYNOPSIS_THRESHOLD
        str_qual = (
            (tags_sim_arr is not None and float(tags_sim_arr[candidate_index]) >= EVIDENCE_TAG_THRESHOLD)
            or (themes_sim_arr is not None and float(themes_sim_arr[candidate_index]) >= EVIDENCE_THEME_THRESHOLD)
            or (genres_sim_arr is not None and float(genres_sim_arr[candidate_index]) >= EVIDENCE_GENRE_THRESHOLD)
        )
        present_groups = (1 if sem_qual else 0) + (1 if str_qual else 0) + (1 if has_neighbourhood else 0)
    else:
        present_groups = (1 if has_semantic else 0) + (1 if has_structured else 0) + (1 if has_neighbourhood else 0)

    r_cross = max(0, present_groups - 1)
    return content_score * (1.0 + CROSS_GROUP_CONFIDENCE_MULTIPLIER * r_cross), candidate_paths


def _resolve_candidate_taxonomy(
    candidate_id: int,
    cand_row: int,
    *,
    genres_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    themes_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    tags_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    parsed_genres_by_id: Mapping[int, frozenset[Genre]] | None,
    parsed_themes_by_id: Mapping[int, frozenset[Theme]] | None,
    tag_enums_by_id: Mapping[int, frozenset[Tag]] | None,
    taxonomy_tokens_by_id: Mapping[int, frozenset[TaxonomyToken]] | None,
    parsed_genres_by_row: Sequence[frozenset[Genre]] | None,
    parsed_themes_by_row: Sequence[frozenset[Theme]] | None,
    tag_enums_by_row: Sequence[frozenset[Tag]] | None,
    taxonomy_tokens_by_row: Sequence[frozenset[TaxonomyToken]] | None,
) -> tuple[frozenset[Genre], frozenset[Theme], frozenset[Tag], frozenset[TaxonomyToken]]:
    """Resolve candidate genres, themes, tags, and combined taxonomy tokens."""
    if parsed_genres_by_row is not None and cand_row >= 0:
        candidate_genres = parsed_genres_by_row[cand_row]
    elif parsed_genres_by_id is not None and candidate_id in parsed_genres_by_id:
        candidate_genres = parsed_genres_by_id[candidate_id]
    else:
        candidate_genres = frozenset(
            g for label in genres_by_id.get(candidate_id, ()) if (g := safe_parse_genre(label))
        )

    if parsed_themes_by_row is not None and cand_row >= 0:
        candidate_themes = parsed_themes_by_row[cand_row]
    elif parsed_themes_by_id is not None and candidate_id in parsed_themes_by_id:
        candidate_themes = parsed_themes_by_id[candidate_id]
    else:
        candidate_themes = frozenset(
            th for label in themes_by_id.get(candidate_id, ()) if (th := safe_parse_theme(label))
        )

    if tag_enums_by_row is not None and cand_row >= 0:
        candidate_tags = tag_enums_by_row[cand_row]
    elif tag_enums_by_id is not None and candidate_id in tag_enums_by_id:
        candidate_tags = tag_enums_by_id[candidate_id]
    else:
        candidate_tags = frozenset(
            Tag(t) for t in tags_by_id.get(candidate_id, ()) if isinstance(t, Tag) or t in Tag._value2member_map_
        )

    if taxonomy_tokens_by_row is not None and cand_row >= 0:
        candidate_all_tokens = taxonomy_tokens_by_row[cand_row]
    elif taxonomy_tokens_by_id is not None and candidate_id in taxonomy_tokens_by_id:
        candidate_all_tokens = taxonomy_tokens_by_id[candidate_id]
    else:
        candidate_all_tokens = frozenset(candidate_genres | candidate_themes | candidate_tags)

    return candidate_genres, candidate_themes, candidate_tags, candidate_all_tokens


def _compute_subsumption_multiplier(
    candidate_id: int,
    cand_row: int,
    source_ctx: _SourceScoringContext,
    candidate_all_tokens: frozenset[TaxonomyToken],
    *,
    thematic_leaf_tokens_by_id: Mapping[int, frozenset[TaxonomyToken]] | None,
    thematic_leaf_tokens_by_row: Sequence[frozenset[TaxonomyToken]] | None,
) -> float:
    """Compute taxonomy redundancy, sibling transfer, and leaf-specificity adjustment."""
    exact_matches = source_ctx.source_all_tokens & candidate_all_tokens
    deduped_exact = prune_ancestor_tokens(exact_matches)
    redundancy_factor = (
        (len(deduped_exact) / len(exact_matches)) ** 0.5 if len(exact_matches) > len(deduped_exact) else 1.0
    )

    has_exact_leaf_sport = not exact_matches.isdisjoint(LEAF_SPORT_TAGS)
    sibling_bonus = 0.0
    if not has_exact_leaf_sport:
        candidate_leaves = candidate_all_tokens - exact_matches
        seen_hypernyms: set[object] = set()
        for candidate_token in candidate_leaves:
            candidate_sibling_pairs = source_ctx.anchor_sibling_hypernyms.get(candidate_token)
            if candidate_sibling_pairs:
                for anchor_token, hypernym in candidate_sibling_pairs:
                    if anchor_token not in exact_matches and hypernym not in seen_hypernyms:
                        seen_hypernyms.add(hypernym)
                        sibling_bonus += SIBLING_TRANSFER_FACTOR * 0.04

    subsumption_multiplier = redundancy_factor * (1.0 + min(0.06, sibling_bonus))

    thematic_exact = exact_matches - NON_THEMATIC_ORTHOGONAL_TAGS
    if source_ctx.source_thematic_leaves and thematic_exact:
        if thematic_leaf_tokens_by_row is not None and cand_row >= 0:
            matched_thematic_leaves = thematic_exact & thematic_leaf_tokens_by_row[cand_row]
        elif thematic_leaf_tokens_by_id is not None and candidate_id in thematic_leaf_tokens_by_id:
            matched_thematic_leaves = thematic_exact & thematic_leaf_tokens_by_id[candidate_id]
        else:
            matched_thematic_leaves = thematic_exact - ALL_ANCESTOR_TOKENS

        if matched_thematic_leaves:
            subsumption_multiplier *= 1.10
        elif thematic_exact.issubset(ALL_ANCESTOR_TOKENS):
            subsumption_multiplier *= 0.90

    return subsumption_multiplier


def _apply_clash_and_tone_guards(
    score: float,
    candidate: UnionCandidate,
    candidate_index: int,
    entity_id: int,
    dense_cosine: float,
    source_ctx: _SourceScoringContext,
    candidate_genres: frozenset[Genre],
    candidate_themes: frozenset[Theme],
    candidate_tags: frozenset[Tag],
    *,
    pure_tone_contradiction_guard: bool,
    generic_genre_suppression: bool,
    hook_tag_promotion: bool,
    batch_tone_multipliers: np.ndarray | None,
    clash_masks_by_id: Mapping[int, ClashFlag] | None,
    rating_embedding_cosine: Mapping[int, float] | None,
    themes_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    tags_by_id: Mapping[int, Sequence[str] | frozenset[str]],
) -> float:
    """Apply tonal clash rules, hook-tag promotion, and generic-backdrop suppression guards."""
    tone_multiplier = 1.0
    if pure_tone_contradiction_guard:
        if batch_tone_multipliers is not None:
            tone_multiplier = float(batch_tone_multipliers[candidate_index])
        else:
            candidate_evidence_scores = {item.path: item.score for item in candidate.evidence}
            dense_cos = (
                rating_embedding_cosine.get(candidate.anime_id)
                if rating_embedding_cosine is not None and candidate.anime_id in rating_embedding_cosine
                else candidate_evidence_scores.get('embedding', 0.50)
            )
            dense_cosine_val = float(dense_cos) if dense_cos is not None else 0.50
            candidate_clash_mask = (
                clash_masks_by_id[candidate.anime_id]
                if clash_masks_by_id is not None and candidate.anime_id in clash_masks_by_id
                else extract_clash_flags(
                    normalize_clash_tokens((*candidate_genres, *candidate_themes, *candidate_tags))
                )
            )
            tone_multiplier = evaluate_compiled_clash_rules(
                source_ctx.anchor_clash_rules,
                candidate_clash_mask,
                dense_cosine_val,
                anchor_mask=source_ctx.source_clash_mask,
            )
        score = score * tone_multiplier

    if not (generic_genre_suppression or hook_tag_promotion):
        return score

    shared_genres = source_ctx.source_genres & candidate_genres
    shared_themes = source_ctx.source_themes & candidate_themes
    all_shared_tags = source_ctx.source_tags & candidate_tags
    shared_hook_tags = all_shared_tags & SPECIFIC_HOOK_AND_TONE_TAGS
    shared_narrative_tags = all_shared_tags - NON_NARRATIVE_TAGS

    if hook_tag_promotion and len(shared_hook_tags) >= MIN_SHARED_HOOK_TAGS_FOR_PROMOTION:
        score = score * HOOK_TAG_SALIENCE_MULTIPLIER

    if (
        dense_cosine < LOW_SEMANTIC_SOFT_FLOOR_COSINE_THRESHOLD
        and len(shared_themes) <= 1
        and not shared_narrative_tags
    ):
        score = score * LOW_SEMANTIC_SOFT_FLOOR_FACTOR

    shared_non_setting_themes = shared_themes - SETTING_BACKDROP_THEMES
    if (
        dense_cosine >= TIER1_CORROBORATION_SYNERGY_COSINE_THRESHOLD
        and (len(shared_non_setting_themes) >= 1 or len(shared_hook_tags) >= 1)
        and (not pure_tone_contradiction_guard or tone_multiplier >= 1.0)
    ):
        score = score * TIER1_CORROBORATION_SYNERGY_FACTOR

    if not generic_genre_suppression:
        return score

    is_sparse_anchor = (len(source_ctx.source_genres) <= 1 and not source_ctx.source_themes) or len(
        source_ctx.source_tags
    ) <= 1
    effective_narrative_threshold = (
        SPARSE_ANCHOR_NARRATIVE_THRESHOLD if is_sparse_anchor else GENERIC_BROAD_GENRE_NARRATIVE_THRESHOLD
    )
    effective_damping_factor = (
        SPARSE_ANCHOR_GENRE_DAMPING_FACTOR if is_sparse_anchor else GENERIC_BROAD_GENRE_DAMPING_FACTOR
    )

    if shared_genres:
        is_broad_only = shared_genres.issubset(GENERIC_BROAD_GENRES)
        is_lone_broad_candidate = len(candidate_genres) <= 1 and not candidate_themes
        if (
            is_broad_only
            and not shared_themes
            and not shared_narrative_tags
            and dense_cosine < effective_narrative_threshold
        ):
            lone_factor = 0.70 if is_lone_broad_candidate else 1.00
            score = score * (effective_damping_factor * lone_factor)
    elif not shared_themes and not shared_narrative_tags and dense_cosine < effective_narrative_threshold:
        score = score * (effective_damping_factor * 0.70)

    if (
        shared_themes
        and shared_themes.issubset(SETTING_BACKDROP_THEMES)
        and not shared_narrative_tags
        and dense_cosine < GENERIC_BROAD_THEME_NARRATIVE_THRESHOLD
    ):
        score = score * GENERIC_BROAD_THEME_DAMPING_FACTOR

    if (
        all_shared_tags
        and not shared_narrative_tags
        and not shared_themes
        and dense_cosine < PERSONA_ONLY_DAMPING_COSINE_THRESHOLD
    ):
        score = score * PERSONA_ONLY_DAMPING_FACTOR

    if entity_id != candidate.anime_id and rating_embedding_cosine is not None:
        entrypoint_themes = frozenset(themes_by_id.get(entity_id, ()))
        entrypoint_tags = frozenset(tags_by_id.get(entity_id, ()))
        entrypoint_narrative_tags = (source_ctx.source_tags & entrypoint_tags) - NON_NARRATIVE_TAGS
        entrypoint_shared_themes = source_ctx.source_themes & entrypoint_themes
        entrypoint_dense = rating_embedding_cosine.get(entity_id, 0.0)

        if not entrypoint_shared_themes and not entrypoint_narrative_tags:
            if entrypoint_dense < STORYLINE_ENTRYPOINT_COHERENCE_COSINE_THRESHOLD:
                score = score * STORYLINE_ENTRYPOINT_COHERENCE_DAMPING_FACTOR
        elif entrypoint_dense < 0.30:
            score = score * 0.90

    return score


def _apply_post_ranking(
    score: float,
    candidate: UnionCandidate,
    cand_row: int,
    content_score: float,
    dense_cosine: float,
    source_ctx: _SourceScoringContext,
    *,
    structure_policy: NarrativeStructurePolicy | None,
    narrative_profiles_by_id: Mapping[int, NarrativeProfile] | None,
    narrative_profiles_by_row: Sequence[NarrativeProfile | None] | None,
    synopses_by_id: Mapping[int, str | None] | None,
    synopses_by_row: Sequence[str | None] | None,
    tags_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    language_policy: LanguageCompatibilityPolicy | None,
    languages_by_id: Mapping[int, str] | None,
    languages_by_row: Sequence[str | None] | None,
) -> float:
    """Apply narrative structure, origin-language, candidate multiplier, and cascade floor."""
    candidate_id = candidate.anime_id
    if structure_policy is not None and source_ctx.source_struct is not None:
        candidate_struct = (
            narrative_profiles_by_row[cand_row] if narrative_profiles_by_row is not None and cand_row >= 0 else None
        )
        if candidate_struct is None and narrative_profiles_by_id is not None:
            candidate_struct = narrative_profiles_by_id.get(candidate_id)
        if candidate_struct is None:
            cand_synopsis = (
                synopses_by_row[cand_row]
                if synopses_by_row is not None and cand_row >= 0
                else (synopses_by_id.get(candidate_id) if synopses_by_id else None)
            )
            candidate_struct = resolve_narrative_profile(
                frozenset(tags_by_id.get(candidate_id, ())),
                cand_synopsis,
            )
        score *= structure_policy.multiplier(source_ctx.source_struct, candidate_struct)

    if language_policy is not None and languages_by_id:
        candidate_language = (
            languages_by_row[cand_row]
            if languages_by_row is not None and cand_row >= 0
            else languages_by_id.get(candidate_id)
        )
        score *= language_policy.multiplier(
            source_ctx.source_language, candidate_language, dense_similarity=dense_cosine
        )

    score *= candidate.score_multiplier
    if content_score > 0.0:
        score = max(score, content_score * 0.20)
    return score


def score_candidates(
    source_anime_id: int,
    candidates: Sequence[UnionCandidate],
    *,
    genres_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    themes_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    tags_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    demographics_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    ratings_by_id: Mapping[int, str] | None = None,
    rating_policy: RatingPolicy | None = None,
    recommendation_entity_ids: Mapping[int, int] | None = None,
    ranking_policy: RankingPolicy | None = None,
    properties: Sequence[ScoringProperty] | None = None,
    property_values: Mapping[str, PropertyValues] | None = None,
    synopsis_pairwise_dense: Mapping[int, float] | None = None,
    rating_embedding_cosine: Mapping[int, float] | None = None,
    embedding_gate_low: float = EMBEDDING_GATE_LOW,
    embedding_gate_high: float = EMBEDDING_GATE_HIGH,
    gated_synopsis_transfer: bool = False,
    evidence_qualified_multiplier: bool = False,
    pure_tone_contradiction_guard: bool = False,
    clash_masks_by_id: Mapping[int, ClashFlag] | None = None,
    generic_genre_suppression: bool = False,
    hook_tag_promotion: bool = False,
    structure_policy: NarrativeStructurePolicy | None = None,
    narrative_profiles_by_id: Mapping[int, NarrativeProfile] | None = None,
    language_policy: LanguageCompatibilityPolicy | None = None,
    languages_by_id: Mapping[int, str] | None = None,
    synopses_by_id: Mapping[int, str | None] | None = None,
    synopsis_scoring_paths: Sequence[str] = DEFAULT_SYNOPSIS_SCORING_PATHS,
    taxonomy_tokens_by_id: Mapping[int, frozenset[TaxonomyToken]] | None = None,
    thematic_leaf_tokens_by_id: Mapping[int, frozenset[TaxonomyToken]] | None = None,
    similarity_tags_by_id: Mapping[int, frozenset[str]] | None = None,
    parsed_genres_by_id: Mapping[int, frozenset[Genre]] | None = None,
    parsed_themes_by_id: Mapping[int, frozenset[Theme]] | None = None,
    tag_enums_by_id: Mapping[int, frozenset[Tag]] | None = None,
    tags_csr: tuple[Any, dict[str, int], np.ndarray] | None = None,
    themes_csr: tuple[Any, dict[str, int], np.ndarray] | None = None,
    genres_csr: tuple[Any, dict[str, int], np.ndarray] | None = None,
    index_by_id: Mapping[int, int] | None = None,
    ratings_by_row: Sequence[str | None] | None = None,
    demographics_by_row: Sequence[frozenset[str]] | None = None,
    parsed_genres_by_row: Sequence[frozenset[Genre]] | None = None,
    parsed_themes_by_row: Sequence[frozenset[Theme]] | None = None,
    tag_enums_by_row: Sequence[frozenset[Tag]] | None = None,
    taxonomy_tokens_by_row: Sequence[frozenset[TaxonomyToken]] | None = None,
    thematic_leaf_tokens_by_row: Sequence[frozenset[TaxonomyToken]] | None = None,
    narrative_profiles_by_row: Sequence[NarrativeProfile | None] | None = None,
    synopses_by_row: Sequence[str | None] | None = None,
    languages_by_row: Sequence[str | None] | None = None,
) -> tuple[ScoredCandidate, ...]:
    """Score qualified candidates using the active synopsis channels and metadata."""
    source_ctx = _prepare_source_scoring_context(
        source_anime_id,
        genres_by_id=genres_by_id,
        themes_by_id=themes_by_id,
        tags_by_id=tags_by_id,
        demographics_by_id=demographics_by_id,
        ratings_by_id=ratings_by_id,
        properties=properties,
        property_values=property_values,
        clash_masks_by_id=clash_masks_by_id,
        structure_policy=structure_policy,
        narrative_profiles_by_id=narrative_profiles_by_id,
        languages_by_id=languages_by_id,
        synopses_by_id=synopses_by_id,
        taxonomy_tokens_by_id=taxonomy_tokens_by_id,
        thematic_leaf_tokens_by_id=thematic_leaf_tokens_by_id,
        similarity_tags_by_id=similarity_tags_by_id,
        parsed_genres_by_id=parsed_genres_by_id,
        parsed_themes_by_id=parsed_themes_by_id,
        tag_enums_by_id=tag_enums_by_id,
    )
    base_sims = _compute_base_similarity(
        source_anime_id,
        candidates,
        source_ctx,
        property_values=property_values,
        synopsis_pairwise_dense=synopsis_pairwise_dense,
        rating_embedding_cosine=rating_embedding_cosine,
        embedding_gate_low=embedding_gate_low,
        embedding_gate_high=embedding_gate_high,
        gated_synopsis_transfer=gated_synopsis_transfer,
        pure_tone_contradiction_guard=pure_tone_contradiction_guard,
        clash_masks_by_id=clash_masks_by_id,
        synopsis_scoring_paths=synopsis_scoring_paths,
        similarity_tags_by_id=similarity_tags_by_id,
        tags_csr=tags_csr,
        themes_csr=themes_csr,
        genres_csr=genres_csr,
        index_by_id=index_by_id,
    )

    identity_map = recommendation_entity_ids or {}
    num_candidates = len(candidates)
    tags_sim_arr = base_sims.prop_sim_arrays.get('tags')
    themes_sim_arr = base_sims.prop_sim_arrays.get('themes')
    genres_sim_arr = base_sims.prop_sim_arrays.get('genres')
    best_by_entity: dict[int, tuple[float, int, set[str]]] = {}

    for candidate_index, candidate in enumerate(candidates):
        candidate_id = candidate.anime_id
        entity_id = identity_map.get(candidate_id, candidate_id)
        synopsis_score = float(base_sims.synopsis_scores[candidate_index])
        content_score = float(base_sims.content_scores[candidate_index])

        final_score, candidate_paths = _compute_cross_group_score(
            candidate,
            candidate_index,
            synopsis_score,
            content_score,
            evidence_qualified_multiplier=evidence_qualified_multiplier,
            tags_sim_arr=tags_sim_arr,
            themes_sim_arr=themes_sim_arr,
            genres_sim_arr=genres_sim_arr,
        )

        dense_cosine = (
            float(rating_embedding_cosine[candidate_id])
            if rating_embedding_cosine is not None and candidate_id in rating_embedding_cosine
            else float({item.path: item.score for item in candidate.evidence}.get('embedding', 0.50))
        )
        cand_row = (
            base_sims.cand_indices[candidate_index]
            if index_by_id is not None and len(base_sims.cand_indices) == num_candidates
            else -1
        )

        if rating_policy is not None and ratings_by_id is not None:
            candidate_rating = (
                ratings_by_row[cand_row]
                if ratings_by_row is not None and cand_row >= 0
                else ratings_by_id.get(candidate_id)
            )
            candidate_demos = (
                demographics_by_row[cand_row]
                if demographics_by_row is not None and cand_row >= 0
                else demographics_by_id.get(candidate_id, ())
            )
            shared_themes_raw = source_ctx.source_raw_themes & frozenset(themes_by_id.get(candidate_id, ()))
            if similarity_tags_by_id is not None:
                candidate_clean_tags = similarity_tags_by_id.get(candidate_id, frozenset())
            else:
                candidate_clean_tags = frozenset(similarity_tag_ids(tags_by_id.get(candidate_id, ())))
            shared_tags_raw = source_ctx.source_clean_tags & candidate_clean_tags
            dense_similarity = (
                rating_embedding_cosine.get(candidate_id) if rating_embedding_cosine is not None else None
            )
            final_score *= rating_policy.multiplier(
                source_ctx.source_rating,
                candidate_rating,
                parent_demographics=source_ctx.source_demos,
                candidate_demographics=candidate_demos,
                shared_themes=shared_themes_raw,
                shared_tags=shared_tags_raw,
                dense_cosine=dense_similarity,
            )

        candidate_genres, candidate_themes, candidate_tags, candidate_all_tokens = _resolve_candidate_taxonomy(
            candidate_id,
            cand_row,
            genres_by_id=genres_by_id,
            themes_by_id=themes_by_id,
            tags_by_id=tags_by_id,
            parsed_genres_by_id=parsed_genres_by_id,
            parsed_themes_by_id=parsed_themes_by_id,
            tag_enums_by_id=tag_enums_by_id,
            taxonomy_tokens_by_id=taxonomy_tokens_by_id,
            parsed_genres_by_row=parsed_genres_by_row,
            parsed_themes_by_row=parsed_themes_by_row,
            tag_enums_by_row=tag_enums_by_row,
            taxonomy_tokens_by_row=taxonomy_tokens_by_row,
        )

        final_score *= _compute_subsumption_multiplier(
            candidate_id,
            cand_row,
            source_ctx,
            candidate_all_tokens,
            thematic_leaf_tokens_by_id=thematic_leaf_tokens_by_id,
            thematic_leaf_tokens_by_row=thematic_leaf_tokens_by_row,
        )

        final_score = _apply_clash_and_tone_guards(
            final_score,
            candidate,
            candidate_index,
            entity_id,
            dense_cosine,
            source_ctx,
            candidate_genres,
            candidate_themes,
            candidate_tags,
            pure_tone_contradiction_guard=pure_tone_contradiction_guard,
            generic_genre_suppression=generic_genre_suppression,
            hook_tag_promotion=hook_tag_promotion,
            batch_tone_multipliers=base_sims.batch_tone_multipliers,
            clash_masks_by_id=clash_masks_by_id,
            rating_embedding_cosine=rating_embedding_cosine,
            themes_by_id=themes_by_id,
            tags_by_id=tags_by_id,
        )

        final_score = _apply_post_ranking(
            final_score,
            candidate,
            cand_row,
            content_score,
            dense_cosine,
            source_ctx,
            structure_policy=structure_policy,
            narrative_profiles_by_id=narrative_profiles_by_id,
            narrative_profiles_by_row=narrative_profiles_by_row,
            synopses_by_id=synopses_by_id,
            synopses_by_row=synopses_by_row,
            tags_by_id=tags_by_id,
            language_policy=language_policy,
            languages_by_id=languages_by_id,
            languages_by_row=languages_by_row,
        )

        existing = best_by_entity.get(entity_id)
        if existing is None or final_score > existing[0]:
            best_by_entity[entity_id] = (final_score, candidate.witness_member_id or candidate_id, candidate_paths)

    deduplicated = tuple(
        ScoredCandidate(entity_id, witness_id, score, tuple(sorted(paths)))
        for entity_id, (score, witness_id, paths) in best_by_entity.items()
    )
    return (ranking_policy or ScoreDescending()).rank(deduplicated)


def dice(source: frozenset[str] | set[str], candidate: Sequence[str] | frozenset[str] | set[str] | None) -> float:
    """Measure overlap relative to the combined source and candidate labels."""
    if not candidate:
        return 0.0
    candidate_set = candidate if isinstance(candidate, (frozenset, set)) else frozenset(candidate)
    denominator = len(source) + len(candidate_set)
    return 2.0 * len(source & candidate_set) / denominator if denominator else 0.0


def coverage(source: frozenset[str] | set[str], candidate: Sequence[str] | frozenset[str] | set[str] | None) -> float:
    """Measure how much of the source metadata the candidate preserves."""
    if not source or not candidate:
        return 0.0
    candidate_set = candidate if isinstance(candidate, (frozenset, set)) else frozenset(candidate)
    return len(source & candidate_set) / len(source)
