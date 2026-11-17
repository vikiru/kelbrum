"""Typed metric names shared by recommendation calculations."""

from collections.abc import Callable, Iterable, Mapping, Sequence
from enum import StrEnum

import msgspec
import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix


class Similarity(StrEnum):
    """Higher-is-better metrics used by recommendation scoring."""

    COSINE = 'cosine'
    JACCARD = 'jaccard'
    DICE = 'dice'
    TVERSKY = 'tversky'
    MANHATTAN = 'manhattan'


class Distance(StrEnum):
    """Lower-is-better counterparts useful for diagnostic calculations."""

    COSINE = 'cosine'
    JACCARD = 'jaccard'
    DICE = 'dice'
    MANHATTAN = 'manhattan'


SimilarityName = Similarity | str
TVERSKY_ALPHA = 0.7
TVERSKY_BETA = 0.3


class SimilarityOperands(msgspec.Struct, frozen=True):
    """Prepared scalar or pairwise operands shared by metric strategies."""

    intersections: np.ndarray | None = None
    left_sizes: np.ndarray | float | None = None
    right_sizes: np.ndarray | float | None = None
    left_norms: np.ndarray | float | None = None
    right_norms: np.ndarray | float | None = None
    differences: np.ndarray | None = None
    shared: np.ndarray | None = None


class SimilarityMetric:
    """Scalar/vectorized implementation and availability metadata for a metric."""

    def __init__(
        self,
        identity: str,
        availability: str,
        scalar: Callable[[NDArray[np.floating], NDArray[np.floating]], float],
        vectorized: Callable[[SimilarityOperands], np.ndarray],
    ) -> None:
        self.identity = identity
        self.availability = availability
        self.scalar = scalar
        self.vectorized = vectorized


def similarity_score(left: NDArray[np.floating], right: NDArray[np.floating], metric: SimilarityName) -> float:
    """Return one higher-is-better score for two dense feature rows."""
    return SIMILARITY_REGISTRY[_coerce_similarity(metric)].scalar(left, right)


def vectorized_similarity(metric: SimilarityName, operands: SimilarityOperands) -> np.ndarray:
    """Apply one registered metric to prepared pairwise operands."""
    return SIMILARITY_REGISTRY[_coerce_similarity(metric)].vectorized(operands)


def distance_to_similarity(distance: float, metric: SimilarityName) -> float:
    """Convert a supported lower-is-better distance into a similarity score."""
    if _coerce_similarity(metric) is not Similarity.MANHATTAN:
        raise ValueError(f'unsupported distance metric: {metric}')
    return 1.0 / (1.0 + distance)


def _cosine_score(left: NDArray[np.floating], right: NDArray[np.floating]) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(left, right) / denominator)


def _binary_score(left: NDArray[np.floating], right: NDArray[np.floating], metric: Similarity) -> float:
    left_valid = left > 0
    right_valid = right > 0
    intersection = float(np.count_nonzero(left_valid & right_valid))
    if metric is Similarity.JACCARD:
        denominator = float(np.count_nonzero(left_valid | right_valid))
        return intersection / denominator if denominator else 0.0
    denominator = float(np.count_nonzero(left_valid) + np.count_nonzero(right_valid))
    return 2.0 * intersection / denominator if denominator else 0.0


def _jaccard_score(left: NDArray[np.floating], right: NDArray[np.floating]) -> float:
    """Return binary Jaccard similarity for two feature rows."""
    return _binary_score(left, right, Similarity.JACCARD)


def _dice_score(left: NDArray[np.floating], right: NDArray[np.floating]) -> float:
    """Return binary Dice similarity for two feature rows."""
    return _binary_score(left, right, Similarity.DICE)


def _tversky_score(left: NDArray[np.floating], right: NDArray[np.floating]) -> float:
    left_valid = left > 0
    right_valid = right > 0
    intersection = float(np.count_nonzero(left_valid & right_valid))
    left_only = float(np.count_nonzero(left_valid & ~right_valid))
    right_only = float(np.count_nonzero(right_valid & ~left_valid))
    denominator = intersection + TVERSKY_ALPHA * left_only + TVERSKY_BETA * right_only
    return intersection / denominator if denominator else 0.0


def tversky(
    source: frozenset[str] | set[str],
    candidate: frozenset[str] | set[str],
    *,
    alpha: float = TVERSKY_ALPHA,
    beta: float = TVERSKY_BETA,
) -> float:
    """Return asymmetric Tversky similarity for two categorical sets."""
    intersection = len(source & candidate)
    denominator = intersection + alpha * len(source - candidate) + beta * len(candidate - source)
    return intersection / denominator if denominator else 0.0


def idf_tversky(
    source: frozenset[str] | set[str],
    candidate: Sequence[str] | frozenset[str] | set[str] | None,
    *,
    alpha: float = 0.8,
    beta: float = 0.2,
    idf_map: Mapping[str, float] | None = None,
) -> float:
    """Return IDF-weighted asymmetric Tversky similarity for categorical labels."""
    if not source or not candidate:
        return 0.0
    c_set = candidate if isinstance(candidate, (frozenset, set)) else frozenset(candidate)
    s_set = source if isinstance(source, (frozenset, set)) else frozenset(source)

    inter = s_set & c_set
    if not inter:
        return 0.0
    if idf_map is None:
        inter_w = float(len(inter))
        source_only_w = float(len(s_set) - len(inter))
        cand_only_w = float(len(c_set) - len(inter))
    else:
        get_w = idf_map.get
        inter_w = sum(get_w(term, 1.0) for term in inter)
        source_only_w = sum(get_w(term, 1.0) for term in (s_set - inter))
        cand_only_w = sum(get_w(term, 1.0) for term in (c_set - inter))
    denominator = inter_w + alpha * source_only_w + beta * cand_only_w
    return inter_w / denominator if denominator else 0.0


def build_idf_csr(
    label_lists: Sequence[Iterable[str]],
    idf_map: Mapping[str, float] | None = None,
) -> tuple['csr_matrix', dict[str, int], NDArray[np.float64]]:
    """Build a row-aligned CSR matrix of IDF weights and per-row total weights."""
    vocab: dict[str, int] = {}
    indptr = [0]
    indices: list[int] = []
    data: list[float] = []
    row_totals = np.zeros(len(label_lists), dtype=np.float64)
    get_w = idf_map.get if idf_map is not None else None
    for row_idx, labels in enumerate(label_lists):
        seen: set[int] = set()
        total = 0.0
        for label in labels:
            col = vocab.get(label)
            if col is None:
                col = len(vocab)
                vocab[label] = col
            if col not in seen:
                seen.add(col)
                w = float(get_w(label, 1.0)) if get_w is not None else 1.0
                indices.append(col)
                data.append(w)
                total += w
        row_totals[row_idx] = total
        indptr.append(len(indices))
    mat = csr_matrix(
        (np.array(data, dtype=np.float64), np.array(indices, dtype=np.int32), np.array(indptr, dtype=np.int32)),
        shape=(len(label_lists), len(vocab)),
    )
    return mat, vocab, row_totals


def _manhattan_score(left: NDArray[np.floating], right: NDArray[np.floating]) -> float:
    """Return Manhattan distance converted to a higher-is-better score."""
    diffs = np.abs(left - right)
    distance = float(diffs.mean()) if diffs.size else 0.0
    return distance_to_similarity(distance, Similarity.MANHATTAN)


def _vectorized_set_similarity(operands: SimilarityOperands, metric: Similarity) -> np.ndarray:
    intersections = _required(operands.intersections, 'intersections')
    left_sizes = _required(operands.left_sizes, 'left_sizes')
    right_sizes = _required(operands.right_sizes, 'right_sizes')
    if metric is Similarity.JACCARD:
        numerator = intersections
        denominator = left_sizes + right_sizes - intersections
    else:
        numerator = 2.0 * intersections
        denominator = left_sizes + right_sizes
    return np.divide(numerator, denominator, out=np.zeros_like(intersections), where=denominator > 0.0)


def _vectorized_jaccard(operands: SimilarityOperands) -> np.ndarray:
    """Return pairwise Jaccard scores from prepared set operands."""
    return _vectorized_set_similarity(operands, Similarity.JACCARD)


def _vectorized_dice(operands: SimilarityOperands) -> np.ndarray:
    """Return pairwise Dice scores from prepared set operands."""
    return _vectorized_set_similarity(operands, Similarity.DICE)


def _vectorized_tversky(operands: SimilarityOperands) -> np.ndarray:
    intersections = _required(operands.intersections, 'intersections')
    left_sizes = _required(operands.left_sizes, 'left_sizes')
    right_sizes = _required(operands.right_sizes, 'right_sizes')
    denominator = (
        intersections + TVERSKY_ALPHA * (left_sizes - intersections) + TVERSKY_BETA * (right_sizes - intersections)
    )
    return np.divide(intersections, denominator, out=np.zeros_like(intersections), where=denominator > 0.0)


def _vectorized_cosine(operands: SimilarityOperands) -> np.ndarray:
    intersections = _required(operands.intersections, 'intersections')
    denominator = _required(operands.left_norms, 'left_norms') * _required(operands.right_norms, 'right_norms')
    return np.divide(intersections, denominator, out=np.zeros_like(intersections), where=denominator > 0.0)


def _vectorized_manhattan(operands: SimilarityOperands) -> np.ndarray:
    differences = _required(operands.differences, 'differences')
    if operands.shared is None:
        return 1.0 / (1.0 + differences.mean(axis=-1))
    counts = operands.shared.sum(axis=-1)
    means = np.divide(
        np.where(operands.shared, differences, 0.0).sum(axis=-1),
        counts,
        out=np.zeros_like(counts, dtype=np.float64),
        where=counts > 0,
    )
    return np.divide(1.0, 1.0 + means, out=np.zeros_like(means), where=counts > 0)


def _required(value: np.ndarray | float | None, name: str) -> np.ndarray:
    if value is None:
        raise ValueError(f'similarity operands require {name}')
    return np.asarray(value)


SIMILARITY_REGISTRY: dict[Similarity, SimilarityMetric] = {
    Similarity.COSINE: SimilarityMetric('cosine-v1', 'row', _cosine_score, _vectorized_cosine),
    Similarity.JACCARD: SimilarityMetric(
        'jaccard-v1',
        'row',
        _jaccard_score,
        _vectorized_jaccard,
    ),
    Similarity.DICE: SimilarityMetric(
        'dice-v1',
        'row',
        _dice_score,
        _vectorized_dice,
    ),
    Similarity.TVERSKY: SimilarityMetric(
        'tversky-v1',
        'row',
        _tversky_score,
        _vectorized_tversky,
    ),
    Similarity.MANHATTAN: SimilarityMetric(
        'manhattan-v1',
        'shared-dimensions',
        _manhattan_score,
        _vectorized_manhattan,
    ),
}


def _coerce_similarity(metric: SimilarityName) -> Similarity:
    try:
        return Similarity(metric)
    except ValueError as error:
        raise ValueError(f'unsupported similarity metric: {metric}') from error
