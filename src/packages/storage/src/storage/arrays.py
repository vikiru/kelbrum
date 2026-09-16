"""Atomic dense and sparse numerical persistence."""

from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from storage.atomic import write_atomic
from storage.errors import CorruptArtifactError, require_artifact


def write_array(path: Path, values: NDArray[np.generic]) -> None:
    """Atomically write a NumPy array."""
    _atomic_numpy_write(path, values, compressed=False)


def read_array(path: Path) -> NDArray[np.generic]:
    """Read a dense NumPy array and normalize missing or corrupt storage errors."""
    require_artifact(path, 'Array')
    try:
        return np.load(path, allow_pickle=False)
    except (OSError, ValueError) as error:
        raise CorruptArtifactError(f'Could not read array artifact: {path}') from error


def write_sparse(path: Path, values: sparse.spmatrix) -> None:
    """Atomically write a SciPy sparse matrix."""
    write_atomic(path, lambda temporary_path: sparse.save_npz(temporary_path, values))


def read_sparse(path: Path) -> sparse.csr_matrix:
    """Read a sparse matrix and normalize missing or corrupt storage errors."""
    require_artifact(path, 'Sparse')
    try:
        return sparse.load_npz(path).tocsr()
    except (OSError, ValueError) as error:
        raise CorruptArtifactError(f'Could not read sparse artifact: {path}') from error


def _atomic_numpy_write(path: Path, values: NDArray[np.generic], *, compressed: bool) -> None:
    """Write dense NumPy values atomically, optionally using compressed storage."""

    def write_values(temporary_path: Path) -> None:
        with temporary_path.open('wb') as stream:
            if compressed:
                np.savez_compressed(stream, values=values)
            else:
                np.save(stream, values, allow_pickle=False)

    write_atomic(path, write_values)
