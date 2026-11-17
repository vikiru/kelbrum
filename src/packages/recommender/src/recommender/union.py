"""Candidate union and production retrieval-group reduction."""

from collections.abc import Iterable, Mapping, Sequence
from heapq import nsmallest
from math import isfinite

import msgspec

from recommender.contracts import RecommendationResult


class PathEvidence(msgspec.Struct, frozen=True):
    """One path's nomination of a candidate."""

    path: str
    rank: int
    score: float
    post_reducer_position: int | None = None
    witness_member_id: int | None = None


class UnionCandidate(msgspec.Struct, frozen=True):
    """One unique anime ID with every path nomination retained."""

    anime_id: int
    evidence: tuple[PathEvidence, ...]
    witness_evidence: tuple[PathEvidence, ...] = ()
    witness_member_id: int | None = None
    score_multiplier: float = 1.0

    def __post_init__(self) -> None:
        if not isfinite(self.score_multiplier) or not 0.0 <= self.score_multiplier <= 1.0:
            raise ValueError('candidate score multiplier must be finite and between 0 and 1')

    @property
    def source_count(self) -> int:
        return len(self.evidence)

    @property
    def best_rank(self) -> int:
        return min(item.rank for item in self.evidence)

    @property
    def path_count(self) -> int:
        return len({item.path for item in self.evidence})

    @property
    def retrieval_group_count(self) -> int:
        return len({PATH_GROUPS[item.path] for item in self.evidence})

    @property
    def evidence_groups(self) -> tuple[str, ...]:
        return tuple(sorted({PATH_GROUPS[item.path] for item in self.evidence}))


class RetrievalGroupBudget(msgspec.Struct, frozen=True):
    """Maximum candidate IDs retained from each retrieval group."""

    semantic: int = 600
    structured: int = 600
    neighbourhood: int = 200
    affinity: int = 60

    def __post_init__(self) -> None:
        if min(self.semantic, self.structured, self.neighbourhood, self.affinity) < 1:
            raise ValueError('retrieval group budgets must be positive')


class RetrievalDiagnostics(msgspec.Struct, frozen=True):
    """Aggregate candidate counts from the most recent raw recommendation batch."""

    source_count: int
    unbounded_candidate_count: int
    reduced_candidate_count: int
    retrieval_group_candidate_counts: dict[str, int]
    path_timings_ms: dict[str, float] = msgspec.field(default_factory=dict)
    path_candidate_counts: dict[str, int] = msgspec.field(default_factory=dict)


class GroupSelection(msgspec.Struct, frozen=True):
    """Candidate IDs retained through one retrieval group."""

    group: str
    candidate_ids: tuple[int, ...]


class PathReduction(msgspec.Struct, frozen=True):
    """Retained path evidence and the groups that selected each candidate."""

    path_results: tuple[tuple[str, tuple[tuple[int, float], ...]], ...]
    selected_by_group: tuple[GroupSelection, ...]
    original_path_results: tuple[tuple[str, tuple[tuple[int, float], ...]], ...]


AVAILABLE_RETRIEVAL_PATHS = (
    'weighted-v2',
    'genres',
    'themes',
    'tags',
    'bm25',
    'char_3_5g_tfidf',
    'lsa',
    'embedding',
    'demographic',
    'studio',
)
PATH_GROUPS = {
    'bm25': 'semantic',
    'char_3_5g_tfidf': 'semantic',
    'char_tfidf': 'semantic',
    'char': 'semantic',
    'lsa': 'semantic',
    'embedding': 'semantic',
    'genres': 'structured',
    'themes': 'structured',
    'tags': 'structured',
    'weighted-v2': 'neighbourhood',
    'demographic': 'affinity',
    'studio': 'affinity',
}
DEFAULT_RETRIEVAL_PATHS = (
    'embedding',
    'weighted-v2',
    'bm25',
    'themes',
    'genres',
    'tags',
    'lsa',
)
DEFAULT_PATH_LIMITS: dict[str, int] = {}
RETRIEVAL_REDUCER_POLICY = {
    'group_reduction': 'raw-max-per-storyline-retrieval-group-budget-v2',
    'tie_break': 'candidate-id-ascending',
    'invalid_scores': 'discard-non-finite-and-non-positive',
}
RETRIEVAL_PATH_ORDER = AVAILABLE_RETRIEVAL_PATHS
SEMANTIC_EVIDENCE_PATHS = frozenset({'bm25', 'lsa', 'embedding'})
CATEGORICAL_EVIDENCE_PATHS = frozenset({'genres', 'themes', 'tags', 'demographic', 'studio', 'weighted-v2'})
DEFAULT_RETRIEVAL_GROUP_BUDGET = RetrievalGroupBudget()
UNION_POLICY_IDENTITY = 'evidence-union-v2'


def validate_retrieval_paths(paths: Sequence[str]) -> tuple[str, ...]:
    """Validate and preserve the caller's explicit retrieval path order."""
    active = tuple(paths)
    if len(set(active)) != len(active):
        raise ValueError('retrieval paths must be unique')
    unknown = set(active) - set(AVAILABLE_RETRIEVAL_PATHS)
    if unknown:
        raise ValueError(f'unsupported retrieval paths: {", ".join(sorted(unknown))}')
    return active


def reduce_path_results(
    path_results: Sequence[tuple[str, Sequence[tuple[int, float]]]],
    *,
    budgets: RetrievalGroupBudget = DEFAULT_RETRIEVAL_GROUP_BUDGET,
    story_line_entrypoint_by_id: Mapping[int, int] | None = None,
) -> PathReduction:
    """Apply group budgets by storyline while retaining each selected member's evidence."""
    for path, _ in path_results:
        if path not in PATH_GROUPS:
            raise ValueError(f'unknown retrieval path: {path}')

    group_scores = _collect_group_scores(path_results, story_line_entrypoint_by_id)
    group_limits = {
        'semantic': budgets.semantic,
        'structured': budgets.structured,
        'neighbourhood': budgets.neighbourhood,
        'affinity': budgets.affinity,
    }
    selected_by_group = tuple(
        GroupSelection(group, tuple(sorted(_top_candidate_ids(scores, group_limits[group]))))
        for group, scores in sorted(group_scores.items())
    )
    selected_story_lines = {
        story_line_id for selection in selected_by_group for story_line_id in selection.candidate_ids
    }
    retained_path_results = tuple(
        (
            path,
            tuple(
                (candidate_id, score)
                for candidate_id, score in results
                if _story_line_id(candidate_id, story_line_entrypoint_by_id) in selected_story_lines
            ),
        )
        for path, results in path_results
    )
    original_results = tuple((path, tuple(results)) for path, results in path_results)
    return PathReduction(retained_path_results, selected_by_group, original_results)


def _collect_group_scores(
    path_results: Sequence[tuple[str, Sequence[tuple[int, float]]]],
    story_line_entrypoint_by_id: Mapping[int, int] | None,
) -> dict[str, dict[int, float]]:
    group_scores: dict[str, dict[int, float]] = {}
    for path, results in path_results:
        candidates = group_scores.setdefault(PATH_GROUPS[path], {})
        max_score = max((score for _, score in results), default=1.0)
        scale = max_score if max_score > 0.0 else 1.0
        for candidate_id, score in results:
            story_line_id = (
                story_line_entrypoint_by_id.get(candidate_id, candidate_id)
                if story_line_entrypoint_by_id is not None
                else candidate_id
            )
            normalized_score = score / scale
            candidates[story_line_id] = max(candidates.get(story_line_id, float('-inf')), normalized_score)
    return group_scores


def _story_line_id(candidate_id: int, story_line_entrypoint_by_id: Mapping[int, int] | None) -> int:
    if story_line_entrypoint_by_id is None:
        return candidate_id
    return story_line_entrypoint_by_id.get(candidate_id, candidate_id)


def _top_candidate_ids(
    scores: dict[int, float],
    limit: int,
    *,
    tie_breakers: Mapping[int, float] | None = None,
) -> set[int]:
    if tie_breakers is None:
        return {
            candidate_id for candidate_id, _ in nsmallest(limit, scores.items(), key=lambda item: (-item[1], item[0]))
        }
    return {
        candidate_id
        for candidate_id, _ in nsmallest(
            limit,
            scores.items(),
            key=lambda item: (-item[1], -tie_breakers.get(item[0], 0.0), item[0]),
        )
    }


def build_union(
    path_results: Iterable[tuple[str, Sequence[tuple[int, float]]]],
    *,
    original_path_results: Iterable[tuple[str, Sequence[tuple[int, float]]]] | None = None,
) -> tuple[UnionCandidate, ...]:
    """Merge path results once by anime ID without mixing path scores."""
    original_ranks: dict[str, dict[int, int]] = {}
    for path, results in original_path_results or ():
        ranks_for_path: dict[int, int] = {}
        for rank, (anime_id, _score) in enumerate(results, start=1):
            if anime_id not in ranks_for_path:
                ranks_for_path[anime_id] = rank
        original_ranks[path] = ranks_for_path
    collected: dict[int, list[PathEvidence]] = {}
    for path, results in path_results:
        if not path.strip():
            raise ValueError('retrieval path name cannot be empty')
        path_ranks = original_ranks.get(path)
        unique_results: dict[int, tuple[int, float, int]] = {}
        for post_reducer_position, (anime_id, score) in enumerate(results, start=1):
            rank = path_ranks.get(anime_id, post_reducer_position) if path_ranks is not None else post_reducer_position
            if anime_id <= 0 or rank <= 0:
                raise ValueError('retrieval results require positive IDs and ranks')
            if not isfinite(score):
                raise ValueError('retrieval scores must be finite')
            previous = unique_results.get(anime_id)
            if previous is None or score > previous[1]:
                unique_results[anime_id] = (rank, score, post_reducer_position)
        for anime_id, (rank, score, post_reducer_position) in unique_results.items():
            collected.setdefault(anime_id, []).append(PathEvidence(path, rank, score, post_reducer_position))
    candidates = []
    for anime_id, evidence in collected.items():
        ordered_evidence = tuple(sorted(evidence, key=_evidence_order))
        witness_evidence = tuple(
            PathEvidence(item.path, item.rank, item.score, item.post_reducer_position, anime_id)
            for item in ordered_evidence
        )
        candidates.append(
            UnionCandidate(
                anime_id=anime_id,
                evidence=ordered_evidence,
                witness_evidence=witness_evidence,
                witness_member_id=anime_id,
            )
        )
    return tuple(sorted(candidates, key=_candidate_order))


def build_union_from_results(
    path_results: Iterable[tuple[str, RecommendationResult]],
) -> tuple[UnionCandidate, ...]:
    """Adapt existing recommender results into one unique-ID union."""
    return build_union(
        (path, tuple((item.anime_id, item.score) for item in result.items)) for path, result in path_results
    )


def _evidence_order(item: PathEvidence) -> tuple[str, int]:
    return item.path, item.rank


def _candidate_order(candidate: UnionCandidate) -> int:
    return candidate.anime_id
