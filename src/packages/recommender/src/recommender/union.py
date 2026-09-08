"""Evidence-preserving unique-ID Union for independent retrieval paths."""

from collections.abc import Iterable, Sequence
from enum import StrEnum

import msgspec

from models.contracts import RecommendationResult


class PathEvidence(msgspec.Struct, frozen=True):
    """One path's nomination of a candidate."""

    path: str
    rank: int
    score: float


class UnionCandidate(msgspec.Struct, frozen=True):
    """One unique anime ID with every path nomination retained."""

    anime_id: int
    evidence: tuple[PathEvidence, ...]

    @property
    def source_count(self) -> int:
        return len(self.evidence)

    @property
    def best_rank(self) -> int:
        return min(item.rank for item in self.evidence)


class RetrievalMode(StrEnum):
    """Select the candidate budget applied before frozen scoring."""

    LEGACY_UNION = 'legacy_union'
    FAMILY_REDUCED = 'family_reduced'


class RetrievalFamilyBudget(msgspec.Struct, frozen=True):
    """Maximum nominations retained from each retrieval family."""

    semantic: int = 200
    structured: int = 100
    neighbourhood: int = 100
    affinity: int = 50

    def __post_init__(self) -> None:
        if min(self.semantic, self.structured, self.neighbourhood, self.affinity) < 1:
            raise ValueError('retrieval family budgets must be positive')


class RetrievalDiagnostics(msgspec.Struct, frozen=True):
    """Aggregate candidate counts from the most recent raw recommendation batch."""

    source_count: int
    unbounded_candidate_count: int
    reduced_candidate_count: int
    family_candidate_counts: dict[str, int]


PATH_FAMILIES = {
    'bm25': 'semantic',
    'lsa': 'semantic',
    'embedding': 'semantic',
    'genres': 'structured',
    'themes': 'structured',
    'tags': 'structured',
    'conjunctions': 'structured',
    'concepts': 'structured',
    'weighted-v2': 'neighbourhood',
    'direct-knn': 'neighbourhood',
    'profile-knn': 'neighbourhood',
    'demographic': 'affinity',
    'studio': 'affinity',
}
RETRIEVAL_REDUCER_VERSION = 'family-reducer-v1'
RETRIEVAL_PATH_ORDER = tuple(PATH_FAMILIES)
SEMANTIC_EVIDENCE_PATHS = frozenset({'bm25', 'lsa', 'embedding'})
CATEGORICAL_EVIDENCE_PATHS = frozenset({'genres', 'themes', 'tags', 'demographic', 'studio', 'weighted-v2'})
DEFAULT_RETRIEVAL_FAMILY_BUDGET = RetrievalFamilyBudget()


def reduce_path_results(
    path_results: Sequence[tuple[str, Sequence[tuple[int, float]]]],
    *,
    mode: RetrievalMode,
    budgets: RetrievalFamilyBudget = DEFAULT_RETRIEVAL_FAMILY_BUDGET,
) -> tuple[tuple[str, tuple[tuple[int, float], ...]], ...]:
    """Apply family budgets while preserving original path evidence and order."""
    if mode is RetrievalMode.LEGACY_UNION:
        return tuple((path, tuple(results)) for path, results in path_results)
    family_candidates: dict[str, dict[int, float]] = {}
    for path, results in path_results:
        try:
            family = PATH_FAMILIES[path]
        except KeyError as error:
            raise ValueError(f'unknown retrieval path: {path}') from error
        candidates = family_candidates.setdefault(family, {})
        for candidate_id, score in results:
            candidates[candidate_id] = max(candidates.get(candidate_id, float('-inf')), float(score))
    family_limits = {
        'semantic': budgets.semantic,
        'structured': budgets.structured,
        'neighbourhood': budgets.neighbourhood,
        'affinity': budgets.affinity,
    }

    def _sort_candidate_score(item: tuple[int, float]) -> tuple[float, int]:
        return (-item[1], item[0])

    retained: set[int] = set()
    for family, candidates in family_candidates.items():
        ranked = sorted(candidates.items(), key=_sort_candidate_score)
        retained.update(candidate_id for candidate_id, _ in ranked[: family_limits[family]])
    return tuple(
        (path, tuple((candidate_id, score) for candidate_id, score in results if candidate_id in retained))
        for path, results in path_results
    )


def build_union(
    path_results: Iterable[tuple[str, Sequence[tuple[int, float]]]],
) -> tuple[UnionCandidate, ...]:
    """Merge path results once by anime ID without mixing path scores."""
    collected: dict[int, list[PathEvidence]] = {}
    for path, results in path_results:
        if not path.strip():
            raise ValueError('retrieval path name cannot be empty')
        for rank, (anime_id, score) in enumerate(results, start=1):
            if anime_id <= 0 or rank <= 0:
                raise ValueError('retrieval results require positive IDs and ranks')
            collected.setdefault(anime_id, []).append(PathEvidence(path, rank, float(score)))
    candidates = [
        UnionCandidate(anime_id, tuple(sorted(evidence, key=_evidence_order)))
        for anime_id, evidence in collected.items()
    ]
    return tuple(sorted(candidates, key=_candidate_order))


def build_union_from_results(
    path_results: Iterable[tuple[str, RecommendationResult]],
) -> tuple[UnionCandidate, ...]:
    """Adapt existing recommender results into one unique-ID Union."""
    return build_union(
        (
            path,
            tuple((item.anime_id, item.score) for item in result.items),
        )
        for path, result in path_results
    )


def _evidence_order(item: PathEvidence) -> tuple[str, int]:
    return item.path, item.rank


def _candidate_order(candidate: UnionCandidate) -> int:
    return candidate.anime_id
