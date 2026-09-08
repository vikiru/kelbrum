"""Compare recommendation strategies on a shared evaluation request."""

from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path

import msgspec

from models.contracts import RecommendationConfig, RecommendationItem, RecommendationResult
from storage.json_io import write_json

MAX_COMPARISON_RECOMMENDATIONS = 100


class StrategyComparison(msgspec.Struct, frozen=True):
    overlap_count: int
    overlap_rate: float
    first_only_count: int
    second_only_count: int
    first_mean_score: float
    second_mean_score: float


StrategyRunner = Callable[[int, RecommendationConfig], RecommendationResult]


class StrategyRun(msgspec.Struct, frozen=True):
    source_anime_id: int
    results: tuple[tuple[str, RecommendationResult], ...]
    comparisons: tuple[tuple[str, str, StrategyComparison], ...]


def compare_recommendations(
    first: Sequence[RecommendationItem], second: Sequence[RecommendationItem]
) -> StrategyComparison:
    """Compare two ranked recommendation lists by IDs and scores."""
    first_scores = {item.anime_id: item.score for item in first}
    second_scores = {item.anime_id: item.score for item in second}
    overlap = set(first_scores) & set(second_scores)
    denominator = max(len(first_scores), len(second_scores), 1)
    return StrategyComparison(
        overlap_count=len(overlap),
        overlap_rate=len(overlap) / denominator,
        first_only_count=len(first_scores - second_scores.keys()),
        second_only_count=len(second_scores - first_scores.keys()),
        first_mean_score=_mean(first_scores.values()),
        second_mean_score=_mean(second_scores.values()),
    )


def write_comparison_report(path: str, *, report: Mapping[str, object]) -> None:
    """Persist a compact comparison report through the shared JSON adapter."""
    write_json(Path(path), dict(report))


def compare_strategies(
    anime_ids: Iterable[int],
    strategies: Mapping[str, StrategyRunner],
    *,
    config: RecommendationConfig | None = None,
) -> tuple[StrategyRun, ...]:
    """Run every named strategy for each anime and compare its top results."""
    active_config = config or RecommendationConfig(limit=MAX_COMPARISON_RECOMMENDATIONS)
    if active_config.limit > MAX_COMPARISON_RECOMMENDATIONS:
        raise ValueError(f'strategy comparisons support at most {MAX_COMPARISON_RECOMMENDATIONS} recommendations')
    if not strategies:
        raise ValueError('at least one recommendation strategy is required')
    ordered_strategies = tuple(sorted(strategies.items()))
    runs: list[StrategyRun] = []
    for anime_id in anime_ids:
        results = tuple((name, runner(anime_id, active_config)) for name, runner in ordered_strategies)
        comparisons = tuple(
            (first_name, second_name, compare_recommendations(first.items, second.items))
            for index, (first_name, first) in enumerate(results)
            for second_name, second in results[index + 1 :]
        )
        runs.append(StrategyRun(anime_id, results, comparisons))
    return tuple(runs)


def _mean(values: Iterable[float]) -> float:
    values = tuple(values)
    return sum(values) / len(values) if values else 0.0
