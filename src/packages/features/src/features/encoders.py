"""Feature encoders for categorical, set-valued, text, and episode data."""

from collections import Counter
from collections.abc import Iterable, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

from normalization.encoders import bucketize, clean_labels, multi_hot
from normalization.scalers import log1p


def episode_buckets(
    episodes: Sequence[int | None],
    *,
    boundaries: tuple[int, ...] = (1, 12, 17, 29, 51, 101, 301, 500),
) -> tuple[csr_matrix, tuple[str, ...]]:
    """Encode episode counts using configurable inclusive lower bounds."""
    if not boundaries or boundaries[0] != 1 or tuple(sorted(boundaries)) != boundaries:
        raise ValueError('episode boundaries must be sorted and start at 1')
    return bucketize(episodes, boundaries=boundaries, missing_below=1)


def year_buckets(
    years: Sequence[int | None],
    *,
    boundaries: tuple[int, ...] = (1917, 1980, 1992, 2008, 2016, 2021, 2025),
) -> tuple[csr_matrix, tuple[str, ...]]:
    """Encode release years into configurable inclusive ranges."""
    if not boundaries or tuple(sorted(boundaries)) != boundaries:
        raise ValueError('year boundaries must be sorted and non-empty')
    return bucketize(years, boundaries=boundaries, missing_below=boundaries[0])


def year_continuous(years: Sequence[int | None], *, minimum: int = 1917, maximum: int = 2027) -> NDArray[np.float32]:
    """Return bounded year values while preserving missing years as NaN."""
    if minimum >= maximum:
        raise ValueError('minimum year must be less than maximum year')
    values = np.asarray([float(year) if year is not None else np.nan for year in years], dtype=np.float32)
    return np.asarray(np.clip((values - minimum) / (maximum - minimum), 0.0, 1.0), dtype=np.float32)


def episode_log1p(episodes: Sequence[int | None]) -> NDArray[np.float64]:
    """Return log1p episode counts while preserving missing values as NaN."""
    values = np.asarray([float(count) if count is not None and count >= 0 else np.nan for count in episodes])
    present = np.isfinite(values)
    output = np.full(values.shape, np.nan, dtype=np.float64)
    output[present] = log1p(values[present]).ravel()
    return output


def studio_multi_hot(
    studios: Iterable[Iterable[str]], *, minimum_frequency: int = 3
) -> tuple[csr_matrix, tuple[str, ...]]:
    """Build an opt-in studio block while pruning rare studios."""
    rows = [clean_labels(row) for row in studios]
    frequencies = Counter(studio for row in rows for studio in row)
    retained = [tuple(studio for studio in row if frequencies[studio] >= minimum_frequency) for row in rows]
    return multi_hot(retained)


def studio_frequency(studios: Iterable[Iterable[str]]) -> NDArray[np.float32]:
    """Return the number of catalogue titles associated with each anime's studios."""
    rows = [set(clean_labels(row)) for row in studios]
    frequencies = Counter(studio for row in rows for studio in row)
    return np.asarray([sum(frequencies[studio] for studio in row) for row in rows], dtype=np.float32)


def studio_quality_features(
    studios: Iterable[Iterable[str]],
    scores: Sequence[float | None],
    ranks: Sequence[float | None],
) -> NDArray[np.float32]:
    """Return optional studio median score/rank and title-count features.

    Aggregates are computed from the supplied catalogue only. Missing values remain NaN
    so the owning feature policy can choose an appropriate imputation strategy.
    """
    rows = [set(clean_labels(row)) for row in studios]
    if len(rows) != len(scores) or len(rows) != len(ranks):
        raise ValueError('studios, scores, and ranks must have the same length')
    score_by_studio: dict[str, list[float]] = {}
    rank_by_studio: dict[str, list[float]] = {}
    for row, score, rank in zip(rows, scores, ranks, strict=True):
        for studio in row:
            if score is not None:
                score_by_studio.setdefault(studio, []).append(score)
            if rank is not None:
                rank_by_studio.setdefault(studio, []).append(rank)
    output = np.full((len(rows), 3), np.nan, dtype=np.float32)
    for index, row in enumerate(rows):
        score_values = [value for studio in row for value in score_by_studio.get(studio, [])]
        rank_values = [value for studio in row for value in rank_by_studio.get(studio, [])]
        if score_values:
            output[index, 0] = np.median(score_values)
        if rank_values:
            output[index, 1] = np.median(rank_values)
        output[index, 2] = sum(len(score_by_studio.get(studio, [])) for studio in row)
    return output
