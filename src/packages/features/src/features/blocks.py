"""Deterministic feature blocks with explicit metadata."""

import msgspec
import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix, hstack


class FeatureBlock(msgspec.Struct, frozen=True):
    name: str
    kind: str
    values: NDArray[np.floating] | csr_matrix
    column_names: tuple[str, ...]
    source_properties: tuple[str, ...]
    row_available: NDArray[np.bool_] | None = None
    dimension_available: NDArray[np.bool_] | None = None

    def availability(self) -> NDArray[np.bool_]:
        """Return explicit row availability, with legacy value fallback."""
        if self.row_available is not None:
            if self.row_available.shape != (self.values.shape[0],):
                raise ValueError(f'feature availability does not match block rows: {self.name}')
            return self.row_available
        if isinstance(self.values, csr_matrix):
            return np.asarray(self.values.getnnz(axis=1) > 0).ravel()
        return np.any(np.asarray(self.values) != 0, axis=1)


class FeatureBundle(msgspec.Struct, frozen=True):
    anime_ids: NDArray[np.int64]
    blocks: tuple[FeatureBlock, ...]

    def __post_init__(self) -> None:
        if self.anime_ids.ndim != 1:
            raise ValueError('anime_ids must be one-dimensional')
        if any(block.values.shape[0] != self.anime_ids.shape[0] for block in self.blocks):
            raise ValueError('every feature block must preserve anime-ID alignment')
        if len(np.unique(self.anime_ids)) != self.anime_ids.size:
            raise ValueError('anime_ids must be unique')
        if any(block.values.shape[1] != len(block.column_names) for block in self.blocks):
            raise ValueError('feature column metadata must match matrix width')
        for block in self.blocks:
            if block.row_available is not None and block.row_available.shape != self.anime_ids.shape:
                raise ValueError(f'feature availability must align with anime IDs: {block.name}')
            if block.dimension_available is not None and block.dimension_available.shape != block.values.shape:
                raise ValueError(f'feature dimension availability must align with values: {block.name}')

    def matrix(self) -> NDArray[np.float32] | csr_matrix:
        """Return all blocks as one row-aligned matrix."""
        matrices = [block.values for block in self.blocks]
        if any(isinstance(matrix, csr_matrix) for matrix in matrices):
            sparse_matrices = [matrix if isinstance(matrix, csr_matrix) else csr_matrix(matrix) for matrix in matrices]
            return csr_matrix(hstack(sparse_matrices, format='csr', dtype=np.float32))
        dense_matrices = [np.asarray(matrix) for matrix in matrices]
        return np.concatenate(dense_matrices, axis=1).astype(np.float32, copy=False)

    def block(self, name: str) -> FeatureBlock | None:
        """Return one named block without exposing the bundle's storage details."""
        return next((block for block in self.blocks if block.name == name), None)
