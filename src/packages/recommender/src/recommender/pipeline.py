"""Frozen production recommendation ordering over independent path evidence."""

from collections.abc import Mapping, Sequence
from types import FunctionType
from typing import Any

import msgspec
import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

from anime_catalogue import AnimeCatalogue
from anime_catalogue.demographics import (
    DEMOGRAPHIC_AFFINITY,
    ContentSeverityLevel,
    Demographic,
    get_content_severity_level,
    parse_demographic,
)
from anime_catalogue.subsumption import (
    ALL_ANCESTOR_TOKENS,
    NON_THEMATIC_ORTHOGONAL_TAGS,
    TaxonomyToken,
)
from anime_catalogue.tags import CORE_HOOK_TAGS, TONE_ATMOSPHERE_TAGS
from anime_catalogue.taxonomy import Genre, Theme, safe_parse_genre, safe_parse_theme
from anime_catalogue.tone_space import compute_tonal_coordinate
from config import derive_payload_identity, derive_stage_identity
from features.blocks import AvailabilityPolicy, FeatureBundle
from features.synopsis import LatentConfig, TfidfConfig
from features.tag_assignment import get_tag_assignment_registry, tag_assignment_registry_identity
from features.tags import (
    Tag,
    apply_tag_assignments,
    get_tag_salience,
    similarity_tag_ids,
    tag_registry_identity,
)
from graph import ManualRelationshipRow, RelationshipIndex
from normalization.metadata import MetadataState
from normalization.ratings import RatingClass, normalize_rating
from recommender.clash_rules import ClashFlag, extract_clash_flags, normalize_clash_tokens
from recommender.conflicts import is_hard_retrieval_contradiction
from recommender.contracts import RawRecommendation, RecommendationItem
from recommender.inputs import RecommenderInputs
from recommender.language_policy import OriginLanguage
from recommender.maturity_adjustment import is_weak_special_maturity_mismatch
from recommender.metrics import build_idf_csr
from recommender.paths import AffinityPathIndex, CategoricalPathIndex, SynopsisPathIndex, build_synopsis_path_index
from recommender.plan import RecommenderPlan
from recommender.post_ranking import (
    AnimePostRankingMetadata,
    build_mainline_runtime_index,
    compute_metadata_multiplier,
    compute_path_reliability_multiplier,
    extract_post_ranking_metadata,
)
from recommender.properties import SimilarityProperty
from recommender.qualification import (
    expand_story_line_entrypoints,
    nominate_story_line_entrypoints,
    qualify_candidates,
)
from recommender.ranking import ScoredCandidate, ScoreDescending
from recommender.rating_policy import RatingPolicy
from recommender.retrieval import RetrievalEngine
from recommender.scoring import (
    SIGMOID_GATE_CENTER,
    SIGMOID_GATE_SLOPE,
    SPECIFIC_HOOK_AND_TONE_TAGS,
    ScoringMetric,
    ScoringProperty,
    fuse_synopsis_vectors,
    make_idf_tversky,
    make_salience_weighted_tag_metric,
    score_candidates,
    to_recommendation_item,
)
from recommender.structure_policy import NarrativeProfile, resolve_narrative_profile
from recommender.surfacing import SurfacingPolicy
from recommender.union import (
    CATEGORICAL_EVIDENCE_PATHS,
    SEMANTIC_EVIDENCE_PATHS,
    UNION_POLICY_IDENTITY,
    RetrievalDiagnostics,
    RetrievalGroupBudget,
    build_union,
)
from recommender.weighted_v2 import WeightedV2Index

RECOMMENDER_POLICY_DESCRIPTOR = {
    'score_domain': 'finite-non-negative',
    'retrieval': 'deterministic-path-reduction',
    'ranking': 'score-descending-candidate-id-ascending',
}
DEFAULT_RECOMMENDATION_SOURCE_BATCH_SIZE = 100


def _rating_class(value: str) -> RatingClass:
    return normalize_rating(value)


DEMOGRAPHIC_COMPATIBILITY: dict[str, dict[str, float]] = {
    **{
        anchor.value: {cand.value: score for cand, score in targets.items()}
        for anchor, targets in DEMOGRAPHIC_AFFINITY.items()
    },
    **{
        anchor.value.casefold(): {cand.value.casefold(): score for cand, score in targets.items()}
        for anchor, targets in DEMOGRAPHIC_AFFINITY.items()
    },
}


class _CatalogueState(msgspec.Struct, frozen=True):
    """Prepared row-aligned catalogue facts consumed by scoring and retrieval."""

    frame: pl.DataFrame
    catalogue: AnimeCatalogue
    anime_ids: tuple[int, ...]
    index_by_id: Mapping[int, int]
    titles: Mapping[int, str]
    genres: tuple[tuple[Genre, ...], ...]
    themes: tuple[tuple[Theme, ...], ...]
    demographics: tuple[tuple[str, ...], ...]
    tags: tuple[tuple[str, ...], ...]
    ratings: tuple[str, ...]
    eligible_ids_by_profile: Mapping[tuple[str, tuple[str, ...]], frozenset[int]]
    ineligible_ids_by_profile: Mapping[tuple[str, tuple[str, ...]], frozenset[int]]
    ratings_by_id: Mapping[int, str]
    genres_by_id: Mapping[int, frozenset[Genre]]
    themes_by_id: Mapping[int, frozenset[Theme]]
    demographics_by_id: Mapping[int, frozenset[str]]
    tags_by_id: Mapping[int, frozenset[str]]
    idfs_by_property: Mapping[str, Mapping[str, float]]
    anime_type_by_id: Mapping[int, str | None]
    episodes_by_id: Mapping[int, int | None]
    source_by_id: Mapping[int, str | None]
    score_by_id: Mapping[int, float | None]
    origin_language_by_id: Mapping[int, str]
    metadata_states_by_id: Mapping[int, Mapping[str, MetadataState]]
    post_ranking_metadata_by_id: Mapping[int, AnimePostRankingMetadata]
    taxonomy_tokens_by_id: Mapping[int, frozenset[TaxonomyToken]]
    thematic_leaf_tokens_by_id: Mapping[int, frozenset[TaxonomyToken]]
    similarity_tags_by_id: Mapping[int, frozenset[str]]
    parsed_genres_by_id: Mapping[int, frozenset[Genre]]
    parsed_themes_by_id: Mapping[int, frozenset[Theme]]
    tag_enums_by_id: Mapping[int, frozenset[Tag]]
    clash_masks_by_id: Mapping[int, ClashFlag]
    tonal_coordinate_by_id: Mapping[int, float]
    content_severity_by_id: Mapping[int, ContentSeverityLevel]
    narrative_profiles_by_id: Mapping[int, NarrativeProfile]
    synopses_by_id: Mapping[int, str | None]
    clash_masks_arr: np.ndarray | None = None
    tags_csr: tuple[Any, dict[str, int], np.ndarray] | None = None
    themes_csr: tuple[Any, dict[str, int], np.ndarray] | None = None
    genres_csr: tuple[Any, dict[str, int], np.ndarray] | None = None
    rating_classes_arr: np.ndarray | None = None
    origin_langs_arr: np.ndarray | None = None


class _RetrievalState(msgspec.Struct, frozen=True):
    """Prepared path indexes and resolved path configuration."""

    engine: RetrievalEngine
    similarity_properties: tuple[SimilarityProperty, ...]


def _prepare_catalogue(
    frame: pl.DataFrame,
    bundle: FeatureBundle,
    rating_policy: RatingPolicy,
    *,
    manual_relationships: Sequence[ManualRelationshipRow] = (),
) -> _CatalogueState:
    """Validate and prepare all row-aligned catalogue facts."""
    ordered_frame = frame.sort('mal_id')
    catalogue = AnimeCatalogue.from_frame(ordered_frame)
    catalogue.validate_aligned_ids(bundle.anime_ids.tolist(), source_name='feature bundle')
    anime_ids = catalogue.anime_ids
    genres = catalogue.genres
    themes = catalogue.themes
    demographics = catalogue.demographics
    if 'manual_tags' in ordered_frame.columns:
        tags = tuple(tuple(tag_list or ()) for tag_list in ordered_frame.get_column('manual_tags').to_list())
        tag_map = dict(zip(anime_ids, tags, strict=True))
    else:
        tag_map = apply_tag_assignments(anime_ids, get_tag_assignment_registry().assignments)
        tags = tuple(tuple(tag_map.get(anime_id, ())) for anime_id in anime_ids)
    genres_by_id, themes_by_id, demographics_by_id, tags_by_id = _build_feature_maps(
        anime_ids,
        genres,
        themes,
        demographics,
        tags,
    )
    genre_idf = _compute_corpus_idf(genres, len(anime_ids))
    theme_idf = _compute_corpus_idf(themes, len(anime_ids))
    tag_idf = _compute_corpus_idf(tags, len(anime_ids))
    idfs_by_property = {
        'genres': genre_idf,
        'themes': theme_idf,
        'tags': tag_idf,
    }
    eligible_ids_by_profile, ineligible_ids_by_profile = _build_eligibility_index(
        anime_ids,
        catalogue.ratings,
        demographics,
        rating_policy,
    )

    taxonomy_tokens_by_id: dict[int, frozenset[TaxonomyToken]] = {}
    thematic_leaf_tokens_by_id: dict[int, frozenset[TaxonomyToken]] = {}
    similarity_tags_by_id: dict[int, frozenset[str]] = {}
    parsed_genres_by_id: dict[int, frozenset[Genre]] = {}
    parsed_themes_by_id: dict[int, frozenset[Theme]] = {}
    tag_enums_by_id: dict[int, frozenset[Tag]] = {}
    clash_masks_by_id: dict[int, ClashFlag] = {}
    tonal_coordinate_by_id: dict[int, float] = {}
    content_severity_by_id: dict[int, ContentSeverityLevel] = {}

    ratings_by_id = dict(zip(anime_ids, catalogue.ratings, strict=True))
    raw_synopses = (
        ordered_frame.get_column('synopsis').to_list()
        if 'synopsis' in ordered_frame.columns
        else catalogue.synopsis_features
    )
    synopses_by_id = {
        anime_id: (
            str(raw_syn) if raw_syn is not None and str(raw_syn).strip() else (catalogue.synopsis_features[idx] or None)
        )
        for idx, (anime_id, raw_syn) in enumerate(zip(anime_ids, raw_synopses, strict=True))
    }
    narrative_profiles_by_id = {
        anime_id: resolve_narrative_profile(
            tags_by_id.get(anime_id, frozenset()),
            synopses_by_id.get(anime_id),
        )
        for anime_id in anime_ids
    }
    for anime_id in anime_ids:
        anime_genres = frozenset(
            genre for label in genres_by_id.get(anime_id, ()) if (genre := safe_parse_genre(label))
        )
        anime_themes = frozenset(
            theme for label in themes_by_id.get(anime_id, ()) if (theme := safe_parse_theme(label))
        )
        anime_tags = frozenset(
            Tag(tag) for tag in tags_by_id.get(anime_id, ()) if isinstance(tag, Tag) or tag in Tag._value2member_map_
        )
        all_tokens = frozenset(anime_genres | anime_themes | anime_tags)
        taxonomy_tokens_by_id[anime_id] = all_tokens
        thematic_leaf_tokens_by_id[anime_id] = (all_tokens - NON_THEMATIC_ORTHOGONAL_TAGS) - ALL_ANCESTOR_TOKENS
        similarity_tags_by_id[anime_id] = frozenset(similarity_tag_ids(tags_by_id.get(anime_id, ())))
        parsed_genres_by_id[anime_id] = anime_genres
        parsed_themes_by_id[anime_id] = anime_themes
        tag_enums_by_id[anime_id] = anime_tags
        clash_masks_by_id[anime_id] = extract_clash_flags(
            normalize_clash_tokens(
                genres_by_id.get(anime_id, frozenset())
                | themes_by_id.get(anime_id, frozenset())
                | tags_by_id.get(anime_id, frozenset())
            )
        )
        tonal_coordinate_by_id[anime_id] = compute_tonal_coordinate(taxonomy_tokens_by_id[anime_id])
        content_severity_by_id[anime_id] = get_content_severity_level(ratings_by_id.get(anime_id, ''))

    rows_by_id = {row['mal_id']: row for row in ordered_frame.iter_rows(named=True)}
    sim_tag_lists = tuple(similarity_tag_ids(t) for t in tags)
    tag_idf = idfs_by_property.get('tags')
    tag_salience_weights = {
        tag: get_tag_salience(tag) * (tag_idf.get(tag, 1.0) if tag_idf is not None else 1.0)
        for tag_list in sim_tag_lists
        for tag in tag_list
    }
    return _CatalogueState(
        frame=ordered_frame,
        catalogue=catalogue,
        anime_ids=anime_ids,
        index_by_id=catalogue.index_by_id,
        titles=dict(zip(anime_ids, catalogue.titles, strict=True)),
        genres=genres,
        themes=themes,
        demographics=demographics,
        tags=tags,
        ratings=catalogue.ratings,
        eligible_ids_by_profile=eligible_ids_by_profile,
        ineligible_ids_by_profile=ineligible_ids_by_profile,
        ratings_by_id=dict(zip(anime_ids, catalogue.ratings, strict=True)),
        genres_by_id=genres_by_id,
        themes_by_id=themes_by_id,
        demographics_by_id=demographics_by_id,
        tags_by_id=tags_by_id,
        idfs_by_property=idfs_by_property,
        anime_type_by_id={anime_id: row.get('anime_type') for anime_id, row in rows_by_id.items()},
        episodes_by_id={anime_id: row.get('episodes') for anime_id, row in rows_by_id.items()},
        source_by_id={anime_id: row.get('source') for anime_id, row in rows_by_id.items()},
        score_by_id={anime_id: row.get('score') for anime_id, row in rows_by_id.items()},
        origin_language_by_id={
            anime_id: str(rows_by_id[anime_id].get('origin_language') or OriginLanguage.JAPANESE)
            for anime_id in anime_ids
        },
        metadata_states_by_id={
            anime_id: {
                name: (
                    MetadataState.OBSERVED
                    if name == 'tags' and tag_map.get(anime_id)
                    else _metadata_state(row.get(f'{name}_state'))
                )
                for name in ('synopsis', 'genres', 'themes', 'tags', 'type', 'demographics', 'rating')
            }
            for anime_id, row in rows_by_id.items()
        },
        post_ranking_metadata_by_id=_prepare_post_ranking_metadata(ordered_frame, manual_relationships),
        taxonomy_tokens_by_id=taxonomy_tokens_by_id,
        thematic_leaf_tokens_by_id=thematic_leaf_tokens_by_id,
        similarity_tags_by_id=similarity_tags_by_id,
        parsed_genres_by_id=parsed_genres_by_id,
        parsed_themes_by_id=parsed_themes_by_id,
        tag_enums_by_id=tag_enums_by_id,
        clash_masks_by_id=clash_masks_by_id,
        clash_masks_arr=np.array([int(clash_masks_by_id.get(aid, 0)) for aid in anime_ids], dtype=np.int64),
        tags_csr=build_idf_csr(sim_tag_lists, idf_map=tag_salience_weights),
        themes_csr=build_idf_csr(themes, idf_map=idfs_by_property.get('themes')),
        genres_csr=build_idf_csr(genres, idf_map=idfs_by_property.get('genres')),
        rating_classes_arr=np.array(
            [int(normalize_rating(str(rows_by_id[aid].get('rating') or '')).value != '') for aid in anime_ids],
            dtype=np.int8,
        ),
        origin_langs_arr=np.array(
            [hash(str(rows_by_id[aid].get('origin_language') or 'Japanese')) & 0x7F for aid in anime_ids],
            dtype=np.int8,
        ),
        tonal_coordinate_by_id=tonal_coordinate_by_id,
        content_severity_by_id=content_severity_by_id,
        narrative_profiles_by_id=narrative_profiles_by_id,
        synopses_by_id=synopses_by_id,
    )


def _prepare_post_ranking_metadata(
    frame: pl.DataFrame,
    manual_relationships: Sequence[ManualRelationshipRow] = (),
) -> Mapping[int, AnimePostRankingMetadata]:
    relations_frame = (
        pl.DataFrame(
            {
                'source_id': [row.source_id for row in manual_relationships],
                'target_id': [row.target_id for row in manual_relationships],
                'relation_type': [row.relation_type for row in manual_relationships],
                'same_story_intent': [row.same_story_intent.value for row in manual_relationships],
            }
        )
        if manual_relationships
        else None
    )
    runtimes, episodes = build_mainline_runtime_index(frame, relations_frame)
    return extract_post_ranking_metadata(frame, runtimes, storyline_episodes_by_id=episodes)


def _compute_corpus_idf(sequences: Sequence[Sequence[str]], total_docs: int) -> dict[str, float]:
    """Compute smoothed BM25 IDF weights over corpus categorical sequences."""
    df_counts: dict[str, int] = {}
    for items in sequences:
        for term in set(items):
            df_counts[term] = df_counts.get(term, 0) + 1
    return {term: max(0.0, float(np.log((total_docs - df + 0.5) / (df + 0.5)) + 1.0)) for term, df in df_counts.items()}


def _embedding_matrix(bundle: FeatureBundle) -> NDArray[np.floating] | None:
    """Return the aligned embedding block when preparation generated one."""
    block = bundle.block('synopsis-embedding')
    return None if block is None else np.asarray(block.values, dtype=np.float32)


def _metric_identity(metric: ScoringMetric) -> str:
    if isinstance(metric, FunctionType):
        return f'{metric.__module__}.{metric.__qualname__}'
    metric_type = type(metric)
    return f'{metric_type.__module__}.{metric_type.__qualname__}'


def _metadata_state(value: object) -> MetadataState:
    if isinstance(value, str):
        try:
            return MetadataState(value)
        except ValueError:
            pass
    return MetadataState.UNKNOWN


def _build_eligibility_index(
    anime_ids: Sequence[int],
    ratings: Sequence[str],
    demographics: Sequence[Sequence[str]],
    rating_policy: RatingPolicy,
) -> tuple[
    dict[tuple[str, tuple[str, ...]], frozenset[int]],
    dict[tuple[str, tuple[str, ...]], frozenset[int]],
]:
    """Precompute eligible candidates for each distinct source rating and demographic profile."""
    all_anime_ids = frozenset(anime_ids)
    source_profiles = {
        (parent_rating, _normalized_demographics(parent_demographics))
        for parent_rating, parent_demographics in zip(ratings, demographics, strict=True)
    }
    eligible = {
        (parent_rating, parent_demographics): frozenset(
            anime_id
            for anime_id, candidate_rating in zip(anime_ids, ratings, strict=True)
            if rating_policy.evaluate(
                parent_rating,
                candidate_rating,
                parent_demographics=parent_demographics,
            ).allowed
        )
        for parent_rating, parent_demographics in source_profiles
    }
    ineligible = {profile: all_anime_ids - eligible_ids for profile, eligible_ids in eligible.items()}
    return eligible, ineligible


def _normalized_demographics(demographics: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({demographic.strip().casefold() for demographic in demographics if demographic.strip()}))


def _build_feature_maps(
    anime_ids: Sequence[int],
    genres: Sequence[Sequence[Genre]],
    themes: Sequence[Sequence[Theme]],
    demographics: Sequence[Sequence[str]],
    tags: Sequence[Sequence[str]],
) -> tuple[
    dict[int, frozenset[Genre]],
    dict[int, frozenset[Theme]],
    dict[int, frozenset[str]],
    dict[int, frozenset[str]],
]:
    """Build ID-keyed feature maps used by the scoring stage."""
    return (
        dict(zip(anime_ids, map(frozenset, genres), strict=True)),
        dict(zip(anime_ids, map(frozenset, themes), strict=True)),
        dict(zip(anime_ids, map(frozenset, demographics), strict=True)),
        dict(zip(anime_ids, map(frozenset, tags), strict=True)),
    )


def _build_synopsis_index(
    anime_ids: Sequence[int],
    synopsis_features: Sequence[str | None],
    bundle: FeatureBundle,
    active_paths: Sequence[str],
    *,
    include_bm25: bool,
    include_lsa: bool,
    include_embedding: bool,
    embedding_matrix: NDArray[np.floating] | None,
    tfidf_config: TfidfConfig | None,
    latent_config: LatentConfig | None,
) -> tuple[SynopsisPathIndex, tuple[str, ...]]:
    """Fit the enabled synopsis indexes and return their active path names."""
    index = build_synopsis_path_index(anime_ids, synopsis_features)
    if include_bm25:
        block = bundle.block('synopsis-bm25')
        if block is not None and isinstance(block.values, csr_matrix):
            index.fit_bm25_matrix(block.values)
        else:
            index.fit_bm25()
    if 'char_3_5g_tfidf' in active_paths:
        index.fit_char_tfidf()
    if include_lsa:
        block = bundle.block('synopsis-lsa')
        if block is not None and not isinstance(block.values, csr_matrix):
            index.fit_lsa_matrix(block.values)
        else:
            index.fit_lsa(tfidf_config, latent_config)
    if embedding_matrix is None and include_embedding:
        embedding_matrix = _embedding_matrix(bundle)
    if embedding_matrix is not None and include_embedding:
        index.fit_embedding_matrix(np.asarray(embedding_matrix, dtype=np.float32))
    enabled_paths = tuple(
        path
        for path, enabled in (
            ('bm25', include_bm25 and 'bm25' in active_paths),
            ('char_3_5g_tfidf', 'char_3_5g_tfidf' in active_paths),
            ('lsa', include_lsa and 'lsa' in active_paths),
            ('embedding', embedding_matrix is not None and 'embedding' in active_paths),
        )
        if enabled
    )
    return index, enabled_paths


def _build_structured_indexes(
    anime_ids: Sequence[int],
    frame: pl.DataFrame,
    genres: Sequence[Sequence[str]],
    themes: Sequence[Sequence[str]],
    demographics: Sequence[Sequence[str]],
    tags: Sequence[Sequence[str]],
    active_paths: Sequence[str],
    *,
    idfs_by_property: Mapping[str, Mapping[str, float]] | None = None,
) -> tuple[dict[str, CategoricalPathIndex], dict[str, AffinityPathIndex]]:
    """Build categorical and affinity indexes for the enabled structured paths with Tversky and salience/IDF."""
    idfs = idfs_by_property or {}
    categorical: dict[str, CategoricalPathIndex] = {}
    if 'genres' in active_paths:
        categorical['genres'] = CategoricalPathIndex(
            anime_ids,
            genres,
            alpha=0.60,
            beta=0.40,
            weights=idfs.get('genres'),
        )
    if 'themes' in active_paths:
        categorical['themes'] = CategoricalPathIndex(
            anime_ids,
            themes,
            alpha=0.75,
            beta=0.25,
            weights=idfs.get('themes'),
        )
    if 'tags' in active_paths:
        tags = tuple(similarity_tag_ids(row) for row in tags)
        all_unique_tags = {tag for row in tags for tag in row}
        tag_salience_weights = {tag: get_tag_salience(tag) for tag in all_unique_tags}
        categorical['tags'] = CategoricalPathIndex(
            anime_ids,
            tags,
            alpha=0.80,
            beta=0.20,
            weights=tag_salience_weights,
        )
    affinity: dict[str, AffinityPathIndex] = {}
    if 'demographic' in active_paths:
        affinity['demographic'] = AffinityPathIndex(anime_ids, demographics, DEMOGRAPHIC_COMPATIBILITY)
    if 'studio' in active_paths:
        studio_values = tuple(tuple(str(studio_id) for studio_id in values) for values in frame['studio_ids'].to_list())
        affinity['studio'] = AffinityPathIndex(anime_ids, studio_values)
    return categorical, affinity


def _build_retrieval_state(
    state: _CatalogueState,
    bundle: FeatureBundle,
    active_paths: Sequence[str],
    *,
    include_bm25: bool,
    include_lsa: bool,
    include_embedding: bool,
    synopsis_embedding_matrix: NDArray[np.floating] | None,
    synopsis_tfidf_config: TfidfConfig | None,
    synopsis_latent_config: LatentConfig | None,
    retrieval_limit: int,
    retrieval_batch_size: int,
    retrieval_group_budget: RetrievalGroupBudget | None,
    relationship_index: RelationshipIndex | None = None,
    similarity_properties: Sequence[SimilarityProperty] | None,
    availability_policy: AvailabilityPolicy | None,
) -> _RetrievalState:
    """Build weighted, synopsis, categorical, and affinity retrieval indexes."""
    weighted_v2 = (
        WeightedV2Index(bundle, properties=similarity_properties, availability_policy=availability_policy)
        if 'weighted-v2' in active_paths
        else None
    )
    synopsis, enabled_synopsis_paths = _build_synopsis_index(
        state.anime_ids,
        state.catalogue.synopsis_features,
        bundle,
        active_paths,
        include_bm25=include_bm25,
        include_lsa=include_lsa,
        include_embedding=include_embedding,
        embedding_matrix=synopsis_embedding_matrix,
        tfidf_config=synopsis_tfidf_config,
        latent_config=synopsis_latent_config,
    )
    resolved_paths = tuple(
        path
        for path in active_paths
        if path not in {'bm25', 'char_3_5g_tfidf', 'lsa', 'embedding'} or path in enabled_synopsis_paths
    )
    categorical, affinity = _build_structured_indexes(
        state.anime_ids,
        state.frame,
        state.genres,
        state.themes,
        state.demographics,
        state.tags,
        active_paths,
        idfs_by_property=state.idfs_by_property,
    )
    return _RetrievalState(
        engine=RetrievalEngine(
            synopsis,
            weighted_v2,
            categorical,
            affinity,
            retrieval_limit=retrieval_limit,
            retrieval_batch_size=retrieval_batch_size,
            group_budget=retrieval_group_budget,
            enabled_paths=resolved_paths,
            relationship_index=relationship_index,
        ),
        similarity_properties=() if weighted_v2 is None else weighted_v2.properties,
    )


class Recommender:
    """Production recommender with shared retrieval indexes and frozen v2 scoring."""

    def __init__(
        self,
        inputs: RecommenderInputs,
        plan: RecommenderPlan,
    ) -> None:
        active_retrieval_paths = plan.retrieval_paths
        self._rating_policy = plan.rating_policy
        state = _prepare_catalogue(
            inputs.frame,
            inputs.bundle,
            self._rating_policy,
            manual_relationships=inputs.manual_relationships,
        )
        self._catalogue_state = state
        self._hook_tags_by_id = {aid: tags & SPECIFIC_HOOK_AND_TONE_TAGS for aid, tags in state.tags_by_id.items()}
        self._relationship_index = inputs.relationship_index
        self._relationship_policy_identity = plan.relationship_policy_identity
        self._ranking_policy = plan.ranking_policy
        self._scoring_paths = frozenset(plan.scoring_paths)
        self._scoring_properties = tuple(
            ScoringProperty(
                name=p.name,
                weight=p.weight,
                metric=(
                    make_salience_weighted_tag_metric(idf_map=state.idfs_by_property.get(p.name))
                    if p.metric_identity
                    in (
                        'salience-weighted-tversky-82-v1',
                        'salience-weighted-tversky-82-content-v2',
                        'idf-tversky-82-v1',
                    )
                    else make_idf_tversky(alpha=0.6, beta=0.4, idf_map=state.idfs_by_property.get(p.name))
                    if p.metric_identity == 'idf-tversky-64-v1'
                    else make_idf_tversky(alpha=0.75, beta=0.25, idf_map=state.idfs_by_property.get(p.name))
                    if p.metric_identity == 'idf-tversky-7525-v1'
                    else make_idf_tversky(alpha=0.7, beta=0.3, idf_map=state.idfs_by_property.get(p.name))
                    if p.metric_identity == 'idf-tversky-73-v1'
                    else p.metric
                ),
                metric_identity=p.metric_identity,
            )
            for p in plan.scoring_properties
        )
        self._scoring_property_values = dict(inputs.scoring_property_values or {})
        self._availability_policy_identity = plan.availability_policy_identity
        self._feature_configuration_identity = inputs.feature_configuration_identity
        self._weak_maturity_demotion = plan.weak_maturity_demotion
        self._weak_maturity_demotion_penalty = plan.weak_maturity_demotion_penalty
        self._embedding_gate_low = plan.embedding_gate_low
        self._embedding_gate_high = plan.embedding_gate_high
        self._gated_synopsis_transfer = plan.gated_synopsis_transfer
        self._evidence_qualified_multiplier = plan.evidence_qualified_multiplier
        self._pure_tone_contradiction_guard = plan.pure_tone_contradiction_guard
        self._generic_genre_suppression = plan.generic_genre_suppression
        self._hook_tag_promotion = plan.hook_tag_promotion
        self._structure_policy = plan.structure_policy
        self._language_policy = plan.language_policy
        self._metadata_post_ranking = plan.metadata_post_ranking
        self._resolved_plan_identity = plan.identity
        self._synopsis_tfidf_config = inputs.synopsis_tfidf_config
        self._synopsis_latent_config = inputs.synopsis_latent_config
        self._surfacing_policy = inputs.surfacing_policy or SurfacingPolicy()
        retrieval_state = _build_retrieval_state(
            state,
            inputs.bundle,
            active_retrieval_paths,
            include_bm25=plan.has_path('bm25') or 'bm25' in self._scoring_paths,
            include_lsa=plan.has_path('lsa') or 'lsa' in self._scoring_paths,
            include_embedding=plan.has_path('embedding') or 'embedding' in self._scoring_paths,
            synopsis_embedding_matrix=inputs.synopsis_embedding_matrix,
            synopsis_tfidf_config=inputs.synopsis_tfidf_config,
            synopsis_latent_config=inputs.synopsis_latent_config,
            retrieval_limit=plan.retrieval_limit,
            retrieval_batch_size=plan.retrieval_batch_size,
            retrieval_group_budget=plan.retrieval_group_budget,
            relationship_index=inputs.relationship_index,
            similarity_properties=plan.similarity_properties,
            availability_policy=plan.availability_policy,
        )
        self._similarity_properties = retrieval_state.similarity_properties
        self._retrieval = retrieval_state.engine
        self._pairwise_dense_cosine_cache: dict[tuple[int, int], float] = {}
        self._source_dense_cosine_rows: dict[int, np.ndarray] = {}
        self._post_ranking_meta_by_row = tuple(state.post_ranking_metadata_by_id.get(aid) for aid in state.anime_ids)
        self._themes_by_row = tuple(state.themes_by_id.get(aid, frozenset()) for aid in state.anime_ids)
        self._genres_by_row = tuple(state.genres_by_id.get(aid, frozenset()) for aid in state.anime_ids)
        self._tags_by_row = tuple(state.tags_by_id.get(aid, frozenset()) for aid in state.anime_ids)
        self._hook_tags_by_row = tuple(self._hook_tags_by_id.get(aid, frozenset()) for aid in state.anime_ids)
        self._tonal_coordinate_by_row = tuple(state.tonal_coordinate_by_id.get(aid, 0.0) for aid in state.anime_ids)
        self._content_severity_by_row = tuple(
            state.content_severity_by_id.get(aid, ContentSeverityLevel.LEVEL_0_UNIVERSAL) for aid in state.anime_ids
        )
        self._ratings_by_row = tuple(state.ratings_by_id.get(aid) for aid in state.anime_ids)
        self._demographics_by_row = tuple(state.demographics_by_id.get(aid, frozenset()) for aid in state.anime_ids)
        self._parsed_genres_by_row = tuple(state.parsed_genres_by_id.get(aid, frozenset()) for aid in state.anime_ids)
        self._parsed_themes_by_row = tuple(state.parsed_themes_by_id.get(aid, frozenset()) for aid in state.anime_ids)
        self._tag_enums_by_row = tuple(state.tag_enums_by_id.get(aid, frozenset()) for aid in state.anime_ids)
        self._taxonomy_tokens_by_row = tuple(
            state.taxonomy_tokens_by_id.get(aid, frozenset()) for aid in state.anime_ids
        )
        self._thematic_leaf_tokens_by_row = tuple(
            state.thematic_leaf_tokens_by_id.get(aid, frozenset()) for aid in state.anime_ids
        )
        self._narrative_profiles_by_row = tuple(state.narrative_profiles_by_id.get(aid) for aid in state.anime_ids)
        self._synopses_by_row = tuple(state.synopses_by_id.get(aid) for aid in state.anime_ids)
        self._languages_by_row = tuple(state.origin_language_by_id.get(aid) for aid in state.anime_ids)

    @property
    def relationship_fingerprint(self) -> str:
        """Return the structural graph identity used by this recommender."""
        if self._relationship_index is None:
            return 'none'
        return self._relationship_index.fingerprint()

    @property
    def retrieval_identity(self) -> str:
        """Return a deterministic identity for retrieval and group reduction."""
        return self._retrieval.identity

    @property
    def union_identity(self) -> str:
        """Return the active candidate-merging policy identity."""
        return UNION_POLICY_IDENTITY

    @property
    def ranking_identity(self) -> str:
        """Return the active ordering policy identity."""
        return self._ranking_policy.identity

    @property
    def policy_identity(self) -> str:
        """Return one deterministic identity for all recommendation policy choices."""
        return derive_stage_identity(
            'recommender',
            contract_identity='recommendation-policy-v1',
            source_identity='none',
            configuration_identity=derive_payload_identity(self._policy_configuration()),
            policy_identity=derive_payload_identity(RECOMMENDER_POLICY_DESCRIPTOR),
            producer_identity='recommender.pipeline',
        )

    def _policy_configuration(self) -> dict[str, object]:
        """Build the semantic configuration payload used by policy identity."""
        return {
            'recommender_policy': RECOMMENDER_POLICY_DESCRIPTOR,
            'relationship_graph': self.relationship_fingerprint,
            'relationship_policy': self._relationship_policy_identity,
            'catalogue': derive_payload_identity(tuple(self._catalogue_state.anime_ids)),
            'feature_configuration': self._feature_configuration_identity,
            'synopsis_configuration': {
                'tfidf': self._synopsis_tfidf_config,
                'latent': self._synopsis_latent_config,
            },
            'rating': self._rating_policy.identity,
            'scoring_paths': tuple(sorted(self._scoring_paths)),
            'resolved_plan': self._resolved_plan_identity,
            'weak_maturity_demotion': self._weak_maturity_demotion,
            'weak_maturity_demotion_penalty': self._weak_maturity_demotion_penalty,
            'metadata_post_ranking': self._metadata_post_ranking,
            'retrieval': self.retrieval_identity,
            'union': self.union_identity,
            'ranking': self.ranking_identity,
            'surfacing': {
                'name': self._surfacing_policy.name,
                'minimum_score': self._surfacing_policy.minimum_score,
                'maximum_results': self._surfacing_policy.maximum_results,
            },
            'similarity_properties': [
                {
                    'name': property_spec.name,
                    'weight': property_spec.weight,
                    'metric': property_spec.metric,
                    'content': property_spec.contributes_to_content,
                }
                for property_spec in self._similarity_properties
            ],
            'scoring_properties': [
                {
                    'name': property_spec.name,
                    'weight': property_spec.weight,
                    'metric': property_spec.metric_identity or _metric_identity(property_spec.metric),
                }
                for property_spec in self._scoring_properties
            ],
            'scoring_property_values': derive_payload_identity(self._scoring_property_values),
            'scoring_version': 'scoring-v3-3',
            'availability_policy': self._availability_policy_identity,
            'tag_vocabulary_identity': tag_registry_identity(),
            'tag_assignment_identity': tag_assignment_registry_identity(),
        }

    @property
    def last_retrieval_diagnostics(self) -> RetrievalDiagnostics:
        """Return aggregate counts from the most recent raw recommendation batch."""
        return self._retrieval.last_diagnostics

    def recommend(
        self,
        source_anime_id: int,
        *,
        limit: int,
    ) -> tuple[RecommendationItem, ...]:
        raw_items = self.raw_recommend_many((source_anime_id,))[source_anime_id]
        return self._present_raw_items(raw_items, limit=limit)

    def recommend_many(
        self,
        source_anime_ids: Sequence[int],
        *,
        limit: int,
    ) -> Mapping[int, tuple[RecommendationItem, ...]]:
        """Return independent per-source results while retaining shared indexes."""
        raw_results = self.raw_recommend_many(source_anime_ids)
        return {
            source_id: self._present_raw_items(raw_results[source_id], limit=limit) for source_id in source_anime_ids
        }

    def recommend_ids_many(
        self,
        source_anime_ids: Sequence[int],
        *,
        limit: int,
        source_batch_size: int = DEFAULT_RECOMMENDATION_SOURCE_BATCH_SIZE,
    ) -> Mapping[int, tuple[int, ...]]:
        """Return production recommendation IDs in bounded source batches."""
        if source_batch_size < 1:
            raise ValueError('source_batch_size must be positive')

        recommendations: dict[int, tuple[int, ...]] = {}
        for start in range(0, len(source_anime_ids), source_batch_size):
            end = min(start + source_batch_size, len(source_anime_ids))
            batch_ids = source_anime_ids[start:end]
            recommendations.update(self._recommend_ids_batch(batch_ids, limit))
            if end < len(source_anime_ids):
                self._pairwise_dense_cosine_cache.clear()
                if hasattr(self, '_source_dense_cosine_rows'):
                    self._source_dense_cosine_rows.clear()
        return recommendations

    def _recommend_ids_batch(
        self,
        source_anime_ids: Sequence[int],
        limit: int,
    ) -> Mapping[int, tuple[int, ...]]:
        raw_results = self.raw_recommend_many(source_anime_ids)
        franchise_by_id = self._relationship_index.franchise_by_id if self._relationship_index is not None else None
        same_story_exclusions = (
            self._relationship_index.exclusions_by_id if self._relationship_index is not None else None
        )
        story_line_by_id = (
            self._relationship_index.story_line_entrypoint_by_id if self._relationship_index is not None else None
        )
        return {
            source_id: tuple(
                item.anime_id
                for item in self._surfacing_policy.surface(
                    raw_results[source_id],
                    franchise_by_id=franchise_by_id,
                    same_story_exclusions_by_id=same_story_exclusions,
                    story_line_by_id=story_line_by_id,
                    source_anime_id=source_id,
                )[:limit]
            )
            for source_id in source_anime_ids
        }

    def _present_raw_items(
        self,
        raw_items: Sequence[RawRecommendation],
        *,
        limit: int,
        source_anime_id: int | None = None,
    ) -> tuple[RecommendationItem, ...]:
        franchise_by_id = self._relationship_index.franchise_by_id if self._relationship_index is not None else None
        same_story_exclusions = (
            self._relationship_index.exclusions_by_id if self._relationship_index is not None else None
        )
        story_line_by_id = (
            self._relationship_index.story_line_entrypoint_by_id if self._relationship_index is not None else None
        )
        surfaced_items = self._surfacing_policy.surface(
            raw_items,
            franchise_by_id=franchise_by_id,
            same_story_exclusions_by_id=same_story_exclusions,
            story_line_by_id=story_line_by_id,
            source_anime_id=source_anime_id,
        )[:limit]
        return tuple(to_recommendation_item(item.anime_id, item.score) for item in surfaced_items)

    def raw_similarity_many(
        self,
        source_anime_ids: Sequence[int],
    ) -> Mapping[int, tuple[ScoredCandidate, ...]]:
        """Return pre-qualification canonical similarity rows for experiments."""
        source_indices = tuple(
            self._catalogue_state.index_by_id[source_anime_id] for source_anime_id in source_anime_ids
        )
        ineligible_ids_by_source = tuple(
            self._catalogue_state.ineligible_ids_by_profile.get(
                (
                    self._catalogue_state.ratings[source_index],
                    _normalized_demographics(self._catalogue_state.demographics[source_index]),
                ),
                frozenset(),
            )
            for source_index in source_indices
        )
        retrieval = self._retrieval.retrieve(
            source_indices,
            ineligible_ids_by_source=ineligible_ids_by_source,
        )
        synopsis_ranker = getattr(self._retrieval, 'synopsis', None)
        results: dict[int, tuple[ScoredCandidate, ...]] = {}
        for row_number, source_anime_id in enumerate(source_anime_ids):
            source_index = source_indices[row_number]
            path_results = retrieval.results[row_number]
            eligible_ids = self._catalogue_state.eligible_ids_by_profile.get(
                (
                    self._catalogue_state.ratings[source_index],
                    _normalized_demographics(self._catalogue_state.demographics[source_index]),
                ),
                frozenset(),
            )

            canonical_eligibility_cache: dict[int, bool] = {}
            src_exclusions = (
                self._relationship_index.same_story_exclusions(source_anime_id)
                if self._relationship_index is not None
                else frozenset()
            )
            src_meta = self._catalogue_state.post_ranking_metadata_by_id.get(source_anime_id)
            src_themes = self._catalogue_state.themes_by_id.get(source_anime_id, frozenset())
            src_tags = self._hook_tags_by_id.get(source_anime_id, frozenset())
            src_genres = self._catalogue_state.genres_by_id.get(source_anime_id, frozenset())
            src_raw_tags = self._catalogue_state.tags_by_id.get(source_anime_id, frozenset())
            src_tone = self._catalogue_state.tonal_coordinate_by_id.get(source_anime_id, 0.0)
            src_content_level = self._catalogue_state.content_severity_by_id.get(
                source_anime_id, ContentSeverityLevel.LEVEL_0_UNIVERSAL
            )

            def is_canonical(
                candidate_id: int,
                source_id: int = source_anime_id,
                allowed_ids: frozenset[int] = eligible_ids,
                cache: dict[int, bool] = canonical_eligibility_cache,
                exclusions: frozenset[int] = src_exclusions,
                meta: Any = src_meta,
                themes: frozenset[Theme] = src_themes,
                tags: frozenset[str] = src_tags,
                genres: frozenset[Genre] = src_genres,
                raw_tags: frozenset[str] = src_raw_tags,
                tone: float = src_tone,
                content_level: ContentSeverityLevel = src_content_level,
            ) -> bool:
                cached_res = cache.get(candidate_id)
                if cached_res is not None:
                    return cached_res
                is_eligible_res = self._canonical_candidate_is_eligible(
                    source_id,
                    candidate_id,
                    allowed_ids,
                    source_exclusions=exclusions,
                    source_meta=meta,
                    source_themes=themes,
                    source_tags=tags,
                    source_genres=genres,
                    source_raw_tags=raw_tags,
                    source_tone=tone,
                    source_content_level=content_level,
                )
                cache[candidate_id] = is_eligible_res
                return is_eligible_res

            qualified = qualify_candidates(
                source_anime_id,
                build_union(
                    path_results,
                    original_path_results=(
                        retrieval.original_results[row_number] if retrieval.original_results else None
                    ),
                ),
                relationship_index=self._relationship_index,
                is_eligible=eligible_ids.__contains__,
                is_canonical_eligible=is_canonical,
            )
            entrypoint_candidates, _ = nominate_story_line_entrypoints(
                source_anime_id,
                qualified,
                relationship_index=self._relationship_index,
                is_eligible=eligible_ids.__contains__,
                is_canonical_eligible=is_canonical,
            )
            scoring_candidates, scoring_entity_ids = expand_story_line_entrypoints(
                entrypoint_candidates,
                relationship_index=self._relationship_index,
            )
            synopsis_pairwise_dense: dict[int, float] | None = None
            rating_embedding_cosine: dict[int, float] | None = None
            if (
                synopsis_ranker is not None
                and hasattr(synopsis_ranker, 'pairwise_dense_similarities')
                and scoring_candidates
            ):
                target_indices = [self._catalogue_state.index_by_id[c.anime_id] for c in scoring_candidates]
                fitted = getattr(synopsis_ranker, 'fitted_paths', ())
                active_scoring_paths = tuple(path for path in self._scoring_paths if path in fitted)
                b_sims = (
                    synopsis_ranker.pairwise_dense_similarities('bm25', source_index, target_indices)
                    if 'bm25' in self._scoring_paths and 'bm25' in fitted
                    else np.zeros(len(target_indices), dtype=np.float32)
                )
                l_sims = (
                    synopsis_ranker.pairwise_dense_similarities('lsa', source_index, target_indices)
                    if 'lsa' in self._scoring_paths and 'lsa' in fitted
                    else np.zeros(len(target_indices), dtype=np.float32)
                )
                if 'embedding' in self._scoring_paths and 'embedding' in fitted:
                    e_sims = synopsis_ranker.pairwise_dense_similarities('embedding', source_index, target_indices)
                    rating_embedding_cosine = {}
                    for candidate, similarity in zip(scoring_candidates, e_sims, strict=True):
                        sim_val = float(similarity)
                        rating_embedding_cosine[candidate.anime_id] = sim_val
                        if np.isfinite(similarity):
                            self._pairwise_dense_cosine_cache[(source_anime_id, candidate.anime_id)] = sim_val
                    sigmoid_weights = 1.0 / (1.0 + np.exp(-SIGMOID_GATE_SLOPE * (e_sims - SIGMOID_GATE_CENTER)))
                    ge_sims = np.where(
                        np.isfinite(e_sims) & (e_sims > 0.0),
                        sigmoid_weights * e_sims,
                        0.0,
                    ).astype(np.float32)
                else:
                    ge_sims = np.zeros(len(target_indices), dtype=np.float32)
                ble_sims = fuse_synopsis_vectors(
                    b_sims,
                    l_sims,
                    ge_sims,
                    active_paths=active_scoring_paths,
                )
                synopsis_pairwise_dense = {
                    c.anime_id: float(s) for c, s in zip(scoring_candidates, ble_sims, strict=True)
                }

            results[source_anime_id] = score_candidates(
                source_anime_id,
                scoring_candidates,
                genres_by_id=self._catalogue_state.genres_by_id,
                themes_by_id=self._catalogue_state.themes_by_id,
                demographics_by_id=self._catalogue_state.demographics_by_id,
                tags_by_id=self._catalogue_state.tags_by_id,
                ratings_by_id=self._catalogue_state.ratings_by_id,
                rating_policy=self._rating_policy,
                recommendation_entity_ids=scoring_entity_ids,
                ranking_policy=self._ranking_policy,
                properties=self._scoring_properties,
                property_values=self._scoring_property_values,
                synopsis_pairwise_dense=synopsis_pairwise_dense,
                rating_embedding_cosine=rating_embedding_cosine,
                embedding_gate_low=self._embedding_gate_low,
                embedding_gate_high=self._embedding_gate_high,
                gated_synopsis_transfer=self._gated_synopsis_transfer,
                evidence_qualified_multiplier=self._evidence_qualified_multiplier,
                pure_tone_contradiction_guard=self._pure_tone_contradiction_guard,
                generic_genre_suppression=self._generic_genre_suppression,
                hook_tag_promotion=self._hook_tag_promotion,
                structure_policy=self._structure_policy,
                narrative_profiles_by_id=self._catalogue_state.narrative_profiles_by_id,
                language_policy=self._language_policy,
                languages_by_id=self._catalogue_state.origin_language_by_id,
                synopses_by_id=self._catalogue_state.synopses_by_id,
                synopsis_scoring_paths=tuple(sorted(self._scoring_paths)),
                taxonomy_tokens_by_id=self._catalogue_state.taxonomy_tokens_by_id,
                thematic_leaf_tokens_by_id=self._catalogue_state.thematic_leaf_tokens_by_id,
                similarity_tags_by_id=self._catalogue_state.similarity_tags_by_id,
                parsed_genres_by_id=self._catalogue_state.parsed_genres_by_id,
                parsed_themes_by_id=self._catalogue_state.parsed_themes_by_id,
                tag_enums_by_id=self._catalogue_state.tag_enums_by_id,
                clash_masks_by_id=self._catalogue_state.clash_masks_by_id,
                tags_csr=self._catalogue_state.tags_csr,
                themes_csr=self._catalogue_state.themes_csr,
                genres_csr=self._catalogue_state.genres_csr,
                index_by_id=self._catalogue_state.index_by_id,
                ratings_by_row=getattr(self, '_ratings_by_row', None),
                demographics_by_row=getattr(self, '_demographics_by_row', None),
                parsed_genres_by_row=getattr(self, '_parsed_genres_by_row', None),
                parsed_themes_by_row=getattr(self, '_parsed_themes_by_row', None),
                tag_enums_by_row=getattr(self, '_tag_enums_by_row', None),
                taxonomy_tokens_by_row=getattr(self, '_taxonomy_tokens_by_row', None),
                thematic_leaf_tokens_by_row=getattr(self, '_thematic_leaf_tokens_by_row', None),
                narrative_profiles_by_row=getattr(self, '_narrative_profiles_by_row', None),
                synopses_by_row=getattr(self, '_synopses_by_row', None),
                languages_by_row=getattr(self, '_languages_by_row', None),
            )
        return results

    def _pairwise_dense_cosine(self, source_anime_id: int, candidate_id: int, fallback: float = 0.50) -> float:
        """Compute pairwise dense synopsis similarity between source and candidate."""
        index_by_id = getattr(self._catalogue_state, 'index_by_id', {})
        candidate_index = index_by_id.get(candidate_id)
        if candidate_index is None:
            return fallback

        source_rows = getattr(self, '_source_dense_cosine_rows', None)
        if source_rows is not None:
            cached_row = source_rows.get(source_anime_id)
            if cached_row is not None:
                val = float(cached_row[candidate_index])
                return val if np.isfinite(val) else fallback

        if hasattr(self, '_pairwise_dense_cosine_cache'):
            cached_val = self._pairwise_dense_cosine_cache.get((source_anime_id, candidate_id))
            if cached_val is not None:
                return cached_val

        synopsis_ranker = getattr(getattr(self, '_retrieval', None), 'synopsis', None)
        fitted_paths = getattr(synopsis_ranker, 'fitted_paths', ())
        if synopsis_ranker is None or 'embedding' not in fitted_paths:
            return fallback

        source_index = index_by_id.get(source_anime_id)
        if source_index is None:
            return fallback

        if source_rows is not None and hasattr(synopsis_ranker, 'pairwise_dense_similarities'):
            row = synopsis_ranker.pairwise_dense_similarities(
                'embedding',
                source_index,
                range(len(self._catalogue_state.anime_ids)),
            )
            source_rows[source_anime_id] = row
            val = float(row[candidate_index])
            return val if np.isfinite(val) else fallback

        similarities = synopsis_ranker.pairwise_dense_similarities('embedding', source_index, [candidate_index])
        if len(similarities) > 0 and np.isfinite(similarities[0]):
            val = float(similarities[0])
            if hasattr(self, '_pairwise_dense_cosine_cache'):
                self._pairwise_dense_cosine_cache[(source_anime_id, candidate_id)] = val
            return val
        return fallback

    def _canonical_candidate_is_eligible(
        self,
        source_anime_id: int,
        candidate_id: int,
        eligible_ids: frozenset[int],
        *,
        source_exclusions: frozenset[int] | None = None,
        source_meta: AnimePostRankingMetadata | None = None,
        source_themes: frozenset[Theme] | None = None,
        source_tags: frozenset[str] | None = None,
        source_genres: frozenset[Genre] | None = None,
        source_raw_tags: frozenset[str] | None = None,
        source_tone: float | None = None,
        source_content_level: ContentSeverityLevel | None = None,
    ) -> bool:
        if candidate_id not in eligible_ids:
            return False
        exclusions = (
            source_exclusions
            if source_exclusions is not None
            else (
                self._relationship_index.same_story_exclusions(source_anime_id)
                if self._relationship_index is not None
                else frozenset()
            )
        )
        if candidate_id in exclusions:
            return False

        if source_meta is None:
            source_meta = self._catalogue_state.post_ranking_metadata_by_id.get(source_anime_id)
        cand_idx = (
            self._catalogue_state.index_by_id.get(candidate_id) if hasattr(self, '_post_ranking_meta_by_row') else None
        )
        candidate_meta = (
            self._post_ranking_meta_by_row[cand_idx]
            if cand_idx is not None
            else self._catalogue_state.post_ranking_metadata_by_id.get(candidate_id)
        )
        if source_meta is None or candidate_meta is None:
            return True

        if source_themes is None:
            source_themes = self._catalogue_state.themes_by_id.get(source_anime_id, frozenset())
        candidate_themes = (
            self._themes_by_row[cand_idx]
            if cand_idx is not None
            else self._catalogue_state.themes_by_id.get(candidate_id, frozenset())
        )
        if source_tags is None:
            source_tags = self._hook_tags_by_id.get(source_anime_id, frozenset())
        candidate_tags = (
            self._hook_tags_by_row[cand_idx]
            if cand_idx is not None
            else self._hook_tags_by_id.get(candidate_id, frozenset())
        )
        shared_themes = source_themes & candidate_themes
        shared_hooks = source_tags & candidate_tags

        if source_genres is None:
            source_genres = self._catalogue_state.genres_by_id.get(source_anime_id, frozenset())
        candidate_genres = (
            self._genres_by_row[cand_idx]
            if cand_idx is not None
            else self._catalogue_state.genres_by_id.get(candidate_id, frozenset())
        )
        if source_raw_tags is None:
            source_raw_tags = self._catalogue_state.tags_by_id.get(source_anime_id, frozenset())
        candidate_raw_tags = (
            self._tags_by_row[cand_idx]
            if cand_idx is not None
            else self._catalogue_state.tags_by_id.get(candidate_id, frozenset())
        )

        if source_tone is None:
            source_tone = self._catalogue_state.tonal_coordinate_by_id.get(source_anime_id, 0.0)
        candidate_tone = (
            self._tonal_coordinate_by_row[cand_idx]
            if cand_idx is not None
            else self._catalogue_state.tonal_coordinate_by_id.get(candidate_id, 0.0)
        )
        if source_content_level is None:
            source_content_level = self._catalogue_state.content_severity_by_id.get(
                source_anime_id, ContentSeverityLevel.LEVEL_0_UNIVERSAL
            )
        candidate_content_level = (
            self._content_severity_by_row[cand_idx]
            if cand_idx is not None
            else self._catalogue_state.content_severity_by_id.get(candidate_id, ContentSeverityLevel.LEVEL_0_UNIVERSAL)
        )

        if is_hard_retrieval_contradiction(
            source_genres=source_genres,
            source_themes=source_themes,
            source_tags=source_raw_tags,
            source_tone=source_tone,
            source_content_level=source_content_level,
            candidate_genres=candidate_genres,
            candidate_themes=candidate_themes,
            candidate_tags=candidate_raw_tags,
            candidate_tone=candidate_tone,
            candidate_content_level=candidate_content_level,
        ):
            return False

        source_demo = parse_demographic(source_meta.demographic or '')
        candidate_demo = parse_demographic(candidate_meta.demographic or '')
        source_demos = {parse_demographic(d) for d in source_meta.demographics}
        candidate_demos = {parse_demographic(d) for d in candidate_meta.demographics}

        if (
            source_demo not in (Demographic.KIDS, Demographic.UNKNOWN)
            and candidate_demo is Demographic.KIDS
            and not shared_themes
            and not shared_hooks
        ):
            return False

        setting_backdrop_themes = {
            Theme.SCHOOL,
            Theme.WORKPLACE,
            Theme.HISTORICAL,
            Theme.ADULT_CAST,
            Theme.OTAKU_CULTURE,
        }
        substantive_shared_themes = shared_themes - setting_backdrop_themes
        has_corroboration = bool(substantive_shared_themes or shared_hooks)

        source_rating = normalize_rating(source_meta.rating)
        candidate_rating = normalize_rating(candidate_meta.rating)
        is_source_mature = source_rating in (RatingClass.R, RatingClass.R_PLUS, RatingClass.R_X) or (
            Demographic.SEINEN in source_demos
        )
        is_candidate_children = (
            candidate_rating in (RatingClass.G, RatingClass.PG) or candidate_demo is Demographic.KIDS
        )
        if is_source_mature and is_candidate_children and not has_corroboration:
            return False

        is_source_adult_demo = bool(source_demos & {Demographic.SEINEN, Demographic.JOSEI})
        if candidate_rating in (RatingClass.R, RatingClass.R_PLUS, RatingClass.R_X) and not has_corroboration:
            if candidate_rating is RatingClass.R_PLUS and not (
                source_rating in (RatingClass.R, RatingClass.R_PLUS, RatingClass.R_X) or is_source_adult_demo
            ):
                return False
            dense_cos = self._pairwise_dense_cosine(source_anime_id, candidate_id)
            if candidate_rating is RatingClass.R:
                if source_rating in (RatingClass.G, RatingClass.PG) and dense_cos < 0.35:
                    return False
                if source_rating is RatingClass.PG_13 and not is_source_adult_demo and dense_cos < 0.28:
                    return False

        if (
            not has_corroboration
            and candidate_genres
            and candidate_genres.issubset({Genre.FANTASY, Genre.ADVENTURE, Genre.ACTION})
            and self._pairwise_dense_cosine(source_anime_id, candidate_id) < 0.28
        ):
            return False

        if (
            Demographic.SEINEN in source_demos
            and Demographic.SHOUNEN in candidate_demos
            and Genre.SPORTS in candidate_genres
            and Genre.SPORTS not in source_genres
            and shared_themes.issubset({Theme.SCHOOL})
            and Theme.PSYCHOLOGICAL not in candidate_themes
            and not has_corroboration
        ):
            return False

        if not has_corroboration and self._pairwise_dense_cosine(source_anime_id, candidate_id) < 0.12:
            return False

        if (
            not has_corroboration
            and Genre.SPORTS in candidate_genres
            and Genre.SPORTS not in source_genres
            and self._pairwise_dense_cosine(source_anime_id, candidate_id) < 0.40
        ):
            return False

        if not has_corroboration:
            shared_genres = source_genres & candidate_genres
            substantive_shared_genres = shared_genres - {Genre.AWARD_WINNING}
            is_single_generic = len(substantive_shared_genres) == 1 and substantive_shared_genres.issubset(
                {Genre.ACTION, Genre.COMEDY, Genre.ADVENTURE, Genre.FANTASY}
            )
            if not substantive_shared_genres or is_single_generic:
                return False

        if (
            Genre.FANTASY in source_genres
            and bool(source_themes & {Theme.GORE, Theme.MILITARY})
            and Demographic.SEINEN in source_demos
            and (
                Theme.SCHOOL in candidate_themes
                or bool(candidate_themes & {Theme.SCHOOL} or candidate_genres & {Genre.MYSTERY})
            )
            and Genre.FANTASY not in candidate_genres
            and self._pairwise_dense_cosine(source_anime_id, candidate_id) < 0.35
        ):
            return False

        return not (
            len(source_genres) <= 1
            and not source_themes
            and not has_corroboration
            and self._pairwise_dense_cosine(source_anime_id, candidate_id) < 0.28
        )

    def raw_recommend_many(
        self,
        source_anime_ids: Sequence[int],
    ) -> Mapping[int, tuple[RawRecommendation, ...]]:
        """Return canonical ranked candidates before qualification or display policy."""
        raw_results = self.raw_similarity_many(source_anime_ids)
        result: dict[int, tuple[RawRecommendation, ...]] = {}
        for source_id, candidates in raw_results.items():
            source_tags = frozenset(similarity_tag_ids(self._catalogue_state.tags_by_id.get(source_id, frozenset())))
            ranked_candidates = candidates
            if self._metadata_post_ranking:
                ranked_candidates = self._apply_metadata_post_ranking(source_id, ranked_candidates)
            if type(self._ranking_policy) is ScoreDescending:
                ranked_candidates = tuple(
                    sorted(
                        ranked_candidates,
                        key=lambda candidate: (
                            -candidate.score,
                            -len(
                                source_tags
                                & self._catalogue_state.tags_by_id.get(candidate.recommendation_entity_id, frozenset())
                            ),
                            candidate.recommendation_entity_id,
                        ),
                    )
                )
            result[source_id] = tuple(
                RawRecommendation(
                    anime_id=candidate.recommendation_entity_id,
                    witness_member_id=candidate.witness_member_id,
                    score=candidate.score,
                    retrieval_paths=candidate.retrieval_paths,
                    semantic_available=any(path in SEMANTIC_EVIDENCE_PATHS for path in candidate.retrieval_paths),
                    categorical_available=any(path in CATEGORICAL_EVIDENCE_PATHS for path in candidate.retrieval_paths),
                )
                for candidate in ranked_candidates
            )
        # Clear transient batch cache to prevent memory bloat
        if hasattr(self, '_pairwise_dense_cosine_cache'):
            self._pairwise_dense_cosine_cache.clear()
        return result

    def _apply_metadata_post_ranking(
        self,
        source_id: int,
        candidates: Sequence[ScoredCandidate],
    ) -> tuple[ScoredCandidate, ...]:
        meta_by_id = self._catalogue_state.post_ranking_metadata_by_id
        source_meta = meta_by_id.get(source_id)
        if source_meta is None:
            return tuple(candidates)

        state = self._catalogue_state
        genres_by_id = getattr(state, 'genres_by_id', {})
        themes_by_id = getattr(state, 'themes_by_id', {})
        tags_by_id = getattr(state, 'tags_by_id', {})
        source_genres = genres_by_id.get(source_id, frozenset())
        source_themes = themes_by_id.get(source_id, frozenset())
        source_tags = frozenset(similarity_tag_ids(tags_by_id.get(source_id, frozenset())))
        is_sparse_anchor = (len(source_genres) <= 1 and not source_themes) or len(source_tags) <= 1
        hook_and_tone_tags = CORE_HOOK_TAGS | TONE_ATMOSPHERE_TAGS

        synopsis_ranker = getattr(getattr(self, '_retrieval', None), 'synopsis', None)
        fitted_paths = getattr(synopsis_ranker, 'fitted_paths', ())
        has_dense_sims = synopsis_ranker is not None and 'embedding' in fitted_paths

        dense_cos_by_id: dict[int, float] = {}
        source_row = getattr(self, '_source_dense_cosine_rows', {}).get(source_id)
        index_by_id = getattr(self._catalogue_state, 'index_by_id', {})
        cache = getattr(self, '_pairwise_dense_cosine_cache', {})
        uncached_candidates: list[tuple[int, int]] = []
        for candidate in candidates:
            entity_id = candidate.recommendation_entity_id
            if source_row is not None:
                cand_idx = index_by_id.get(entity_id)
                if cand_idx is not None:
                    val = float(source_row[cand_idx])
                    if np.isfinite(val):
                        dense_cos_by_id[entity_id] = val
                        continue
            cached_val = cache.get((source_id, entity_id))
            if cached_val is not None:
                dense_cos_by_id[entity_id] = cached_val
            elif has_dense_sims:
                cand_idx = index_by_id.get(entity_id)
                if cand_idx is not None:
                    uncached_candidates.append((candidate.recommendation_entity_id, cand_idx))

        if uncached_candidates and has_dense_sims:
            source_index = getattr(self._catalogue_state, 'index_by_id', {}).get(source_id)
            if source_index is not None:
                candidate_ids, candidate_indices = zip(*uncached_candidates, strict=True)
                batch_similarities = synopsis_ranker.pairwise_dense_similarities(
                    'embedding', source_index, candidate_indices
                )
                for entity_id, similarity in zip(candidate_ids, batch_similarities, strict=True):
                    if np.isfinite(similarity):
                        val = float(similarity)
                        dense_cos_by_id[entity_id] = val
                        cache[(source_id, entity_id)] = val

        adjusted: list[ScoredCandidate] = []
        for candidate in candidates:
            candidate_id = candidate.recommendation_entity_id
            shared_themes = source_themes & themes_by_id.get(candidate_id, frozenset())
            candidate_tags = tags_by_id.get(candidate_id, frozenset())
            shared_hooks_count = len((source_tags & candidate_tags) & hook_and_tone_tags)
            dense_cosine = dense_cos_by_id.get(candidate_id, 0.50)

            candidate_genres = genres_by_id.get(candidate_id, frozenset())
            candidate_themes = themes_by_id.get(candidate_id, frozenset())
            path_multiplier = compute_path_reliability_multiplier(
                candidate.retrieval_paths,
                candidate.score,
                source_genres=source_genres,
                candidate_genres=candidate_genres,
                source_themes=source_themes,
                candidate_themes=candidate_themes,
                shared_themes=shared_themes,
                shared_hook_tags_count=shared_hooks_count,
                dense_cosine=dense_cosine,
                is_sparse_anchor=is_sparse_anchor,
            )
            candidate_meta = meta_by_id.get(candidate_id)
            if candidate_meta is None:
                adjusted.append(candidate._replace(score=candidate.score * path_multiplier))
                continue

            multiplier = (
                compute_metadata_multiplier(
                    source_meta,
                    candidate_meta,
                    dense_cosine=dense_cosine,
                    shared_hooks_count=shared_hooks_count,
                )
                * path_multiplier
            )
            adjusted_score = candidate.score * multiplier
            adjusted.append(candidate._replace(score=adjusted_score))

        return tuple(adjusted)

    def _maturity_adjusted_score(self, source_id: int, candidate_id: int, score: float) -> float:
        source_rating = _rating_class(self._catalogue_state.ratings[self._catalogue_state.index_by_id[source_id]])
        candidate_rating = _rating_class(self._catalogue_state.ratings[self._catalogue_state.index_by_id[candidate_id]])

        # G/PG vs R/R+/Rx child safety guard
        if source_rating in (RatingClass.G, RatingClass.PG) and candidate_rating in (
            RatingClass.R,
            RatingClass.R_PLUS,
            RatingClass.R_X,
        ):
            return score * 0.10

        if not self._weak_maturity_demotion:
            return score
        shared_genres = self._catalogue_state.genres_by_id[source_id] & self._catalogue_state.genres_by_id[candidate_id]
        shared_themes = self._catalogue_state.themes_by_id[source_id] & self._catalogue_state.themes_by_id[candidate_id]
        if is_weak_special_maturity_mismatch(
            source_rating,
            candidate_rating,
            self._catalogue_state.anime_type_by_id.get(candidate_id),
            self._catalogue_state.episodes_by_id.get(candidate_id),
            self._catalogue_state.source_by_id.get(candidate_id),
            self._catalogue_state.score_by_id.get(candidate_id),
            shared_genres,
            shared_themes,
        ):
            return score - self._weak_maturity_demotion_penalty
        return score

    def search_recommendations(
        self,
        source_anime_id: int,
        query: int | str,
        *,
        limit: int = 10,
    ) -> tuple[RecommendationItem, ...]:
        """Find ranked recommendations for one source by ID or title text."""
        if limit < 1:
            raise ValueError('limit must be positive')
        recommendations = self.recommend(source_anime_id, limit=100)
        if isinstance(query, int):
            return tuple(item for item in recommendations if item.anime_id == query)[:limit]
        normalized_query = query.strip().casefold()
        if not normalized_query:
            raise ValueError('recommendation search query cannot be empty')
        return tuple(
            item
            for item in recommendations
            if normalized_query in self._catalogue_state.titles.get(item.anime_id, '').casefold()
        )[:limit]
