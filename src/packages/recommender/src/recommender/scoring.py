"""Weighted evidence scoring and similarity metrics for recommendations."""

from collections.abc import Callable, Mapping, Sequence

import msgspec

from recommender.contracts import RecommendationItem
from recommender.ranking import RankingPolicy, ScoredCandidate, ScoreDescending
from recommender.union import SEMANTIC_EVIDENCE_PATHS, UnionCandidate

SYNOPSIS_WEIGHT = 0.42
TAG_WEIGHT = 0.24
THEME_WEIGHT = 0.18
GENRE_WEIGHT = 0.10
DEMOGRAPHIC_WEIGHT = 0.06

ScoringMetric = Callable[[frozenset[str], Sequence[str] | frozenset[str]], float]
PropertyValues = Mapping[int, Sequence[str] | frozenset[str]]


class ScoringProperty(msgspec.Struct, frozen=True):
    """Describe one metadata contribution and its replaceable metric."""

    name: str
    weight: float
    metric: ScoringMetric
    metric_identity: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError('scoring property name cannot be empty')
        if self.weight < 0.0:
            raise ValueError('scoring property weight cannot be negative')
        if self.metric_identity is not None and not self.metric_identity.strip():
            raise ValueError('metric identity cannot be empty')


def default_scoring_properties() -> tuple[ScoringProperty, ...]:
    """Return the default metadata scoring policy in stable order."""
    return (
        ScoringProperty('tags', TAG_WEIGHT, coverage, 'coverage-v1'),
        ScoringProperty('themes', THEME_WEIGHT, dice, 'dice-v1'),
        ScoringProperty('genres', GENRE_WEIGHT, coverage, 'coverage-v1'),
        ScoringProperty('demographics', DEMOGRAPHIC_WEIGHT, dice, 'dice-v1'),
    )


def to_recommendation_item(anime_id: int, score: float) -> RecommendationItem:
    """Map a scored candidate to the lightweight result contract."""
    return RecommendationItem(
        anime_id=anime_id,
        score=score,
        contributions=(('normalized_fusion', score),),
    )


def score_candidates(
    source_anime_id: int,
    candidates: Sequence[UnionCandidate],
    *,
    genres_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    themes_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    tags_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    demographics_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    canonical_ids: Mapping[int, int] | None = None,
    ranking_policy: RankingPolicy | None = None,
    properties: Sequence[ScoringProperty] | None = None,
    property_values: Mapping[str, PropertyValues] | None = None,
) -> tuple[ScoredCandidate, ...]:
    """Score qualified candidates without eligibility or presentation policy."""
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
    source_values = {name: frozenset(values.get(source_anime_id, ())) for name, values in candidate_values.items()}
    scored: list[ScoredCandidate] = []
    for candidate in candidates:
        candidate_id = candidate.anime_id
        canonical_id = (canonical_ids or {}).get(candidate_id, candidate_id)
        synopsis_score = max(
            (item.score for item in candidate.evidence if item.path in SEMANTIC_EVIDENCE_PATHS),
            default=0.0,
        )
        metadata_score = sum(
            property_spec.weight
            * property_spec.metric(
                source_values[property_spec.name],
                candidate_values[property_spec.name].get(candidate_id, ()),
            )
            for property_spec in active_properties
        )
        score = SYNOPSIS_WEIGHT * synopsis_score + metadata_score
        scored.append((canonical_id, candidate_id, score, tuple(sorted(item.path for item in candidate.evidence))))
    deduplicated: dict[int, tuple[int, float, set[str]]] = {}
    for candidate_id, alias_id, score, paths in scored:
        current = deduplicated.get(candidate_id)
        if current is None:
            deduplicated[candidate_id] = (alias_id, score, set(paths))
            continue
        best_alias_id, best_score, retained_paths = current
        retained_paths.update(paths)
        if score > best_score:
            best_alias_id, best_score = alias_id, score
        deduplicated[candidate_id] = (best_alias_id, best_score, retained_paths)
    deduplicated_candidates = tuple(
        (candidate_id, alias_id, score, tuple(sorted(paths)))
        for candidate_id, (alias_id, score, paths) in deduplicated.items()
    )
    return (ranking_policy or ScoreDescending()).rank(deduplicated_candidates)


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
