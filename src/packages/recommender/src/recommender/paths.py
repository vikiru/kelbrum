"""Independent retrieval paths used as inputs to the evidence-preserving Union."""

from collections.abc import Iterable, Mapping, Sequence
from heapq import nsmallest
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

try:
    import torch

    _CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    torch = None  # type: ignore[assignment]
    _CUDA_AVAILABLE = False

from features.synopsis import LatentConfig, TfidfConfig, bm25, clean_synopses, lsa, tfidf

FloatVector = NDArray[np.float32]
_MATRIX_DIMENSIONS = 2
MAX_FULL_MATRIX_SCORE_BYTES = 128 * 1024 * 1024


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
        self._cuda_tensors: dict[str, Any] = {}

    def fit_char_tfidf(
        self,
        *,
        ngram_range: tuple[int, int] = (3, 5),
        min_df: int = 5,
        max_df: float = 0.90,
        sublinear_tf: bool = True,
        max_features: int = 35_000,
    ) -> None:
        """Fit a character 3-5 n-gram TF-IDF sparse matrix."""
        cleaned = clean_synopses(self._texts)
        if not any(cleaned):
            self._features['char_3_5g_tfidf'] = csr_matrix((len(cleaned), 0), dtype=np.float32)
        else:
            effective_min_df = min(min_df, len(cleaned)) if isinstance(min_df, int) else min_df
            vectorizer = TfidfVectorizer(
                analyzer='char',
                ngram_range=ngram_range,
                min_df=effective_min_df,
                max_df=max_df if len(cleaned) > 2 else 1.0,
                sublinear_tf=sublinear_tf,
                max_features=max_features,
                strip_accents='unicode',
            )
            matrix = vectorizer.fit_transform(cleaned)
            self._features['char_3_5g_tfidf'] = csr_matrix(matrix, dtype=np.float32)
        self._normalized_features.pop('char_3_5g_tfidf', None)

    def fit_char_tfidf_matrix(self, values: csr_matrix) -> None:
        """Fit an already-generated, row-aligned character TF-IDF matrix."""
        if values.shape[0] != self.anime_ids.size:
            raise ValueError('char TF-IDF matrix must align with anime IDs')
        self._features['char_3_5g_tfidf'] = values
        self._normalized_features.pop('char_3_5g_tfidf', None)

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

    def rank(
        self,
        path: str,
        source_index: int,
        *,
        limit: int = 300,
        excluded_ids: frozenset[int] = frozenset(),
    ) -> tuple[tuple[int, float], ...]:
        """Return one path's ranked IDs without mixing it with other paths."""
        _validate_limit(limit)
        normalized = self._normalized_path(path)
        if not 0 <= source_index < self.anime_ids.size:
            raise IndexError('source row is outside the synopsis index')
        if not self._available[source_index]:
            return ()
        if isinstance(normalized, csr_matrix):
            source_row = cast('csr_matrix', normalized.getrow(source_index))
            product = cast('csr_matrix', normalized @ source_row.T)
            row_indices = product.tocoo().row
            row_scores = np.asarray(product.data, dtype=np.float32)
            mask = (
                (row_indices != source_index)
                & self._available[row_indices]
                & np.isfinite(row_scores)
                & (row_scores > 0.0)
            )
            available = row_indices[mask]
            if excluded_ids:
                available = _remove_excluded(self.anime_ids, available, excluded_ids)
                scores_for_available = row_scores[mask][np.isin(row_indices[mask], available)]
            else:
                scores_for_available = row_scores[mask]
            if available.size == 0:
                return ()
            selected_positions = _select_top_indices(available, scores_for_available, limit, self.anime_ids)
            indices = available[selected_positions]
            return tuple(
                (int(self.anime_ids[index]), float(scores_for_available[pos]))
                for pos, index in zip(selected_positions, indices, strict=True)
            )
        product = normalized @ normalized[source_index]
        scores = np.asarray(product, dtype=np.float32).ravel()
        scores[source_index] = -np.inf
        available_mask = self._available & np.isfinite(scores) & (scores > 0.0)
        if excluded_ids:
            available_mask &= ~np.isin(self.anime_ids, tuple(excluded_ids))
        available = np.flatnonzero(available_mask)
        if available.size == 0:
            return ()
        selected_positions = _select_top_indices(available, scores[available], limit, self.anime_ids)
        indices = available[selected_positions]
        return tuple((int(self.anime_ids[index]), float(scores[index])) for index in indices)

    def rank_many(
        self,
        path: str,
        source_indices: Sequence[int],
        *,
        limit: int = 300,
        excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        """Rank a source batch with one sparse matrix multiplication."""
        _validate_limit(limit)
        normalized = self._normalized_path(path)
        indices = self._validate_source_indices(source_indices)
        _validate_excluded_ids(excluded_ids_by_source, len(indices))
        if isinstance(normalized, csr_matrix):
            sub_norm = cast('csr_matrix', normalized[list(indices)])
            products = sub_norm @ normalized.T
        elif _CUDA_AVAILABLE and torch is not None:
            if path not in self._cuda_tensors:
                self._cuda_tensors[path] = torch.from_numpy(normalized).cuda()
            gpu_mat = self._cuda_tensors[path]
            gpu_sources = gpu_mat[list(indices)]
            products = torch.matmul(gpu_sources, gpu_mat.T).cpu().numpy()
        else:
            products = normalized[list(indices)] @ normalized.T
        output: list[tuple[tuple[int, float], ...]] = []
        for row_number, source_index in enumerate(indices):
            if not self._available[source_index]:
                output.append(())
                continue
            if isinstance(products, csr_matrix):
                start = int(products.indptr[row_number])
                end = int(products.indptr[row_number + 1])
                col_indices = products.indices[start:end]
                col_scores = np.asarray(products.data[start:end], dtype=np.float32)
                mask = (
                    (col_indices != source_index)
                    & self._available[col_indices]
                    & np.isfinite(col_scores)
                    & (col_scores > 0.0)
                )
                available = col_indices[mask]
                available_scores = col_scores[mask]
                if excluded_ids_by_source is not None and excluded_ids_by_source[row_number]:
                    keep = ~np.isin(self.anime_ids[available], tuple(excluded_ids_by_source[row_number]))
                    available = available[keep]
                    available_scores = available_scores[keep]
                if available.size == 0:
                    output.append(())
                    continue
                selected_positions = _select_top_indices(available, available_scores, limit, self.anime_ids)
                ranked = available[selected_positions]
                ranked_scores = available_scores[selected_positions]
                output.append(
                    tuple((int(self.anime_ids[idx]), float(sc)) for idx, sc in zip(ranked, ranked_scores, strict=True))
                )
                continue
            scores = np.asarray(products[row_number]).ravel().astype(np.float32, copy=False)
            scores[source_index] = -np.inf
            available = np.flatnonzero(self._available & np.isfinite(scores) & (scores > 0.0))
            if excluded_ids_by_source is not None:
                available = _remove_excluded(self.anime_ids, available, excluded_ids_by_source[row_number])
            if available.size == 0:
                output.append(())
                continue
            selected_positions = _select_top_indices(available, scores[available], limit, self.anime_ids)
            ranked = available[selected_positions]
            output.append(tuple((int(self.anime_ids[index]), float(scores[index])) for index in ranked))
        return tuple(output)

    def rank_many_adaptive(
        self,
        path: str,
        source_indices: Sequence[int],
        *,
        limit: int = 300,
        candidate_batch_size: int = 512,
        excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
        max_score_bytes: int = MAX_FULL_MATRIX_SCORE_BYTES,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        """Bound full-matrix scoring by its dense score buffer and fall back to streaming."""
        if max_score_bytes < 0:
            raise ValueError('maximum score buffer bytes cannot be negative')
        score_buffer_bytes = len(source_indices) * self.anime_ids.size * np.dtype(np.float32).itemsize
        if score_buffer_bytes <= max_score_bytes:
            return self.rank_many(
                path,
                source_indices,
                limit=limit,
                excluded_ids_by_source=excluded_ids_by_source,
            )
        return self.rank_many_streaming(
            path,
            source_indices,
            limit=limit,
            candidate_batch_size=candidate_batch_size,
            excluded_ids_by_source=excluded_ids_by_source,
        )

    def rank_many_streaming(
        self,
        path: str,
        source_indices: Sequence[int],
        *,
        limit: int = 300,
        candidate_batch_size: int = 512,
        excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        """Rank sources by scanning bounded candidate blocks and retaining top-K state."""
        _validate_limit(limit)
        if candidate_batch_size < 1:
            raise ValueError('candidate_batch_size must be positive')
        normalized = self._normalized_path(path)
        sources = self._validate_source_indices(source_indices)
        _validate_excluded_ids(excluded_ids_by_source, len(sources))
        sub_sources = (
            cast('csr_matrix', normalized[list(sources)])
            if isinstance(normalized, csr_matrix)
            else normalized[list(sources)]
        )
        top_scores = np.full((len(sources), limit), -np.inf, dtype=np.float32)
        top_indices = np.full((len(sources), limit), -1, dtype=np.int32)
        gpu_mat = None
        gpu_src = None
        if not isinstance(normalized, csr_matrix) and _CUDA_AVAILABLE and torch is not None:
            if path not in self._cuda_tensors:
                self._cuda_tensors[path] = torch.from_numpy(normalized).cuda()
            gpu_mat = self._cuda_tensors[path]
            gpu_src = gpu_mat[list(sources)]
        excluded_tuples = (
            tuple(tuple(ex) if ex else () for ex in excluded_ids_by_source)
            if excluded_ids_by_source is not None
            else None
        )
        for start in range(0, self.anime_ids.size, candidate_batch_size):
            stop = min(start + candidate_batch_size, self.anime_ids.size)
            if isinstance(normalized, csr_matrix):
                sub_candidates = cast('csr_matrix', normalized[start:stop])
                block = sub_sources @ sub_candidates.T
            elif gpu_mat is not None and gpu_src is not None and torch is not None:
                gpu_cand = gpu_mat[start:stop]
                block = torch.matmul(gpu_src, gpu_cand.T).cpu().numpy()
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
                if excluded_tuples is not None and excluded_tuples[row_number]:
                    excluded_mask = np.isin(self.anime_ids[start:stop], excluded_tuples[row_number])
                    values[row_number, excluded_mask] = -np.inf
            values[values <= 0.0] = -np.inf
            for row_number in range(len(sources)):
                row_vals = values[row_number]
                pos_mask = np.isfinite(row_vals) & (row_vals > 0.0)
                if not pos_mask.any():
                    continue
                combined_scores = np.concatenate((top_scores[row_number], row_vals[pos_mask]))
                combined_indices = np.concatenate((top_indices[row_number], block_indices[pos_mask]))
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

    def pairwise_dense_similarities(
        self,
        path: str,
        source_index: int,
        target_indices: Sequence[int],
    ) -> np.ndarray:
        """Compute pairwise cosine similarities between a source index and multiple target indices."""
        if isinstance(target_indices, np.ndarray):
            target_array = (
                target_indices if target_indices.dtype == np.intp else target_indices.astype(np.intp, copy=False)
            )
        elif isinstance(target_indices, range) and target_indices == range(self.anime_ids.size):
            target_array = None
        else:
            targets = list(target_indices)
            if not targets:
                return np.zeros(0, dtype=np.float32)
            target_array = np.asarray(targets, dtype=np.intp)
        if target_array is not None and target_array.size == 0:
            return np.zeros(0, dtype=np.float32)
        if not 0 <= source_index < self.anime_ids.size:
            raise IndexError('source row is outside the synopsis index')
        if not self._available[source_index]:
            out_len = self.anime_ids.size if target_array is None else target_array.size
            return np.zeros(out_len, dtype=np.float32)
        normalized = self._normalized_path(path)
        if isinstance(normalized, csr_matrix):
            source_row = cast('csr_matrix', normalized.getrow(source_index))
            target_rows = normalized if target_array is None else cast('csr_matrix', normalized[target_array])
            sims = np.asarray((target_rows @ source_row.T).toarray(), dtype=np.float32).ravel()
        else:
            target_rows = normalized if target_array is None else normalized[target_array]
            sims = np.dot(target_rows, normalized[source_index])
            if not isinstance(sims, np.ndarray):
                sims = np.asarray(sims, dtype=np.float32)
            elif sims.dtype != np.float32:
                sims = sims.astype(np.float32, copy=False)
        available = self._available if target_array is None else self._available[target_array]
        sims[~available] = 0.0
        np.maximum(sims, 0.0, out=sims)
        return sims

    @property
    def fitted_paths(self) -> tuple[str, ...]:
        """Return names of all currently fitted synopsis paths."""
        return tuple(self._features.keys())

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
    """Reusable inverted index for one categorical retrieval path with Tversky and salience/IDF support."""

    def __init__(
        self,
        anime_ids: Sequence[int],
        values: Sequence[Sequence[str]],
        *,
        alpha: float | None = None,
        beta: float | None = None,
        weights: Mapping[str, float] | None = None,
    ) -> None:
        if len(anime_ids) != len(values):
            raise ValueError('categorical IDs and values must be aligned')
        self._anime_ids = np.asarray(anime_ids, dtype=np.int64)
        self._values = tuple(frozenset(row) for row in values)
        self._value_sizes = tuple(len(row) for row in self._values)
        self._alpha = alpha
        self._beta = beta
        self._weights = weights

        if weights is not None:
            self._row_weights = np.asarray(
                [sum(weights.get(label, 1.0) for label in row) for row in self._values],
                dtype=np.float32,
            )
        else:
            self._row_weights = np.asarray(self._value_sizes, dtype=np.float32)

        unique_labels = sorted({label for row in self._values for label in row})
        self._label_to_col = {label: col for col, label in enumerate(unique_labels)}
        num_rows = len(self._values)
        num_cols = len(unique_labels)

        if num_cols > 0:
            row_indices: list[int] = []
            col_indices: list[int] = []
            data_values: list[float] = []

            for row_idx, row in enumerate(self._values):
                for label in row:
                    row_indices.append(row_idx)
                    col_indices.append(self._label_to_col[label])
                    weight = weights.get(label, 1.0) if weights is not None else 1.0
                    data_values.append(weight)

            self._indicator_matrix = csr_matrix(
                (data_values, (row_indices, col_indices)),
                shape=(num_rows, num_cols),
                dtype=np.float32,
            )
            binary_values = np.ones(len(row_indices), dtype=np.float32)
            self._binary_matrix_t = csr_matrix(
                (binary_values, (row_indices, col_indices)),
                shape=(num_rows, num_cols),
                dtype=np.float32,
            ).T.tocsr()
        else:
            self._indicator_matrix = csr_matrix((num_rows, 0), dtype=np.float32)
            self._binary_matrix_t = csr_matrix((0, num_rows), dtype=np.float32)

    def rank_many(
        self,
        source_indices: Sequence[int],
        *,
        limit: int,
        excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        _validate_limit(limit)
        if any(index < 0 or index >= len(self._values) for index in source_indices):
            raise ValueError('categorical source indices must be aligned')
        _validate_excluded_ids(excluded_ids_by_source, len(source_indices))

        use_tversky = self._alpha is not None and self._beta is not None
        alpha = self._alpha if self._alpha is not None else 0.7
        beta = self._beta if self._beta is not None else 0.3

        if self._indicator_matrix.shape[1] == 0:
            return tuple(() for _ in source_indices)

        source_indices_arr = np.asarray(source_indices, dtype=np.int32)
        source_block = self._indicator_matrix[source_indices_arr]

        intersections_matrix = (source_block @ self._binary_matrix_t).tocsr()

        output: list[tuple[tuple[int, float], ...]] = []
        for row_number, source_index in enumerate(source_indices):
            row_start = intersections_matrix.indptr[row_number]
            row_end = intersections_matrix.indptr[row_number + 1]

            if row_start == row_end:
                output.append(())
                continue

            candidate_indices = intersections_matrix.indices[row_start:row_end]
            intersections = intersections_matrix.data[row_start:row_end]

            valid_mask = candidate_indices != source_index
            if not np.any(valid_mask):
                output.append(())
                continue

            valid_candidates = candidate_indices[valid_mask]
            intersections = intersections[valid_mask]

            if excluded_ids_by_source is not None and excluded_ids_by_source[row_number]:
                excluded = excluded_ids_by_source[row_number]
                non_excluded_mask = ~np.isin(self._anime_ids[valid_candidates], tuple(excluded))
                if not np.any(non_excluded_mask):
                    output.append(())
                    continue
                valid_candidates = valid_candidates[non_excluded_mask]
                intersections = intersections[non_excluded_mask]

            source_total_weight = self._row_weights[source_index]
            candidate_total_weights = self._row_weights[valid_candidates]

            if use_tversky:
                left_diff = source_total_weight - intersections
                right_diff = candidate_total_weights - intersections
                denom = intersections + alpha * left_diff + beta * right_diff
                scores = np.divide(intersections, denom, out=np.zeros_like(intersections), where=denom > 0)
            else:
                denom = source_total_weight + candidate_total_weights
                scores = np.divide(2.0 * intersections, denom, out=np.zeros_like(intersections), where=denom > 0)

            valid_scores_mask = scores > 0.0
            if not np.any(valid_scores_mask):
                output.append(())
                continue

            positive_candidates = valid_candidates[valid_scores_mask]
            positive_scores = scores[valid_scores_mask]

            selected_positions = _select_top_indices(positive_candidates, positive_scores, limit, self._anime_ids)
            ranked_indices = positive_candidates[selected_positions]
            output.append(
                tuple(
                    (int(self._anime_ids[idx]), float(positive_scores[pos]))
                    for pos, idx in zip(selected_positions, ranked_indices, strict=True)
                )
            )

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
        self._anime_ids_array = np.asarray(self._anime_ids, dtype=np.int64)
        self._values = tuple(frozenset(row) for row in values)
        self._compatibility = compatibility or {}
        self._postings: dict[str, frozenset[int]] = {}
        postings: dict[str, set[int]] = {}
        for index, row in enumerate(self._values):
            for value in row:
                postings.setdefault(value, set()).add(index)
        self._postings = {value: frozenset(indices) for value, indices in postings.items()}
        self._matrix: csr_matrix | None = None
        self._row_sizes: np.ndarray | None = None
        self._compatibility_one_hot: np.ndarray | None = None
        self._compatibility_matrix: np.ndarray | None = None
        if not self._compatibility and postings:
            vocab = {value: col_idx for col_idx, value in enumerate(postings)}
            rows_idx: list[int] = []
            cols_idx: list[int] = []
            for row_idx, row in enumerate(self._values):
                for value in row:
                    rows_idx.append(row_idx)
                    cols_idx.append(vocab[value])
            data = np.ones(len(rows_idx), dtype=np.float32)
            self._matrix = csr_matrix((data, (rows_idx, cols_idx)), shape=(len(self._values), len(vocab)))
            self._row_sizes = np.asarray(self._matrix.getnnz(axis=1), dtype=np.float64)
        elif self._compatibility and postings:
            vocabulary = tuple(sorted(set(postings) | set(self._compatibility)))
            value_to_column = {value: column for column, value in enumerate(vocabulary)}
            one_hot = np.zeros((len(self._values), len(vocabulary)), dtype=np.float32)
            for row_index, row in enumerate(self._values):
                for value in row:
                    one_hot[row_index, value_to_column[value]] = 1.0
            compatibility_matrix = np.zeros((len(vocabulary), len(vocabulary)), dtype=np.float32)
            for source_value, source_column in value_to_column.items():
                targets = self._compatibility.get(source_value, {})
                for target_value, weight in targets.items():
                    target_column = value_to_column.get(target_value)
                    if target_column is not None:
                        compatibility_matrix[source_column, target_column] = float(weight)
            self._compatibility_one_hot = one_hot
            self._compatibility_matrix = compatibility_matrix

    def rank_many(
        self,
        source_indices: Sequence[int],
        *,
        limit: int,
        excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        _validate_limit(limit)
        if any(index < 0 or index >= len(self._values) for index in source_indices):
            raise ValueError('affinity source indices must be aligned')
        _validate_excluded_ids(excluded_ids_by_source, len(source_indices))
        if self._matrix is not None and self._row_sizes is not None and source_indices:
            return self._rank_many_sparse(source_indices, limit=limit, excluded_ids_by_source=excluded_ids_by_source)
        if self._compatibility_one_hot is not None and self._compatibility_matrix is not None and source_indices:
            return self._rank_many_compatible(
                source_indices, limit=limit, excluded_ids_by_source=excluded_ids_by_source
            )
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
                if excluded_ids_by_source is not None and self._anime_ids[index] in excluded_ids_by_source[len(output)]:
                    continue
                score = self._candidate_score(source, self._values[index])
                if score > 0.0:
                    scored.append((index, score))

            def sort_key(item: tuple[int, float]) -> tuple[float, int]:
                return -item[1], self._anime_ids[item[0]]

            top_scored = nsmallest(limit, scored, key=sort_key)
            output.append(tuple((self._anime_ids[index], score) for index, score in top_scored))
        return tuple(output)

    def _rank_many_sparse(
        self,
        source_indices: Sequence[int],
        *,
        limit: int,
        excluded_ids_by_source: Sequence[frozenset[int]] | None,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        if self._matrix is None or self._row_sizes is None:
            raise RuntimeError('Sparse matrix and row sizes must be initialized')
        intersections_matrix = self._matrix[list(source_indices)] @ self._matrix.T
        output: list[tuple[tuple[int, float], ...]] = []
        for pos, source_index in enumerate(source_indices):
            source_size = self._row_sizes[source_index]
            if source_size == 0.0:
                output.append(())
                continue
            row = intersections_matrix.getrow(pos)
            candidate_indices = row.indices
            if candidate_indices.size == 0:
                output.append(())
                continue
            intersections = row.data.astype(np.float64, copy=False)
            denominators = source_size + self._row_sizes[candidate_indices]
            scores = (2.0 * intersections) / denominators
            valid_mask = (candidate_indices != source_index) & (scores > 0.0)
            if excluded_ids_by_source is not None and excluded_ids_by_source[pos]:
                excluded = excluded_ids_by_source[pos]
                valid_mask &= ~np.isin(self._anime_ids_array[candidate_indices], list(excluded))
            valid_indices = candidate_indices[valid_mask]
            valid_scores = scores[valid_mask]
            if valid_indices.size == 0:
                output.append(())
                continue
            valid_ids = self._anime_ids_array[valid_indices]
            order = np.lexsort((valid_ids, -valid_scores))[:limit]
            output.append(tuple((int(valid_ids[idx]), float(valid_scores[idx])) for idx in order))
        return tuple(output)

    def _rank_many_compatible(
        self,
        source_indices: Sequence[int],
        *,
        limit: int,
        excluded_ids_by_source: Sequence[frozenset[int]] | None,
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        if self._compatibility_one_hot is None or self._compatibility_matrix is None:
            raise RuntimeError('Compatibility matrices must be initialized')
        scores_matrix = (
            self._compatibility_one_hot[list(source_indices)] @ self._compatibility_matrix
        ) @ self._compatibility_one_hot.T
        output: list[tuple[tuple[int, float], ...]] = []
        for pos, source_index in enumerate(source_indices):
            row_scores = scores_matrix[pos]
            valid_mask = row_scores > 0.0
            valid_mask[source_index] = False
            if excluded_ids_by_source is not None and excluded_ids_by_source[pos]:
                valid_mask &= ~np.isin(self._anime_ids_array, list(excluded_ids_by_source[pos]))
            valid_indices = np.flatnonzero(valid_mask)
            if valid_indices.size == 0:
                output.append(())
                continue
            valid_scores = row_scores[valid_indices]
            valid_ids = self._anime_ids_array[valid_indices]
            order = np.lexsort((valid_ids, -valid_scores))[:limit]
            output.append(tuple((int(valid_ids[idx]), float(valid_scores[idx])) for idx in order))
        return tuple(output)

    def _compatible_values(self, source_value: str) -> Iterable[str]:
        compatibility = self._compatibility.get(source_value)
        return (source_value,) if compatibility is None else compatibility.keys()

    def _candidate_score(self, source: frozenset[str], candidate: frozenset[str]) -> float:
        scores: list[float] = []
        for source_value in source:
            compatibility = self._compatibility.get(source_value)
            if compatibility is not None:
                scores.extend(compatibility.get(candidate_value, 0.0) for candidate_value in candidate)
        if scores:
            return max(scores)
        inter = len(source & candidate)
        denom = len(source) + len(candidate)
        return (2.0 * inter / denom) if denom > 0 else 0.0


def _validate_limit(limit: int) -> None:
    if limit < 1:
        raise ValueError('limit must be positive')


def _validate_excluded_ids(excluded_ids_by_source: Sequence[frozenset[int]] | None, source_count: int) -> None:
    if excluded_ids_by_source is not None and len(excluded_ids_by_source) != source_count:
        raise ValueError('exclusion sets must align with source rows')


def _remove_excluded(
    anime_ids: NDArray[np.integer], candidate_indices: NDArray[np.integer], excluded_ids: frozenset[int]
) -> NDArray[np.integer]:
    if not excluded_ids:
        return candidate_indices
    return candidate_indices[~np.isin(anime_ids[candidate_indices], tuple(excluded_ids))]


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
