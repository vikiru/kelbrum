"""Independent retrieval paths used as inputs to the evidence-preserving Union."""

from collections.abc import Iterable, Mapping, Sequence
from heapq import nsmallest
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize

from features.synopsis import LatentConfig, TfidfConfig, bm25, lsa, tfidf

FloatVector = NDArray[np.float32]
_MATRIX_DIMENSIONS = 2


class SynopsisPathIndex:
    """Prepared synopsis matrices for independent lexical and latent paths."""

    def __init__(self, anime_ids: Sequence[int], texts: Sequence[str | None]) -> None:
        if len(anime_ids) != len(texts) or len(set(anime_ids)) != len(anime_ids):
            raise ValueError('anime IDs and synopsis rows must be aligned and unique')
        self.anime_ids = np.asarray(anime_ids, dtype=np.int64)
        self._texts = tuple(texts)
        self._available = np.asarray(
            [bool(text and text.strip()) for text in texts],
            dtype=bool,
        )
        self._features: dict[str, csr_matrix | FloatVector] = {}
        self._normalized_features: dict[str, FloatVector | csr_matrix] = {}

    def fit_tfidf(self, config: TfidfConfig | None = None) -> None:
        self._features['tfidf'] = tfidf(self._texts, config).matrix
        self._normalized_features.pop('tfidf', None)

    def fit_bm25(self) -> None:
        self._features['bm25'] = bm25(self._texts).matrix
        self._normalized_features.pop('bm25', None)

    def fit_bm25_matrix(self, values: csr_matrix) -> None:
        """Fit an already-generated, row-aligned BM25 matrix."""
        if values.shape[0] != self.anime_ids.size:
            raise ValueError('BM25 matrix must align with anime IDs')
        self._features['bm25'] = values
        self._normalized_features.pop('bm25', None)

    def fit_lsa(
        self,
        tfidf_config: TfidfConfig | None = None,
        latent_config: LatentConfig | None = None,
    ) -> None:
        tfidf_features = tfidf(self._texts, tfidf_config)
        self._features['lsa'] = lsa(tfidf_features, latent_config)
        self._normalized_features.pop('lsa', None)

    def fit_lsa_matrix(self, values: FloatVector | np.ndarray) -> None:
        """Fit an already-generated, row-aligned LSA matrix."""
        if values.ndim != _MATRIX_DIMENSIONS or values.shape[0] != self.anime_ids.size:
            raise ValueError('LSA matrix must align with anime IDs')
        self._features['lsa'] = np.asarray(values, dtype=np.float32)
        self._normalized_features.pop('lsa', None)

    def fit_embedding_matrix(self, values: FloatVector) -> None:
        """Fit an already-generated, row-aligned embedding matrix."""
        if values.ndim != _MATRIX_DIMENSIONS or values.shape[0] != self.anime_ids.size:
            raise ValueError('embedding matrix must align with anime IDs')
        self._features['embedding'] = np.asarray(values, dtype=np.float32)
        self._normalized_features.pop('embedding', None)

    def rank(self, path: str, source_index: int, *, limit: int = 300) -> tuple[tuple[int, float], ...]:
        """Return one path's ranked IDs without mixing it with other paths."""
        _validate_limit(limit)
        normalized = self._normalized_path(path)
        if not 0 <= source_index < self.anime_ids.size:
            raise IndexError('source row is outside the synopsis index')
        if not self._available[source_index]:
            return ()
        if isinstance(normalized, csr_matrix):
            source_row = cast('csr_matrix', normalized.getrow(source_index))
            product = normalized @ source_row.T
        else:
            product = normalized @ normalized[source_index]
        scores = np.asarray(product.toarray() if isinstance(product, csr_matrix) else product, dtype=np.float32).ravel()
        scores[source_index] = -np.inf
        available = np.flatnonzero(self._available & np.isfinite(scores) & (scores > 0.0))
        if available.size == 0:
            return ()
        selected_positions = _select_top_indices(available, scores[available], limit, self.anime_ids)
        indices = available[selected_positions]
        return tuple((int(self.anime_ids[index]), float(scores[index])) for index in indices)

    def rank_many(
        self, path: str, source_indices: Sequence[int], *, limit: int = 300
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        """Rank a source batch with one sparse matrix multiplication."""
        _validate_limit(limit)
        normalized = self._normalized_path(path)
        indices = self._validate_source_indices(source_indices)
        if isinstance(normalized, csr_matrix):
            sub_norm = cast('csr_matrix', normalized[list(indices)])
            products = sub_norm @ normalized.T
        else:
            products = normalized[list(indices)] @ normalized.T
        output: list[tuple[tuple[int, float], ...]] = []
        for row_number, source_index in enumerate(indices):
            if not self._available[source_index]:
                output.append(())
                continue
            if isinstance(products, csr_matrix):
                scores = np.asarray(products.getrow(row_number).toarray()).ravel().astype(np.float32, copy=False)
            else:
                scores = np.asarray(products[row_number]).ravel().astype(np.float32, copy=False)
            scores[source_index] = -np.inf
            available = np.flatnonzero(self._available & np.isfinite(scores) & (scores > 0.0))
            if available.size == 0:
                output.append(())
                continue
            selected_positions = _select_top_indices(available, scores[available], limit, self.anime_ids)
            ranked = available[selected_positions]
            output.append(tuple((int(self.anime_ids[index]), float(scores[index])) for index in ranked))
        return tuple(output)

    def rank_many_streaming(
        self,
        path: str,
        source_indices: Sequence[int],
        *,
        limit: int = 300,
        candidate_batch_size: int = 512,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        """Rank sources by scanning bounded candidate blocks and retaining top-K state."""
        _validate_limit(limit)
        if candidate_batch_size < 1:
            raise ValueError('candidate_batch_size must be positive')
        normalized = self._normalized_path(path)
        sources = self._validate_source_indices(source_indices)
        sub_sources = (
            cast('csr_matrix', normalized[list(sources)])
            if isinstance(normalized, csr_matrix)
            else normalized[list(sources)]
        )
        top_scores = np.full((len(sources), limit), -np.inf, dtype=np.float32)
        top_indices = np.full((len(sources), limit), -1, dtype=np.int32)
        for start in range(0, self.anime_ids.size, candidate_batch_size):
            stop = min(start + candidate_batch_size, self.anime_ids.size)
            if isinstance(normalized, csr_matrix):
                sub_candidates = cast('csr_matrix', normalized[start:stop])
                block = sub_sources @ sub_candidates.T
            else:
                block = sub_sources @ normalized[start:stop].T
            values_block = block.toarray() if isinstance(block, csr_matrix) else np.asarray(block)
            values = np.asarray(values_block, dtype=np.float32).copy()
            block_indices = np.arange(start, stop, dtype=np.int32)
            values[:, ~self._available[start:stop]] = -np.inf
            for row_number, source_index in enumerate(sources):
                source_offset = source_index - start
                if 0 <= source_offset < values.shape[1]:
                    values[row_number, source_offset] = -np.inf
                if not self._available[source_index]:
                    values[row_number, :] = -np.inf
            values[values <= 0.0] = -np.inf
            for row_number in range(len(sources)):
                block_selection = _select_top_indices(block_indices, values[row_number], limit, self.anime_ids)
                combined_scores = np.concatenate((top_scores[row_number], values[row_number, block_selection]))
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
            order = np.lexsort((indices, -scores))
            output.append(
                tuple(
                    (int(self.anime_ids[index]), float(scores[position]))
                    for position, index in zip(order, indices[order], strict=True)
                )
            )
        return tuple(output)

    def _normalized_path(self, path: str) -> FloatVector | csr_matrix:
        """Return a cached L2-normalized matrix for a fitted path."""
        values = self._features.get(path)
        if values is None:
            raise KeyError(f'synopsis path is not fitted: {path}')
        normalized = self._normalized_features.get(path)
        if normalized is None:
            matrix = values if isinstance(values, csr_matrix) else np.asarray(values)
            normalized = normalize(matrix, norm='l2', axis=1)
            self._normalized_features[path] = normalized
        return normalized

    def _validate_source_indices(self, source_indices: Sequence[int]) -> tuple[int, ...]:
        """Normalize and validate source rows shared by batch ranking methods."""
        indices = tuple(source_indices)
        if any(index < 0 or index >= self.anime_ids.size for index in indices):
            raise IndexError('source row is outside the synopsis index')
        return indices


def build_synopsis_path_index(anime_ids: Sequence[int], texts: Sequence[str | None]) -> SynopsisPathIndex:
    """Create a synopsis index for later independent path fitting."""
    return SynopsisPathIndex(anime_ids, texts)


class CategoricalPathIndex:
    """Reusable inverted index for one categorical retrieval path."""

    def __init__(self, anime_ids: Sequence[int], values: Sequence[Sequence[str]]) -> None:
        if len(anime_ids) != len(values):
            raise ValueError('categorical IDs and values must be aligned')
        self._anime_ids = tuple(anime_ids)
        self._values = tuple(frozenset(row) for row in values)
        self._value_sizes = tuple(len(row) for row in self._values)
        postings: dict[str, set[int]] = {}
        for index, row in enumerate(self._values):
            for label in row:
                postings.setdefault(label, set()).add(index)
        self._postings = {label: frozenset(indices) for label, indices in postings.items()}

    def rank_many(self, source_indices: Sequence[int], *, limit: int) -> tuple[tuple[tuple[int, float], ...], ...]:
        _validate_limit(limit)
        if any(index < 0 or index >= len(self._values) for index in source_indices):
            raise ValueError('categorical source indices must be aligned')
        output: list[tuple[tuple[int, float], ...]] = []
        for source_index in source_indices:
            source = self._values[source_index]
            overlap_counts: dict[int, int] = {}
            for label in source:
                for candidate_index in self._postings[label]:
                    if candidate_index != source_index:
                        overlap_counts[candidate_index] = overlap_counts.get(candidate_index, 0) + 1
            source_size = len(source)
            scored = [
                (
                    index,
                    2.0 * overlap / (source_size + self._value_sizes[index]),
                )
                for index, overlap in overlap_counts.items()
            ]

            def _scored_key(item: tuple[int, float]) -> tuple[float, int]:
                return (-item[1], self._anime_ids[item[0]])

            top_scored = nsmallest(limit, scored, key=_scored_key)
            output.append(tuple((self._anime_ids[index], score) for index, score in top_scored))
        return tuple(output)


class AffinityPathIndex:
    """Bounded structured retrieval with optional asymmetric value compatibility."""

    def __init__(
        self,
        anime_ids: Sequence[int],
        values: Sequence[Sequence[str]],
        compatibility: Mapping[str, Mapping[str, float]] | None = None,
    ) -> None:
        if len(anime_ids) != len(values):
            raise ValueError('affinity IDs and values must be aligned')
        self._anime_ids = tuple(anime_ids)
        self._values = tuple(frozenset(row) for row in values)
        self._compatibility = compatibility or {}
        self._postings: dict[str, frozenset[int]] = {}
        postings: dict[str, set[int]] = {}
        for index, row in enumerate(self._values):
            for value in row:
                postings.setdefault(value, set()).add(index)
        self._postings = {value: frozenset(indices) for value, indices in postings.items()}

    def rank_many(self, source_indices: Sequence[int], *, limit: int) -> tuple[tuple[tuple[int, float], ...], ...]:
        _validate_limit(limit)
        if any(index < 0 or index >= len(self._values) for index in source_indices):
            raise ValueError('affinity source indices must be aligned')
        output: list[tuple[tuple[int, float], ...]] = []
        for source_index in source_indices:
            source = self._values[source_index]
            if not source:
                output.append(())
                continue
            compatible = {candidate for value in source for candidate in self._compatible_values(value)}
            candidates = set().union(*(self._postings.get(value, frozenset()) for value in compatible))
            candidates.discard(source_index)
            scored: list[tuple[int, float]] = []
            for index in candidates:
                score = self._candidate_score(source, self._values[index])
                if score > 0.0:
                    scored.append((index, score))

            def sort_key(item: tuple[int, float]) -> tuple[float, int]:
                return -item[1], self._anime_ids[item[0]]

            top_scored = nsmallest(limit, scored, key=sort_key)
            output.append(tuple((self._anime_ids[index], score) for index, score in top_scored))
        return tuple(output)

    def _compatible_values(self, source_value: str) -> Iterable[str]:
        compatibility = self._compatibility.get(source_value)
        return (source_value,) if compatibility is None else compatibility.keys()

    def _candidate_score(self, source: frozenset[str], candidate: frozenset[str]) -> float:
        scores: list[float] = []
        for source_value in source:
            compatibility = self._compatibility.get(source_value)
            if compatibility is None:
                scores.append(1.0 if source_value in candidate else 0.0)
            else:
                scores.extend(compatibility.get(candidate_value, 0.0) for candidate_value in candidate)
        return max(scores, default=0.0)


def _validate_limit(limit: int) -> None:
    if limit < 1:
        raise ValueError('limit must be positive')


def _select_top_indices(
    candidate_indices: NDArray[np.integer],
    scores: NDArray[np.floating],
    limit: int,
    anime_ids: NDArray[np.integer],
) -> NDArray[np.integer]:
    """Select positive finite scores using anime ID as the deterministic tie-breaker."""
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
