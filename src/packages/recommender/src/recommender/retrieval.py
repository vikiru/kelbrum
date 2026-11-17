"""Independent candidate retrieval and retrieval-group reduction."""

from collections.abc import Callable, Mapping, Sequence
from time import perf_counter
from typing import Protocol, TypeVar

import msgspec

from config import derive_payload_identity
from graph import RelationshipIndex
from recommender.paths import MAX_FULL_MATRIX_SCORE_BYTES, SynopsisPathIndex
from recommender.union import (
    DEFAULT_PATH_LIMITS,
    DEFAULT_RETRIEVAL_PATHS,
    PATH_GROUPS,
    RETRIEVAL_PATH_ORDER,
    RETRIEVAL_REDUCER_POLICY,
    GroupSelection,
    RetrievalDiagnostics,
    RetrievalGroupBudget,
    reduce_path_results,
    validate_retrieval_paths,
)
from recommender.weighted_v2 import WeightedV2Index

PathScores = tuple[tuple[int, float], ...]
PathResults = tuple[tuple[str, PathScores], ...]
ResultT = TypeVar('ResultT')
SEMANTIC_PATHS = frozenset({'bm25', 'char_3_5g_tfidf', 'lsa', 'embedding'})


def _rank_weighted(
    index: WeightedV2Index,
    source_indices: Sequence[int],
    limit: int,
    candidate_batch_size: int,
    excluded_ids_by_source: Sequence[frozenset[int]] | None,
) -> tuple[PathScores, ...]:
    if excluded_ids_by_source is None:
        return index.rank_many_streaming(source_indices, limit=limit, candidate_batch_size=candidate_batch_size)
    return index.rank_many_streaming(
        source_indices,
        limit=limit,
        candidate_batch_size=candidate_batch_size,
        excluded_ids_by_source=excluded_ids_by_source,
    )


class BatchRanker(Protocol):
    def rank_many(
        self,
        source_indices: Sequence[int],
        *,
        limit: int,
        excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> tuple[PathScores, ...]: ...


class StreamingRanker(Protocol):
    def rank_many_streaming(
        self,
        path: str,
        source_indices: Sequence[int],
        *,
        limit: int,
        candidate_batch_size: int,
        excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> tuple[PathScores, ...]: ...


class RetrievalBatch(msgspec.Struct, frozen=True):
    """Reduced path evidence and retrieval-group selections for each source row."""

    results: tuple[PathResults, ...]
    diagnostics: RetrievalDiagnostics
    selected_by_group: tuple[tuple[GroupSelection, ...], ...] = ()
    original_results: tuple[PathResults, ...] = ()


class RetrievalEngine:
    """Retrieve and reduce candidate paths without scoring or qualification policy."""

    def __init__(
        self,
        synopsis: StreamingRanker,
        weighted: WeightedV2Index | None,
        categorical: Mapping[str, BatchRanker],
        affinity: Mapping[str, BatchRanker],
        *,
        retrieval_limit: int,
        retrieval_batch_size: int = 512,
        group_budget: RetrievalGroupBudget | None = None,
        path_limits: Mapping[str, int] | None = None,
        enabled_paths: Sequence[str] = DEFAULT_RETRIEVAL_PATHS,
        relationship_index: RelationshipIndex | None = None,
    ) -> None:
        if retrieval_limit < 1:
            raise ValueError('retrieval_limit must be positive')
        if retrieval_batch_size < 1:
            raise ValueError('retrieval batch size must be positive')
        self._synopsis = synopsis
        self._weighted = weighted
        self._categorical = categorical
        self._affinity = affinity
        self._retrieval_limit = retrieval_limit
        self._retrieval_batch_size = retrieval_batch_size
        self._group_budget = group_budget
        self._path_limits = dict(DEFAULT_PATH_LIMITS if path_limits is None else path_limits)
        self._enabled_paths = validate_retrieval_paths(enabled_paths)
        self._relationship_index = relationship_index
        self._enabled_synopsis_paths = tuple(path for path in self._enabled_paths if path in SEMANTIC_PATHS)
        self._last_diagnostics = RetrievalDiagnostics(0, 0, 0, {})

    @property
    def last_diagnostics(self) -> RetrievalDiagnostics:
        """Return aggregate counts from the most recent retrieval batch."""
        return self._last_diagnostics

    @property
    def synopsis(self) -> StreamingRanker:
        """Return the synopsis path ranker."""
        return self._synopsis

    @property
    def weighted(self) -> WeightedV2Index | None:
        """Return the weighted v2 index if enabled."""
        return self._weighted

    @property
    def identity(self) -> str:
        """Return the deterministic identity of the active retrieval policy."""
        budget = self._group_budget
        budget_payload = (
            None
            if budget is None
            else {
                'semantic': budget.semantic,
                'structured': budget.structured,
                'neighbourhood': budget.neighbourhood,
                'affinity': budget.affinity,
            }
        )
        configuration = {
            'policy': RETRIEVAL_REDUCER_POLICY if budget is not None else 'no-group-reduction',
            'retrieval_group_budget': budget_payload,
            'path_limits': self._path_limits,
            'path_order': RETRIEVAL_PATH_ORDER,
            'path_groups': PATH_GROUPS,
            'enabled_paths': self._enabled_paths,
            'story_line_policy': (
                self._relationship_index.fingerprint() if self._relationship_index is not None else 'unmapped'
            ),
            'retrieval_limit': self._retrieval_limit,
            'retrieval_batch_size': self._retrieval_batch_size,
            'synopsis_execution': 'adaptive-full-matrix-v1',
            'full_matrix_score_buffer_limit_bytes': MAX_FULL_MATRIX_SCORE_BYTES,
        }
        return derive_payload_identity(configuration)

    def retrieve(
        self,
        source_indices: Sequence[int],
        *,
        ineligible_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> RetrievalBatch:
        """Retrieve all active paths once per batch and apply configured reduction."""
        path_timings_ms: dict[str, float] = {}
        excluded_ids_by_source = self._exclusions_for_sources(source_indices, ineligible_ids_by_source)
        streamed = {
            name: self._measure_path_timing(
                name,
                path_timings_ms,
                lambda name=name: self._rank_synopsis_path(name, source_indices, excluded_ids_by_source),
            )
            for name in self._enabled_synopsis_paths
        }
        weighted: tuple[PathScores, ...]
        if self._weighted is None:
            weighted = ()
        else:
            weighted_index = self._weighted
            weighted = self._measure_path_timing(
                'weighted-v2',
                path_timings_ms,
                lambda: _rank_weighted(
                    weighted_index,
                    source_indices,
                    self._path_limits.get('weighted-v2', self._retrieval_limit),
                    self._retrieval_batch_size,
                    excluded_ids_by_source,
                ),
            )
        categorical = self._rank_paths(self._categorical, source_indices, path_timings_ms, excluded_ids_by_source)
        affinity = self._rank_paths(self._affinity, source_indices, path_timings_ms, excluded_ids_by_source)

        results: list[PathResults] = []
        original_results: list[PathResults] = []
        unbounded_count = 0
        reduced_count = 0
        group_counts: dict[str, int] = {}
        path_candidate_counts: dict[str, int] = {}
        selected_by_group: list[tuple[GroupSelection, ...]] = []
        reduction_started = perf_counter()
        for row_number in range(len(source_indices)):
            path_results = self._path_results_for_row(
                row_number,
                weighted=weighted,
                categorical=categorical,
                streamed=streamed,
                affinity=affinity,
            )
            unbounded_count += sum(len(values) for _, values in path_results)
            for path, values in path_results:
                path_candidate_counts[path] = path_candidate_counts.get(path, 0) + len(values)

            if self._group_budget is None:
                row_original_results = tuple((path, tuple(values)) for path, values in path_results)
                original_results.append(row_original_results)
                reduced_count += len({candidate_id for _, values in path_results for candidate_id, _ in values})
                selected_by_group.append(())
                results.append(tuple((path, tuple(values)) for path, values in path_results))
            else:
                reduction = reduce_path_results(
                    path_results,
                    budgets=self._group_budget,
                    story_line_entrypoint_by_id=(
                        self._relationship_index.story_line_entrypoint_by_id
                        if self._relationship_index is not None
                        else None
                    ),
                )
                original_results.append(reduction.original_path_results)
                reduced = reduction.path_results
                reduced_count += len({candidate_id for _, values in reduced for candidate_id, _ in values})
                for selection in reduction.selected_by_group:
                    group_counts[selection.group] = group_counts.get(selection.group, 0) + len(selection.candidate_ids)
                selected_by_group.append(reduction.selected_by_group)
                results.append(tuple(reduced))
        path_timings_ms['retrieval_group_reduction'] = (perf_counter() - reduction_started) * 1_000
        batch = RetrievalBatch(
            tuple(results),
            RetrievalDiagnostics(
                len(source_indices),
                unbounded_count,
                reduced_count,
                group_counts,
                path_timings_ms,
                path_candidate_counts,
            ),
            tuple(selected_by_group),
            tuple(original_results),
        )
        self._last_diagnostics = batch.diagnostics
        return batch

    def _rank_paths(
        self,
        indexes: Mapping[str, BatchRanker],
        source_indices: Sequence[int],
        timings_ms: dict[str, float],
        excluded_ids_by_source: Sequence[frozenset[int]] | None,
    ) -> dict[str, tuple[PathScores, ...]]:
        """Rank each enabled structured path and record its timing."""
        return {
            name: self._measure_path_timing(
                name,
                timings_ms,
                lambda name=name, index=index: index.rank_many(
                    source_indices,
                    limit=self._path_limits.get(name, self._retrieval_limit),
                    **({} if excluded_ids_by_source is None else {'excluded_ids_by_source': excluded_ids_by_source}),
                ),
            )
            for name, index in indexes.items()
            if name in self._enabled_paths
        }

    def _exclusions_for_sources(
        self,
        source_indices: Sequence[int],
        ineligible_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> tuple[frozenset[int], ...] | None:
        if self._relationship_index is None and ineligible_ids_by_source is None:
            return None
        anime_ids = getattr(self._synopsis, 'anime_ids', None)
        if anime_ids is None:
            raise ValueError('graph-aware retrieval requires the synopsis catalogue ID alignment')
        exclusions: list[frozenset[int]] = []
        for i, source_index in enumerate(source_indices):
            same_story = (
                self._relationship_index.same_story_exclusions(int(anime_ids[source_index]))
                if self._relationship_index is not None
                else frozenset()
            )
            ineligible = ineligible_ids_by_source[i] if ineligible_ids_by_source is not None else frozenset()
            exclusions.append(frozenset(same_story | ineligible))
        return tuple(exclusions)

    def _rank_synopsis_path(
        self,
        path: str,
        source_indices: Sequence[int],
        excluded_ids_by_source: Sequence[frozenset[int]] | None,
    ) -> tuple[PathScores, ...]:
        limit = self._path_limits.get(path, self._retrieval_limit)
        if isinstance(self._synopsis, SynopsisPathIndex):
            return self._synopsis.rank_many_adaptive(
                path,
                source_indices,
                limit=limit,
                candidate_batch_size=self._retrieval_batch_size,
                excluded_ids_by_source=excluded_ids_by_source,
            )
        return self._synopsis.rank_many_streaming(
            path,
            source_indices,
            limit=limit,
            candidate_batch_size=self._retrieval_batch_size,
            **({} if excluded_ids_by_source is None else {'excluded_ids_by_source': excluded_ids_by_source}),
        )

    def _path_results_for_row(
        self,
        row_number: int,
        *,
        weighted: tuple[PathScores, ...],
        categorical: Mapping[str, tuple[PathScores, ...]],
        streamed: Mapping[str, tuple[PathScores, ...]],
        affinity: Mapping[str, tuple[PathScores, ...]],
    ) -> list[tuple[str, PathScores]]:
        """Collect one source row's results in the canonical path order."""
        results: list[tuple[str, PathScores]] = []
        if 'weighted-v2' in self._enabled_paths:
            results.append(('weighted-v2', weighted[row_number]))
        results.extend(
            (name, categorical[name][row_number])
            for name in ('genres', 'themes', 'tags')
            if name in self._enabled_paths
        )
        results.extend((name, streamed[name][row_number]) for name in self._enabled_synopsis_paths)
        results.extend((name, affinity[name][row_number]) for name in self._affinity if name in self._enabled_paths)
        return results

    @staticmethod
    def _measure_path_timing(name: str, timings_ms: dict[str, float], operation: Callable[[], ResultT]) -> ResultT:
        started = perf_counter()
        result = operation()
        timings_ms[name] = (perf_counter() - started) * 1_000
        return result
