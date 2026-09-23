"""Availability-aware weighted content similarity for recommender v2."""

from collections.abc import Mapping, Sequence
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

from features.blocks import AvailabilityPolicy, FeatureBlock, FeatureBundle
from recommender.metrics import (
    Similarity,
    SimilarityName,
    SimilarityOperands,
    distance_to_similarity,
    similarity_score,
    vectorized_similarity,
)
from recommender.properties import SimilarityProperty, default_similarity_properties

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
V2_METRICS: Mapping[str, Similarity] = {
    'synopsis-tfidf': Similarity.COSINE,
    'synopsis-embedding': Similarity.COSINE,
    'genres': Similarity.JACCARD,
    'themes': Similarity.JACCARD,
    'demographics': Similarity.JACCARD,
    'studios': Similarity.JACCARD,
    'anime_type': Similarity.DICE,
    'rating': Similarity.DICE,
    'source': Similarity.DICE,
    'year-bucket': Similarity.DICE,
    'episodes-bucket': Similarity.DICE,
    'duration-bucket': Similarity.DICE,
    'numeric': Similarity.MANHATTAN,
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
        metrics: Mapping[str, SimilarityName] = V2_METRICS,
        properties: Sequence[SimilarityProperty] | None = None,
        availability_policy: AvailabilityPolicy | None = None,
    ) -> None:
        self.anime_ids = bundle.anime_ids.copy()
        self.properties = (
            tuple(properties)
            if properties is not None
            else default_similarity_properties(dict(weights), dict(metrics), CONTENT_BLOCKS)
        )
        _validate_similarity_properties(self.properties)
        self.weights = {property_spec.name: property_spec.weight for property_spec in self.properties}
        self.metrics = {property_spec.name: property_spec.metric for property_spec in self.properties}
        property_names = frozenset(self.weights)
        self.blocks = {
            block.name: _PreparedBlock(block, availability_policy)
            for block in bundle.blocks
            if block.name in property_names
        }

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
        _validate_limit(limit)
        _validate_source_indices((source_index,), self.anime_ids.size)
        _validate_candidate_mask(candidate_mask, self.anime_ids.shape)
        scores = np.zeros(self.anime_ids.size, dtype=np.float64)
        weight_totals = np.zeros(self.anime_ids.size, dtype=np.float64)
        content_weights = np.zeros(self.anime_ids.size, dtype=np.float64)
        source_weight_total = 0.0
        for property_spec in self.properties:
            name = property_spec.name
            weight = property_spec.weight
            block = self.blocks.get(name)
            if block is None or weight <= 0.0 or not block.row_available[source_index]:
                continue
            source_weight_total += weight
            usable = block.pair_available(source_index)
            values = block.similarities(source_index, property_spec.metric)
            scores[usable] += weight * values[usable]
            weight_totals[usable] += weight
            if property_spec.contributes_to_content:
                content_weights[usable] += weight
        valid = self._valid_candidates(
            source_index,
            weight_totals,
            content_weights,
            candidate_mask,
            require_content,
            require_semantic,
        )
        if valid is None:
            return ()
        denominators = weight_totals if renormalize_available else np.full_like(weight_totals, source_weight_total)
        scores[valid] /= denominators[valid]
        valid &= np.isfinite(scores) & (scores > 0.0)
        indices = np.flatnonzero(valid)
        if indices.size == 0:
            return ()
        selected_positions = _select_top_indices(indices, scores[indices], limit, self.anime_ids)
        selected = indices[selected_positions]
        return tuple((int(self.anime_ids[index]), float(scores[index])) for index in selected)

    def _valid_candidates(
        self,
        source_index: int,
        weight_totals: np.ndarray,
        content_weights: np.ndarray,
        candidate_mask: np.ndarray | None,
        require_content: bool,
        require_semantic: bool,
    ) -> np.ndarray | None:
        """Build the candidate mask shared by rank's eligibility rules."""
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
                return None
            valid &= np.logical_or.reduce(semantic_blocks)
        if candidate_mask is not None:
            valid &= candidate_mask
        valid[source_index] = False
        return valid

    def rank_many_streaming(
        self,
        source_indices: Sequence[int],
        *,
        limit: int = 300,
        candidate_batch_size: int = 512,
        candidate_mask: np.ndarray | None = None,
        require_semantic: bool = False,
        require_content: bool = True,
        renormalize_available: bool = True,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        """Score source batches against bounded candidate blocks."""
        _validate_limit(limit)
        if candidate_batch_size < 1:
            raise ValueError('candidate_batch_size must be positive')
        sources = tuple(source_indices)
        _validate_source_indices(sources, self.anime_ids.size)
        _validate_candidate_mask(candidate_mask, self.anime_ids.shape)
        source_weights = self._source_weight_totals(sources)
        semantic_candidates = self._semantic_candidates(sources, require_semantic)
        top_scores = np.full((len(sources), limit), -np.inf, dtype=np.float32)
        top_indices = np.full((len(sources), limit), -1, dtype=np.int32)
        for start in range(0, self.anime_ids.size, candidate_batch_size):
            stop = min(start + candidate_batch_size, self.anime_ids.size)
            block_scores = self._score_block_many(
                sources,
                start,
                stop,
                candidate_mask,
                semantic_candidates,
                require_content,
                renormalize_available,
                source_weights,
            )
            block_indices = np.arange(start, stop, dtype=np.int32)
            for row_number, source_index in enumerate(sources):
                source_offset = source_index - start
                if 0 <= source_offset < block_scores.shape[1]:
                    block_scores[row_number, source_offset] = -np.inf
            for row_number in range(len(sources)):
                block_selection = _select_top_indices(
                    np.arange(start, stop, dtype=np.int32),
                    block_scores[row_number],
                    limit,
                    self.anime_ids,
                )
                combined_scores = np.concatenate((top_scores[row_number], block_scores[row_number, block_selection]))
                combined_indices = np.concatenate((top_indices[row_number], block_indices[block_selection]))
                selection = _select_top_indices(combined_indices, combined_scores, limit, self.anime_ids)
                top_scores[row_number] = -np.inf
                top_indices[row_number] = -1
                top_scores[row_number, : len(selection)] = combined_scores[selection]
                top_indices[row_number, : len(selection)] = combined_indices[selection]

        output: list[tuple[tuple[int, float], ...]] = []
        for row_number in range(len(sources)):
            valid = np.isfinite(top_scores[row_number])
            indices = top_indices[row_number, valid]
            scores = top_scores[row_number, valid]
            order = np.lexsort((self.anime_ids[indices], -scores))
            output.append(
                tuple(
                    (int(self.anime_ids[index]), float(scores[position]))
                    for position, index in zip(order, indices[order], strict=True)
                )
            )
        return tuple(output)

    def _source_weight_totals(self, source_indices: Sequence[int]) -> np.ndarray:
        source_rows = list(source_indices)
        totals = np.zeros(len(source_rows), dtype=np.float64)
        for property_spec in self.properties:
            block = self.blocks.get(property_spec.name)
            if block is not None:
                totals += property_spec.weight * block.row_available[source_rows]
        return totals

    def _semantic_candidates(self, source_indices: Sequence[int], required: bool) -> np.ndarray | None:
        if not required:
            return None
        semantic_blocks = [
            self.blocks[name].row_available for name in ('synopsis-embedding', 'synopsis-tfidf') if name in self.blocks
        ]
        if not semantic_blocks:
            return np.zeros(len(source_indices), dtype=bool)
        available = np.logical_or.reduce(semantic_blocks)
        return available[list(source_indices)]

    def _score_block_many(
        self,
        source_indices: Sequence[int],
        start: int,
        stop: int,
        candidate_mask: np.ndarray | None,
        semantic_candidates: np.ndarray | None,
        require_content: bool,
        renormalize_available: bool,
        source_weights: np.ndarray,
    ) -> np.ndarray:
        scores = np.zeros((len(source_indices), stop - start), dtype=np.float64)
        totals = np.zeros_like(scores)
        content = np.zeros_like(scores)
        for property_spec in self.properties:
            name = property_spec.name
            weight = property_spec.weight
            block = self.blocks.get(name)
            if block is None or weight <= 0.0:
                continue
            source_available = block.row_available[list(source_indices)]
            if not np.any(source_available):
                continue
            values = block.similarities_many(source_indices, property_spec.metric, start, stop)
            usable = block.pair_available_many(source_indices, start, stop)
            usable_values = usable & source_available[:, None]
            scores[usable_values] += weight * values[usable_values]
            totals[usable_values] += weight
            if property_spec.contributes_to_content:
                content[usable_values] += weight
        valid = totals > 0.0
        if require_content:
            valid &= content >= MIN_CONTENT_WEIGHT
        if semantic_candidates is not None:
            valid &= semantic_candidates[:, None]
            semantic_blocks = [
                self.blocks[name].row_available[start:stop]
                for name in ('synopsis-embedding', 'synopsis-tfidf')
                if name in self.blocks
            ]
            if semantic_blocks:
                valid &= np.logical_or.reduce(semantic_blocks)[None, :]
        if candidate_mask is not None:
            valid &= candidate_mask[start:stop][None, :]
        valid &= np.isfinite(scores) & (scores > 0.0)
        denominators = totals if renormalize_available else source_weights[:, None]
        return np.divide(scores, denominators, out=np.full_like(scores, -np.inf), where=valid).astype(np.float32)


def _validate_limit(limit: int) -> None:
    if limit < 1:
        raise ValueError('limit must be positive')


def _validate_source_indices(source_indices: Sequence[int], catalogue_size: int) -> None:
    if any(index < 0 or index >= catalogue_size for index in source_indices):
        raise IndexError('source row is outside the index')


def _validate_candidate_mask(candidate_mask: np.ndarray | None, expected_shape: tuple[int, ...]) -> None:
    if candidate_mask is not None and candidate_mask.shape != expected_shape:
        raise ValueError('candidate mask must align with the weighted index')


def _select_top_indices(
    candidate_indices: NDArray[np.integer],
    scores: NDArray[np.floating],
    limit: int,
    anime_ids: NDArray[np.integer],
) -> NDArray[np.integer]:
    """Select top scores using anime ID as the deterministic tie-breaker."""
    valid = np.isfinite(scores) & (scores > 0.0) & (candidate_indices >= 0)
    positions = np.flatnonzero(valid)
    candidates = candidate_indices[valid]
    candidate_scores = scores[valid]
    if candidates.size <= limit:
        return positions[np.lexsort((anime_ids[candidates], -candidate_scores))]

    threshold = np.partition(candidate_scores, -limit)[-limit]
    above = positions[candidate_scores > threshold]
    tied = positions[candidate_scores == threshold]
    remaining = limit - above.size
    tied = tied[np.argsort(anime_ids[candidate_indices[tied]], kind='stable')[:remaining]]
    selected = np.concatenate((above, tied))
    selected_scores = scores[selected]
    return selected[np.lexsort((anime_ids[candidate_indices[selected]], -selected_scores))]


class _PreparedBlock:
    def __init__(self, block: FeatureBlock, availability_policy: AvailabilityPolicy | None = None) -> None:
        self.values: csr_matrix | np.ndarray = (
            block.values if isinstance(block.values, csr_matrix) else np.asarray(block.values, dtype=np.float32)
        )
        self.row_available = np.asarray(block.availability(availability_policy), dtype=bool).ravel()
        self.dimension_available = (
            np.asarray(block.dimension_available, dtype=bool) if block.dimension_available is not None else None
        )
        self.row_sizes = np.asarray(
            self.values.getnnz(axis=1)
            if isinstance(self.values, csr_matrix)
            else np.count_nonzero(self.values, axis=1),
            dtype=np.float64,
        ).ravel()
        self.row_norms = (
            np.asarray(np.sqrt(self.values.multiply(self.values).sum(axis=1))).ravel()
            if isinstance(self.values, csr_matrix)
            else np.linalg.norm(self.values, axis=1)
        )

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

    def similarities(
        self, source_index: int, metric: SimilarityName, start: int = 0, stop: int | None = None
    ) -> np.ndarray:
        metric = _coerce_similarity(metric)
        stop = self.values.shape[0] if stop is None else stop
        candidate_values = self.values[start:stop]
        candidate_sizes = self.row_sizes[start:stop]
        source = self.values.getrow(source_index) if isinstance(self.values, csr_matrix) else self.values[source_index]
        if metric is Similarity.MANHATTAN:
            differences = np.abs(candidate_values - source)
            if self.dimension_available is not None:
                shared = self.dimension_available[start:stop] & self.dimension_available[source_index]
                return vectorized_similarity(metric, SimilarityOperands(differences=differences, shared=shared))
            return vectorized_similarity(metric, SimilarityOperands(differences=differences))
        if isinstance(self.values, csr_matrix):
            c_mat = cast('csr_matrix', candidate_values)
            s_mat = cast('csr_matrix', source)
            intersections = np.asarray((c_mat @ s_mat.T).toarray()).ravel()
        else:
            intersections = candidate_values @ source
        if metric is Similarity.JACCARD:
            return vectorized_similarity(
                metric,
                SimilarityOperands(
                    intersections=intersections,
                    left_sizes=candidate_sizes,
                    right_sizes=self.row_sizes[source_index],
                ),
            )
        if metric is Similarity.DICE:
            return vectorized_similarity(
                metric,
                SimilarityOperands(
                    intersections=intersections,
                    left_sizes=candidate_sizes,
                    right_sizes=self.row_sizes[source_index],
                ),
            )
        if metric is Similarity.COSINE:
            source_norm = self.row_norms[source_index]
            values = (
                np.asarray((cast('csr_matrix', candidate_values) @ cast('csr_matrix', source).T).toarray()).ravel()
                if isinstance(self.values, csr_matrix)
                else candidate_values @ source
            )
            return vectorized_similarity(
                metric,
                SimilarityOperands(
                    intersections=values,
                    left_norms=self.row_norms[start:stop],
                    right_norms=source_norm,
                ),
            ).ravel()
        raise ValueError(f'unsupported v2 similarity metric: {metric}')

    def similarities_many(
        self, source_indices: Sequence[int], metric: SimilarityName, start: int = 0, stop: int | None = None
    ) -> np.ndarray:
        metric = _coerce_similarity(metric)
        stop = self.values.shape[0] if stop is None else stop
        sources = self.values[list(source_indices)]
        candidates = self.values[start:stop]
        if metric is Similarity.MANHATTAN:
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
                return vectorized_similarity(metric, SimilarityOperands(differences=differences, shared=shared))
            return vectorized_similarity(metric, SimilarityOperands(differences=differences))
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
        if metric is Similarity.JACCARD:
            return vectorized_similarity(
                metric,
                SimilarityOperands(
                    intersections=intersections,
                    left_sizes=source_sizes[:, None],
                    right_sizes=candidate_sizes[None, :],
                ),
            )
        if metric is Similarity.DICE:
            return vectorized_similarity(
                metric,
                SimilarityOperands(
                    intersections=intersections,
                    left_sizes=source_sizes[:, None],
                    right_sizes=candidate_sizes[None, :],
                ),
            )
        if metric is Similarity.COSINE:
            source_norms = self.row_norms[list(source_indices)]
            candidate_norms = self.row_norms[start:stop]
            return vectorized_similarity(
                metric,
                SimilarityOperands(
                    intersections=intersections,
                    left_norms=source_norms[:, None],
                    right_norms=candidate_norms[None, :],
                ),
            )
        raise ValueError(f'unsupported v2 similarity metric: {metric}')

    def similarity(self, left_index: int, right_index: int, metric: SimilarityName) -> float:
        """Calculate one pair score without materializing catalogue-wide scores."""
        metric = _coerce_similarity(metric)
        left = self.values.getrow(left_index) if isinstance(self.values, csr_matrix) else self.values[left_index]
        right = self.values.getrow(right_index) if isinstance(self.values, csr_matrix) else self.values[right_index]
        left_values = left.toarray().ravel() if isinstance(left, csr_matrix) else left
        right_values = right.toarray().ravel() if isinstance(right, csr_matrix) else right
        if metric is Similarity.COSINE:
            denominator = self.row_norms[left_index] * self.row_norms[right_index]
            return float(np.dot(left_values, right_values) / denominator) if denominator else 0.0
        if metric in (Similarity.JACCARD, Similarity.DICE):
            return similarity_score(left_values, right_values, metric)
        if metric is Similarity.MANHATTAN:
            differences = np.abs(left_values - right_values)
            if self.dimension_available is not None:
                shared = self.dimension_available[left_index] & self.dimension_available[right_index]
                distance = _masked_numeric_distance(left_values, right_values, shared)
                return 1.0 / (1.0 + distance) if distance is not None else 0.0
            return float(1.0 / (1.0 + differences.mean()))
        raise ValueError(f'unsupported v2 similarity metric: {metric}')


def weighted_similarity(
    bundle: FeatureBundle,
    left_index: int,
    right_index: int,
    *,
    weights: Mapping[str, float] = V2_WEIGHTS,
    metrics: Mapping[str, SimilarityName] = V2_METRICS,
    properties: Sequence[SimilarityProperty] | None = None,
    availability_policy: AvailabilityPolicy | None = None,
) -> float:
    """Return pairwise weighted similarity with availability renormalization."""
    if left_index < 0 or right_index < 0 or left_index >= bundle.anime_ids.size or right_index >= bundle.anime_ids.size:
        raise IndexError('feature row is outside the bundle')
    active_properties = (
        tuple(properties)
        if properties is not None
        else default_similarity_properties(dict(weights), dict(metrics), CONTENT_BLOCKS)
    )
    _validate_similarity_properties(active_properties)
    blocks = {block.name: block for block in bundle.blocks}
    available: list[tuple[float, float]] = []
    content_weight = 0.0
    for property_spec in active_properties:
        weight = property_spec.weight
        block = blocks.get(property_spec.name)
        if block is None or weight == 0.0:
            continue
        similarity = _property_similarity(block, left_index, right_index, property_spec, availability_policy)
        if similarity is None:
            continue
        if property_spec.contributes_to_content:
            content_weight += weight
        available.append((weight, similarity))
    total_weight = sum(weight for weight, _ in available)
    if total_weight == 0.0 or content_weight < MIN_CONTENT_WEIGHT:
        raise ValueError('anime pair has no comparable feature families')
    return sum(weight * similarity for weight, similarity in available) / total_weight


def _property_similarity(
    block: FeatureBlock,
    left_index: int,
    right_index: int,
    property_spec: SimilarityProperty,
    availability_policy: AvailabilityPolicy | None,
) -> float | None:
    """Return one comparable feature-family score, or ``None`` when unavailable."""
    row_available = block.availability(availability_policy)
    if not row_available[left_index] or not row_available[right_index]:
        return None

    left = block.dense_row(left_index)
    right = block.dense_row(right_index)
    if property_spec.name == 'numeric' and block.dimension_available is not None:
        shared_dimensions = block.dimension_available[left_index] & block.dimension_available[right_index]
        numeric_distance = _masked_numeric_distance(left, right, shared_dimensions)
        return distance_to_similarity(numeric_distance, property_spec.metric) if numeric_distance is not None else None
    if _is_unavailable(left) or _is_unavailable(right):
        return None
    return similarity_score(left, right, property_spec.metric)


def _validate_similarity_properties(properties: Sequence[SimilarityProperty]) -> None:
    """Reject ambiguous or unusable weighted similarity configurations."""
    names = tuple(property_spec.name for property_spec in properties)
    if len(set(names)) != len(names):
        raise ValueError('similarity property names must be unique')
    if not any(property_spec.weight > 0.0 for property_spec in properties):
        raise ValueError('weights must contain at least one positive, non-negative value')


def _is_unavailable(value: np.ndarray) -> bool:
    return value.size == 0 or not np.any(value)


def _coerce_similarity(metric: SimilarityName) -> Similarity:
    """Normalize public string configuration to the typed similarity enum."""
    try:
        return Similarity(metric)
    except ValueError as error:
        raise ValueError(f'unsupported v2 similarity metric: {metric}') from error


def _masked_numeric_distance(left: np.ndarray, right: np.ndarray, shared_dimensions: NDArray[np.bool_]) -> float | None:
    """Return numeric Manhattan distance over jointly observed dimensions."""
    if not shared_dimensions.any():
        return None
    return float(np.abs(left[shared_dimensions] - right[shared_dimensions]).mean())
