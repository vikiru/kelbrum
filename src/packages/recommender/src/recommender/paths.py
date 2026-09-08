"""Independent retrieval paths used as inputs to the evidence-preserving Union."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize

from features.encoders import synopsis_embeddings
from features.synopsis import LatentConfig, TfidfConfig, bm25, lsa, tfidf

FloatVector = NDArray[np.float32]


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
        if values.ndim != 2 or values.shape[0] != self.anime_ids.size:
            raise ValueError('LSA matrix must align with anime IDs')
        self._features['lsa'] = np.asarray(values, dtype=np.float32)
        self._normalized_features.pop('lsa', None)

    def fit_embeddings(
        self,
        *,
        model_name: str,
        cache_path: Path | None = None,
        local_only: bool = True,
    ) -> None:
        """Fit a sentence-embedding synopsis path with optional disk caching."""
        values = synopsis_embeddings(
            self._texts,
            model_name=model_name,
            cache_path=cache_path,
            ordered_ids=self.anime_ids.tolist(),
            local_only=local_only,
        )
        self._features['embedding'] = values
        self._normalized_features.pop('embedding', None)

    def fit_embedding_matrix(self, values: FloatVector) -> None:
        """Fit an already-generated, row-aligned embedding matrix."""
        if values.ndim != 2 or values.shape[0] != self.anime_ids.size:
            raise ValueError('embedding matrix must align with anime IDs')
        self._features['embedding'] = np.asarray(values, dtype=np.float32)
        self._normalized_features.pop('embedding', None)

    def rank(self, path: str, source_index: int, *, limit: int = 300) -> tuple[tuple[int, float], ...]:
        """Return one path's ranked IDs without mixing it with other paths."""
        if path not in self._features:
            raise KeyError(f'synopsis path is not fitted: {path}')
        if not 0 <= source_index < self.anime_ids.size:
            raise IndexError('source row is outside the synopsis index')
        if not self._available[source_index]:
            return ()
        values = self._features[path]
        normalized = self._normalized_features.get(path)
        if normalized is None:
            matrix = values if isinstance(values, csr_matrix) else np.asarray(values)
            normalized = normalize(matrix, norm='l2', axis=1)
            self._normalized_features[path] = normalized
        if isinstance(normalized, csr_matrix):
            source_row = cast('csr_matrix', normalized.getrow(source_index))
            product = normalized @ source_row.T
        else:
            product = normalized @ normalized[source_index]
        scores = np.asarray(product.toarray() if isinstance(product, csr_matrix) else product, dtype=np.float32).ravel()
        scores[source_index] = -np.inf
        available = np.flatnonzero(self._available & np.isfinite(scores) & (scores > 0.0))
        candidate_count = min(limit, available.size)
        if candidate_count == 0:
            return ()
        candidates = available[np.argpartition(-scores[available], candidate_count - 1)[:candidate_count]]
        indices = candidates[np.argsort(-scores[candidates], kind='stable')]
        return tuple((int(self.anime_ids[index]), float(scores[index])) for index in indices)

    def rank_many(
        self, path: str, source_indices: Sequence[int], *, limit: int = 300
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        """Rank a source batch with one sparse matrix multiplication."""
        if path not in self._features:
            raise KeyError(f'synopsis path is not fitted: {path}')
        normalized = self._normalized_features.get(path)
        if normalized is None:
            values = self._features[path]
            matrix = values if isinstance(values, csr_matrix) else np.asarray(values)
            normalized = normalize(matrix, norm='l2', axis=1)
            self._normalized_features[path] = normalized
        indices = tuple(source_indices)
        if any(index < 0 or index >= self.anime_ids.size for index in indices):
            raise IndexError('source row is outside the synopsis index')
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
            candidate_count = min(limit, available.size)
            if candidate_count == 0:
                output.append(())
                continue
            candidates = available[np.argpartition(-scores[available], candidate_count - 1)[:candidate_count]]
            ranked = candidates[np.argsort(-scores[candidates], kind='stable')]
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
        if candidate_batch_size < 1:
            raise ValueError('candidate_batch_size must be positive')
        if path not in self._features:
            raise KeyError(f'synopsis path is not fitted: {path}')
        normalized = self._normalized_features.get(path)
        if normalized is None:
            values = self._features[path]
            matrix = values if isinstance(values, csr_matrix) else np.asarray(values)
            normalized = normalize(matrix, norm='l2', axis=1)
            self._normalized_features[path] = normalized
        sources = tuple(source_indices)
        if any(index < 0 or index >= self.anime_ids.size for index in sources):
            raise IndexError('source row is outside the synopsis index')
        top_scores = np.full((len(sources), limit), -np.inf, dtype=np.float32)
        top_indices = np.full((len(sources), limit), -1, dtype=np.int32)
        for start in range(0, self.anime_ids.size, candidate_batch_size):
            stop = min(start + candidate_batch_size, self.anime_ids.size)
            if isinstance(normalized, csr_matrix):
                sub_sources = cast('csr_matrix', normalized[list(sources)])
                sub_candidates = cast('csr_matrix', normalized[start:stop])
                block = sub_sources @ sub_candidates.T
            else:
                block = normalized[list(sources)] @ normalized[start:stop].T
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
            block_count = min(limit, values.shape[1])
            selection = np.argpartition(values, -block_count, axis=1)[:, -block_count:]
            block_scores = np.take_along_axis(values, selection, axis=1)
            block_indices = block_indices[selection]
            combined_scores = np.concatenate((top_scores, block_scores), axis=1)
            combined_indices = np.concatenate((top_indices, block_indices), axis=1)
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


def build_synopsis_path_index(anime_ids: Sequence[int], texts: Sequence[str | None]) -> SynopsisPathIndex:
    """Create a synopsis index for later independent path fitting."""
    return SynopsisPathIndex(anime_ids, texts)


def rank_categorical(
    anime_ids: Sequence[int],
    values: Sequence[Sequence[str]],
    source_index: int,
    *,
    limit: int = 300,
) -> tuple[tuple[int, float], ...]:
    """Rank one categorical property using Dice similarity."""
    if len(anime_ids) != len(values) or not 0 <= source_index < len(values):
        raise ValueError('categorical IDs, values, and source index must be aligned')
    source = set(values[source_index])
    scores: list[tuple[int, float]] = []
    for index, candidate in enumerate(values):
        if index == source_index:
            continue
        candidate_set = set(candidate)
        denominator = len(source) + len(candidate_set)
        score = 2.0 * len(source & candidate_set) / denominator if denominator else 0.0
        if score > 0.0:
            scores.append((index, score))
    candidate_count = min(limit, len(scores))

    def _rank_key(item: tuple[int, float]) -> tuple[float, int]:
        return (-item[1], int(anime_ids[item[0]]))

    selected = sorted(scores, key=_rank_key)[:candidate_count]
    return tuple((int(anime_ids[index]), score) for index, score in selected)


def rank_categorical_many(
    anime_ids: Sequence[int],
    values: Sequence[Sequence[str]],
    source_indices: Sequence[int],
    *,
    limit: int = 300,
) -> tuple[tuple[tuple[int, float], ...], ...]:
    """Rank categorical paths using one inverted index for a source batch."""
    if len(anime_ids) != len(values) or any(index < 0 or index >= len(values) for index in source_indices):
        raise ValueError('categorical IDs, values, and source indices must be aligned')
    return CategoricalPathIndex(anime_ids, values).rank_many(source_indices, limit=limit)


class CategoricalPathIndex:
    """Reusable inverted index for one categorical retrieval path."""

    def __init__(self, anime_ids: Sequence[int], values: Sequence[Sequence[str]]) -> None:
        if len(anime_ids) != len(values):
            raise ValueError('categorical IDs and values must be aligned')
        self._anime_ids = tuple(int(anime_id) for anime_id in anime_ids)
        self._values = tuple(frozenset(row) for row in values)
        postings: dict[str, set[int]] = {}
        for index, row in enumerate(self._values):
            for label in row:
                postings.setdefault(label, set()).add(index)
        self._postings = {label: frozenset(indices) for label, indices in postings.items()}

    def rank_many(self, source_indices: Sequence[int], *, limit: int) -> tuple[tuple[tuple[int, float], ...], ...]:
        if any(index < 0 or index >= len(self._values) for index in source_indices):
            raise ValueError('categorical source indices must be aligned')
        output: list[tuple[tuple[int, float], ...]] = []
        for source_index in source_indices:
            source = self._values[source_index]
            candidates = set().union(*(self._postings[label] for label in source)) if source else set()
            candidates.discard(source_index)
            scored = [(index, _dice_score(source, self._values[index])) for index in candidates]

            def _scored_key(item: tuple[int, float]) -> tuple[float, int]:
                return (-item[1], self._anime_ids[item[0]])

            scored.sort(key=_scored_key)
            output.append(tuple((self._anime_ids[index], score) for index, score in scored[:limit]))
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
        self._anime_ids = tuple(int(anime_id) for anime_id in anime_ids)
        self._values = tuple(frozenset(row) for row in values)
        self._compatibility = compatibility or {}
        self._postings: dict[str, frozenset[int]] = {}
        postings: dict[str, set[int]] = {}
        for index, row in enumerate(self._values):
            for value in row:
                postings.setdefault(value, set()).add(index)
        self._postings = {value: frozenset(indices) for value, indices in postings.items()}

    def rank_many(self, source_indices: Sequence[int], *, limit: int) -> tuple[tuple[tuple[int, float], ...], ...]:
        if any(index < 0 or index >= len(self._values) for index in source_indices):
            raise ValueError('affinity source indices must be aligned')
        output: list[tuple[tuple[int, float], ...]] = []
        for source_index in source_indices:
            source = self._values[source_index]
            if not source:
                output.append(())
                continue
            compatible = {candidate for value in source for candidate in self._compatibility.get(value, {value: 1.0})}
            candidates = set().union(*(self._postings.get(value, frozenset()) for value in compatible))
            candidates.discard(source_index)
            scored: list[tuple[int, float]] = []
            for index in candidates:
                score = max(
                    self._compatibility.get(value, {value: 1.0}).get(candidate, 0.0)
                    for value in source
                    for candidate in self._values[index]
                )
                if score > 0.0:
                    scored.append((index, score))

            def sort_key(item: tuple[int, float]) -> tuple[float, int]:
                return -item[1], self._anime_ids[item[0]]

            scored.sort(key=sort_key)
            output.append(tuple((self._anime_ids[index], score) for index, score in scored[:limit]))
        return tuple(output)


def _dice_score(source: frozenset[str], candidate: frozenset[str]) -> float:
    denominator = len(source) + len(candidate)
    return 2.0 * len(source & candidate) / denominator if denominator else 0.0
