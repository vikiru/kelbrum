"""Availability-aware weighted content similarity for recommender v2."""

from collections.abc import Mapping, Sequence
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cityblock, cosine, dice, jaccard

from features.blocks import FeatureBlock, FeatureBundle

V2_WEIGHTS: Mapping[str, float] = {
    'synopsis-tfidf': 0.25,
    'genres': 0.18,
    'themes': 0.12,
    'demographics': 0.05,
    'studios': 0.07,
    'anime_type': 0.06,
    'rating': 0.06,
    'source': 0.03,
    'year-bucket': 0.04,
    'episodes-bucket': 0.04,
    'duration-bucket': 0.04,
    'numeric': 0.06,
}
V2_METRICS: Mapping[str, str] = {
    'synopsis-tfidf': 'cosine',
    'synopsis-embedding': 'cosine',
    'genres': 'jaccard',
    'themes': 'jaccard',
    'demographics': 'jaccard',
    'studios': 'jaccard',
    'anime_type': 'dice',
    'rating': 'dice',
    'source': 'dice',
    'year-bucket': 'dice',
    'episodes-bucket': 'dice',
    'duration-bucket': 'dice',
    'numeric': 'manhattan',
}
CONTENT_BLOCKS = frozenset({'synopsis-tfidf', 'synopsis-embedding', 'genres', 'themes', 'studios'})
MIN_CONTENT_WEIGHT = 0.30


class WeightedV2Index:
    """Prepared vectorized index for weighted v2 content similarity."""

    def __init__(
        self,
        bundle: FeatureBundle,
        *,
        weights: Mapping[str, float] = V2_WEIGHTS,
        metrics: Mapping[str, str] = V2_METRICS,
    ) -> None:
        self.anime_ids = bundle.anime_ids.copy()
        self.weights = weights
        self.metrics = metrics
        self.blocks = {block.name: _PreparedBlock(block) for block in bundle.blocks if block.name in weights}

    def rank(
        self,
        source_index: int,
        *,
        limit: int = 10,
        candidate_mask: np.ndarray | None = None,
        require_semantic: bool = False,
        require_content: bool = True,
        renormalize_available: bool = True,
    ) -> tuple[tuple[int, float], ...]:
        """Return top candidates for one source row using vectorized block scoring."""
        if source_index < 0 or source_index >= self.anime_ids.size:
            raise IndexError('source row is outside the index')
        scores = np.zeros(self.anime_ids.size, dtype=np.float64)
        weight_totals = np.zeros(self.anime_ids.size, dtype=np.float64)
        content_weights = np.zeros(self.anime_ids.size, dtype=np.float64)
        source_weight_total = 0.0
        for name, weight in self.weights.items():
            block = self.blocks.get(name)
            if block is None or weight <= 0.0 or not block.row_available[source_index]:
                continue
            source_weight_total += weight
            usable = block.pair_available(source_index)
            values = block.similarities(source_index, self.metrics.get(name, 'cosine'))
            scores[usable] += weight * values[usable]
            weight_totals[usable] += weight
            if name in CONTENT_BLOCKS:
                content_weights[usable] += weight
        valid = weight_totals > 0.0
        if require_content:
            valid &= content_weights >= MIN_CONTENT_WEIGHT
        if require_semantic:
            semantic_blocks = [
                self.blocks[name].row_available
                for name in ('synopsis-embedding', 'synopsis-tfidf')
                if name in self.blocks
            ]
            if not semantic_blocks or not any(block[source_index] for block in semantic_blocks):
                return ()
            valid &= np.logical_or.reduce(semantic_blocks)
        if candidate_mask is not None:
            valid &= candidate_mask
        valid[source_index] = False
        denominators = weight_totals if renormalize_available else np.full_like(weight_totals, source_weight_total)
        scores[valid] /= denominators[valid]
        indices = np.flatnonzero(valid)
        if indices.size == 0:
            return ()
        selected = indices[np.argpartition(scores[indices], -min(limit, indices.size))[-min(limit, indices.size) :]]
        selected = selected[np.argsort(-scores[selected], kind='stable')]
        return tuple((int(self.anime_ids[index]), float(scores[index])) for index in selected)

    def rank_many_streaming(
        self,
        source_indices: Sequence[int],
        *,
        limit: int = 300,
        candidate_batch_size: int = 512,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        """Score source batches against bounded candidate blocks."""
        if candidate_batch_size < 1:
            raise ValueError('candidate_batch_size must be positive')
        sources = tuple(source_indices)
        if any(index < 0 or index >= self.anime_ids.size for index in sources):
            raise IndexError('source row is outside the weighted index')
        top_scores = np.full((len(sources), limit), -np.inf, dtype=np.float32)
        top_indices = np.full((len(sources), limit), -1, dtype=np.int32)
        for start in range(0, self.anime_ids.size, candidate_batch_size):
            stop = min(start + candidate_batch_size, self.anime_ids.size)
            block_scores = self._score_block_many(sources, start, stop)
            block_indices = np.arange(start, stop, dtype=np.int32)
            block_scores = block_scores.copy()
            for row_number, source_index in enumerate(sources):
                source_offset = source_index - start
                if 0 <= source_offset < block_scores.shape[1]:
                    block_scores[row_number, source_offset] = -np.inf
            block_count = min(limit, block_scores.shape[1])
            block_selection = np.argpartition(
                block_scores,
                -block_count,
                axis=1,
            )[:, -block_count:]
            block_top_scores = np.take_along_axis(block_scores, block_selection, axis=1)
            block_top_indices = block_indices[block_selection]
            combined_scores = np.concatenate((top_scores, block_top_scores), axis=1)
            combined_indices = np.concatenate((top_indices, block_top_indices), axis=1)
            selection = np.argpartition(combined_scores, -limit, axis=1)[:, -limit:]
            top_scores = np.take_along_axis(combined_scores, selection, axis=1)
            top_indices = np.take_along_axis(combined_indices, selection, axis=1)

        output: list[tuple[tuple[int, float], ...]] = []
        for row_number in range(len(sources)):
            valid = np.isfinite(top_scores[row_number])
            indices = top_indices[row_number, valid]
            scores = top_scores[row_number, valid]
            order = np.lexsort((indices, -scores))
            output.append(
                tuple(
                    (int(self.anime_ids[index]), float(scores[position]))
                    for position, index in zip(order, indices[order], strict=True)
                )
            )
        return tuple(output)

    def _score_block_many(self, source_indices: Sequence[int], start: int, stop: int) -> np.ndarray:
        scores = np.zeros((len(source_indices), stop - start), dtype=np.float64)
        totals = np.zeros_like(scores)
        content = np.zeros_like(scores)
        for name, weight in self.weights.items():
            block = self.blocks.get(name)
            if block is None or weight <= 0.0:
                continue
            source_available = block.row_available[list(source_indices)]
            if not np.any(source_available):
                continue
            values = block.similarities_many(source_indices, self.metrics.get(name, 'cosine'), start, stop)
            usable = block.pair_available_many(source_indices, start, stop)
            usable_values = usable & source_available[:, None]
            scores[usable_values] += weight * values[usable_values]
            totals[usable_values] += weight
            if name in CONTENT_BLOCKS:
                content[usable_values] += weight
        valid = (totals > 0.0) & (content >= MIN_CONTENT_WEIGHT)
        return np.divide(scores, totals, out=np.full_like(scores, -np.inf), where=valid).astype(np.float32)

    def _score_block(self, source_index: int, start: int, stop: int) -> np.ndarray:
        scores = np.zeros(stop - start, dtype=np.float64)
        totals = np.zeros(stop - start, dtype=np.float64)
        content = np.zeros(stop - start, dtype=np.float64)
        for name, weight in self.weights.items():
            block = self.blocks.get(name)
            if block is None or weight <= 0.0 or not block.row_available[source_index]:
                continue
            values = block.similarities(source_index, self.metrics.get(name, 'cosine'), start, stop)
            usable = block.pair_available(source_index, start, stop)
            scores[usable] += weight * values[usable]
            totals[usable] += weight
            if name in CONTENT_BLOCKS:
                content[usable] += weight
        valid = (totals > 0.0) & (content >= MIN_CONTENT_WEIGHT)
        return np.divide(scores, totals, out=np.full_like(scores, -np.inf), where=valid)


class _PreparedBlock:
    def __init__(self, block: FeatureBlock) -> None:
        self.values: csr_matrix | np.ndarray = (
            block.values if isinstance(block.values, csr_matrix) else np.asarray(block.values, dtype=np.float32)
        )
        self.row_available = np.asarray(block.availability(), dtype=bool).ravel()
        self.dimension_available = (
            np.asarray(block.dimension_available, dtype=bool) if block.dimension_available is not None else None
        )
        self.row_sizes = np.asarray(
            self.values.getnnz(axis=1)
            if isinstance(self.values, csr_matrix)
            else np.count_nonzero(self.values, axis=1),
            dtype=np.float64,
        ).ravel()

    def pair_available(self, source_index: int, start: int = 0, stop: int | None = None) -> np.ndarray:
        stop = self.values.shape[0] if stop is None else stop
        if self.dimension_available is None:
            return self.row_available[start:stop]
        shared = self.dimension_available[start:stop] & self.dimension_available[source_index]
        return shared.any(axis=1)

    def pair_available_many(self, source_indices: Sequence[int], start: int, stop: int) -> np.ndarray:
        if self.dimension_available is None:
            return np.broadcast_to(self.row_available[start:stop], (len(source_indices), stop - start))
        shared = self.dimension_available[list(source_indices), None, :] & self.dimension_available[None, start:stop, :]
        return shared.any(axis=2)

    def similarities(self, source_index: int, metric: str, start: int = 0, stop: int | None = None) -> np.ndarray:
        stop = self.values.shape[0] if stop is None else stop
        candidate_values = self.values[start:stop]
        candidate_sizes = self.row_sizes[start:stop]
        source = self.values.getrow(source_index) if isinstance(self.values, csr_matrix) else self.values[source_index]
        if isinstance(self.values, csr_matrix):
            c_mat = cast('csr_matrix', candidate_values)
            s_mat = cast('csr_matrix', source)
            intersections = np.asarray((c_mat @ s_mat.T).toarray()).ravel()
        else:
            intersections = candidate_values @ source
        if metric == 'jaccard':
            union = candidate_sizes + self.row_sizes[source_index] - intersections
            return np.divide(
                intersections, union, out=np.zeros_like(intersections, dtype=np.float64), where=union > 0.0
            )
        if metric == 'dice':
            denominator = candidate_sizes + self.row_sizes[source_index]
            return np.divide(
                2.0 * intersections,
                denominator,
                out=np.zeros_like(intersections, dtype=np.float64),
                where=denominator > 0.0,
            )
        if metric == 'manhattan':
            differences = np.abs(candidate_values - source)
            if self.dimension_available is not None:
                shared = self.dimension_available[start:stop] & self.dimension_available[source_index]
                differences = np.where(shared, differences, 0.0)
                means = np.divide(
                    differences.sum(axis=1),
                    shared.sum(axis=1),
                    out=np.zeros(stop - start),
                    where=shared.any(axis=1),
                )
                return np.divide(1.0, 1.0 + means, out=np.zeros(stop - start), where=shared.any(axis=1))
            return 1.0 / (1.0 + differences.mean(axis=1))
        if metric == 'cosine':
            source_norm = float(
                np.linalg.norm(cast('csr_matrix', source).toarray())
                if isinstance(self.values, csr_matrix)
                else np.linalg.norm(source)
            )
            values = (
                np.asarray((cast('csr_matrix', candidate_values) @ cast('csr_matrix', source).T).toarray()).ravel()
                if isinstance(self.values, csr_matrix)
                else candidate_values @ source
            )
            norms = (
                np.asarray(np.sqrt(self.values.multiply(self.values).sum(axis=1))).ravel()
                if isinstance(self.values, csr_matrix)
                else np.linalg.norm(self.values, axis=1)
            )
            norms = norms[start:stop]
            denominator = norms * source_norm
            return np.divide(values, denominator, out=np.zeros(stop - start), where=denominator > 0.0).ravel()
        raise ValueError(f'unsupported v2 similarity metric: {metric}')

    def similarities_many(
        self, source_indices: Sequence[int], metric: str, start: int = 0, stop: int | None = None
    ) -> np.ndarray:
        stop = self.values.shape[0] if stop is None else stop
        sources = self.values[list(source_indices)]
        candidates = self.values[start:stop]
        if isinstance(self.values, csr_matrix):
            c_mat = cast('csr_matrix', candidates)
            s_mat = cast('csr_matrix', sources)
            intersections = np.asarray((s_mat @ c_mat.T).toarray())
        else:
            dense_src = cast('np.ndarray', sources)
            dense_cand = cast('np.ndarray', candidates)
            intersections = np.asarray(dense_src @ dense_cand.T)
        candidate_sizes = self.row_sizes[start:stop]
        source_sizes = self.row_sizes[list(source_indices)]
        if metric == 'jaccard':
            union = source_sizes[:, None] + candidate_sizes[None, :] - intersections
            return np.divide(
                intersections, union, out=np.zeros_like(intersections, dtype=np.float64), where=union > 0.0
            )
        if metric == 'dice':
            denominator = source_sizes[:, None] + candidate_sizes[None, :]
            return np.divide(
                2.0 * intersections,
                denominator,
                out=np.zeros_like(intersections, dtype=np.float64),
                where=denominator > 0.0,
            )
        if metric == 'manhattan':
            if isinstance(self.values, csr_matrix):
                dense_sources = cast('csr_matrix', self.values[list(source_indices)]).toarray()
                dense_candidates = cast('csr_matrix', self.values[start:stop]).toarray()
            else:
                dense_sources = np.asarray(sources)
                dense_candidates = np.asarray(candidates)
            differences = np.abs(dense_sources[:, None, :] - dense_candidates[None, :, :])
            if self.dimension_available is not None:
                shared = (
                    self.dimension_available[list(source_indices)][:, None, :]
                    & self.dimension_available[start:stop][None, :, :]
                )
                counts = shared.sum(axis=2)
                means = np.divide(
                    np.where(shared, differences, 0.0).sum(axis=2),
                    counts,
                    out=np.zeros_like(counts, dtype=np.float64),
                    where=counts > 0,
                )
                return np.divide(1.0, 1.0 + means, out=np.zeros_like(means), where=counts > 0)
            return 1.0 / (1.0 + differences.mean(axis=2))
        if metric == 'cosine':
            if isinstance(self.values, csr_matrix):
                source_norms = np.asarray(np.linalg.norm(cast('csr_matrix', sources).toarray(), axis=1))
                candidate_norms = np.asarray(
                    np.sqrt(cast('csr_matrix', candidates).multiply(cast('csr_matrix', candidates)).sum(axis=1))
                ).ravel()
            else:
                source_norms = np.asarray(np.linalg.norm(cast('np.ndarray', sources), axis=1))
                candidate_norms = np.asarray(np.linalg.norm(cast('np.ndarray', candidates), axis=1))
            return np.divide(
                intersections,
                source_norms[:, None] * candidate_norms[None, :],
                out=np.zeros_like(intersections, dtype=np.float64),
                where=(source_norms[:, None] * candidate_norms[None, :]) > 0.0,
            )
        raise ValueError(f'unsupported v2 similarity metric: {metric}')

    def similarity(self, left_index: int, right_index: int, metric: str) -> float:
        """Calculate one pair score without materializing catalogue-wide scores."""
        left = self.values.getrow(left_index) if isinstance(self.values, csr_matrix) else self.values[left_index]
        right = self.values.getrow(right_index) if isinstance(self.values, csr_matrix) else self.values[right_index]
        if metric == 'cosine':
            left_array = left.toarray().ravel() if isinstance(left, csr_matrix) else left
            right_array = right.toarray().ravel() if isinstance(right, csr_matrix) else right
            denominator = np.linalg.norm(left_array) * np.linalg.norm(right_array)
            return float(np.dot(left_array, right_array) / denominator) if denominator else 0.0
        if metric == 'jaccard':
            left_array = left.toarray().ravel() if isinstance(left, csr_matrix) else left
            right_array = right.toarray().ravel() if isinstance(right, csr_matrix) else right
            return float(1.0 - jaccard(left_array > 0, right_array > 0))
        if metric == 'dice':
            left_array = left.toarray().ravel() if isinstance(left, csr_matrix) else left
            right_array = right.toarray().ravel() if isinstance(right, csr_matrix) else right
            return float(1.0 - dice(left_array > 0, right_array > 0))
        if metric == 'manhattan':
            left_array = left.toarray().ravel() if isinstance(left, csr_matrix) else left
            right_array = right.toarray().ravel() if isinstance(right, csr_matrix) else right
            differences = np.abs(left_array - right_array)
            if self.dimension_available is not None:
                shared = self.dimension_available[left_index] & self.dimension_available[right_index]
                distance = _masked_numeric_distance(left_array, right_array, shared)
                return float(1.0 / (1.0 + distance)) if distance is not None else 0.0
            return float(1.0 / (1.0 + differences.mean()))
        raise ValueError(f'unsupported v2 similarity metric: {metric}')


def weighted_distance(
    bundle: FeatureBundle,
    left_index: int,
    right_index: int,
    *,
    weights: Mapping[str, float] = V2_WEIGHTS,
    metrics: Mapping[str, str] = V2_METRICS,
) -> float:
    """Return pairwise weighted cosine distance with availability renormalization."""
    if left_index < 0 or right_index < 0 or left_index >= bundle.anime_ids.size or right_index >= bundle.anime_ids.size:
        raise IndexError('feature row is outside the bundle')
    if any(weight < 0.0 for weight in weights.values()) or not any(weights.values()):
        raise ValueError('weights must contain at least one positive, non-negative value')
    blocks = {block.name: block for block in bundle.blocks}
    available: list[tuple[float, float]] = []
    content_weight = 0.0
    for name, weight in weights.items():
        block = blocks.get(name)
        if block is None or weight == 0.0:
            continue
        left = _row(block, left_index)
        right = _row(block, right_index)
        if _is_unavailable(left) or _is_unavailable(right):
            continue
        if name == 'numeric' and block.dimension_available is not None:
            numeric_distance = _masked_numeric_distance(
                left,
                right,
                block.dimension_available[left_index] & block.dimension_available[right_index],
            )
            if numeric_distance is None:
                continue
            distance = numeric_distance
        else:
            distance = _distance(left, right, metrics.get(name, 'cosine'))
        if name in CONTENT_BLOCKS:
            content_weight += weight
        available.append((weight, distance))
    total_weight = sum(weight for weight, _ in available)
    if total_weight == 0.0 or content_weight < MIN_CONTENT_WEIGHT:
        raise ValueError('anime pair has no comparable feature families')
    return float(sum(weight * distance for weight, distance in available) / total_weight)


def _row(block: FeatureBlock, index: int) -> np.ndarray:
    value = block.values[index]
    return value.toarray().ravel() if isinstance(value, csr_matrix) else np.asarray(value, dtype=np.float64).ravel()


def _is_unavailable(value: np.ndarray) -> bool:
    return value.size == 0 or not np.any(value)


def _distance(left: np.ndarray, right: np.ndarray, metric: str) -> float:
    if metric == 'jaccard':
        return float(jaccard(left > 0, right > 0))
    if metric == 'dice':
        return float(dice(left > 0, right > 0))
    if metric == 'manhattan':
        return float(cityblock(left, right) / left.size)
    if metric != 'cosine':
        raise ValueError(f'unsupported v2 similarity metric: {metric}')
    return float(cosine(left, right))


def _masked_numeric_distance(left: np.ndarray, right: np.ndarray, shared_dimensions: NDArray[np.bool_]) -> float | None:
    """Return numeric Manhattan distance over jointly observed dimensions."""
    if not shared_dimensions.any():
        return None
    return float(np.abs(left[shared_dimensions] - right[shared_dimensions]).mean())
