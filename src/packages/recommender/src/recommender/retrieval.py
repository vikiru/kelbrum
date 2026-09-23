"""Independent candidate retrieval and family-budget reduction."""

from collections.abc import Callable, Mapping, Sequence
from time import perf_counter
from typing import Protocol, TypeVar

import msgspec

from config import derive_payload_identity
from recommender.union import (
    AVAILABLE_RETRIEVAL_PATHS,
    DEFAULT_RETRIEVAL_FAMILY_BUDGET,
    PATH_FAMILIES,
    RETRIEVAL_PATH_ORDER,
    RETRIEVAL_REDUCER_POLICY,
    RetrievalDiagnostics,
    RetrievalFamilyBudget,
    RetrievalMode,
    reduce_path_results,
    validate_retrieval_paths,
)
from recommender.weighted_v2 import WeightedV2Index

PathScores = tuple[tuple[int, float], ...]
PathResults = tuple[tuple[str, PathScores], ...]
ResultT = TypeVar('ResultT')
SEMANTIC_PATHS = frozenset({'bm25', 'lsa', 'embedding'})


class BatchRanker(Protocol):
    def rank_many(self, source_indices: Sequence[int], *, limit: int) -> tuple[PathScores, ...]: ...


class StreamingRanker(Protocol):
    def rank_many_streaming(
        self,
        path: str,
        source_indices: Sequence[int],
        *,
        limit: int,
        candidate_batch_size: int,
    ) -> tuple[PathScores, ...]: ...


class RetrievalBatch(msgspec.Struct, frozen=True):
    """Reduced path evidence for each requested source row."""

    results: tuple[PathResults, ...]
    diagnostics: RetrievalDiagnostics


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
        mode: RetrievalMode,
        family_budget: RetrievalFamilyBudget = DEFAULT_RETRIEVAL_FAMILY_BUDGET,
        enabled_paths: Sequence[str] = AVAILABLE_RETRIEVAL_PATHS,
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
        self._mode = mode
        self._family_budget = family_budget
        self._enabled_paths = validate_retrieval_paths(enabled_paths)
        self._enabled_synopsis_paths = tuple(path for path in self._enabled_paths if path in SEMANTIC_PATHS)
        self._last_diagnostics = RetrievalDiagnostics(0, 0, 0, {})

    @property
    def last_diagnostics(self) -> RetrievalDiagnostics:
        """Return aggregate counts from the most recent retrieval batch."""
        return self._last_diagnostics

    @property
    def identity(self) -> str:
        """Return the deterministic identity of the active retrieval policy."""
        budget = self._family_budget
        return derive_payload_identity(
            {
                'policy': RETRIEVAL_REDUCER_POLICY,
                'mode': self._mode.value,
                'budgets': {
                    'semantic': budget.semantic,
                    'structured': budget.structured,
                    'neighbourhood': budget.neighbourhood,
                    'affinity': budget.affinity,
                },
                'path_order': RETRIEVAL_PATH_ORDER,
                'path_families': PATH_FAMILIES,
                'enabled_paths': self._enabled_paths,
                'retrieval_limit': self._retrieval_limit,
                'retrieval_batch_size': self._retrieval_batch_size,
            }
        )

    def retrieve(self, source_indices: Sequence[int]) -> RetrievalBatch:
        """Retrieve all active paths once per batch and apply configured reduction."""
        path_timings_ms: dict[str, float] = {}
        streamed = {
            name: self._time_path(
                name,
                path_timings_ms,
                lambda name=name: self._synopsis.rank_many_streaming(
                    name,
                    source_indices,
                    limit=self._retrieval_limit,
                    candidate_batch_size=self._retrieval_batch_size,
                ),
            )
            for name in self._enabled_synopsis_paths
        }
        weighted: tuple[PathScores, ...]
        if self._weighted is None:
            weighted = ()
        else:
            weighted_index = self._weighted
            weighted = self._time_path(
                'weighted-v2',
                path_timings_ms,
                lambda: weighted_index.rank_many_streaming(
                    source_indices,
                    limit=self._retrieval_limit,
                    candidate_batch_size=self._retrieval_batch_size,
                ),
            )
        categorical = self._rank_paths(self._categorical, source_indices, path_timings_ms)
        affinity = self._rank_paths(self._affinity, source_indices, path_timings_ms)

        results: list[PathResults] = []
        unbounded_count = 0
        reduced_count = 0
        family_counts = {'semantic': 0, 'structured': 0, 'neighbourhood': 0, 'affinity': 0}
        path_candidate_counts: dict[str, int] = {}
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
            reduced = reduce_path_results(path_results, mode=self._mode, budgets=self._family_budget)
            reduced_count += len({candidate_id for _, values in reduced for candidate_id, _ in values})
            for path, values in reduced:
                family_counts[PATH_FAMILIES[path]] += len(values)
            results.append(tuple(reduced))
        path_timings_ms['family_reduction'] = (perf_counter() - reduction_started) * 1_000
        batch = RetrievalBatch(
            tuple(results),
            RetrievalDiagnostics(
                len(source_indices),
                unbounded_count,
                reduced_count,
                family_counts,
                path_timings_ms,
                path_candidate_counts,
            ),
        )
        self._last_diagnostics = batch.diagnostics
        return batch

    def _rank_paths(
        self,
        indexes: Mapping[str, BatchRanker],
        source_indices: Sequence[int],
        timings_ms: dict[str, float],
    ) -> dict[str, tuple[PathScores, ...]]:
        """Rank each enabled structured path and record its timing."""
        return {
            name: self._time_path(
                name,
                timings_ms,
                lambda index=index: index.rank_many(source_indices, limit=self._retrieval_limit),
            )
            for name, index in indexes.items()
            if name in self._enabled_paths
        }

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
    def _time_path(name: str, timings_ms: dict[str, float], operation: Callable[[], ResultT]) -> ResultT:
        started = perf_counter()
        result = operation()
        timings_ms[name] = (perf_counter() - started) * 1_000
        return result
