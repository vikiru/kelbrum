"""Atomic dense and sparse numerical persistence."""

import os
import tempfile
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from storage.errors import CorruptArtifactError, MissingArtifactError


def write_array(path: Path, values: NDArray[np.generic]) -> None:
    """Atomically write a NumPy array."""
    _atomic_numpy_write(path, values, compressed=False)


def read_array(path: Path) -> NDArray[np.generic]:
    if not path.is_file():
        raise MissingArtifactError(f'Array artifact does not exist: {path}')
    try:
        return np.load(path, allow_pickle=False)
    except (OSError, ValueError) as error:
        raise CorruptArtifactError(f'Could not read array artifact: {path}') from error


def write_sparse(path: Path, values: sparse.spmatrix) -> None:
    """Atomically write a SciPy sparse matrix."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{path.stem}.', suffix='.npz', dir=path.parent)
    os.close(descriptor)
    try:
        sparse.save_npz(temporary_name, values)
        Path(temporary_name).replace(path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def read_sparse(path: Path) -> sparse.csr_matrix:
    if not path.is_file():
        raise MissingArtifactError(f'Sparse artifact does not exist: {path}')
    try:
        return sparse.load_npz(path).tocsr()
    except (OSError, ValueError) as error:
        raise CorruptArtifactError(f'Could not read sparse artifact: {path}') from error


def _atomic_numpy_write(path: Path, values: NDArray[np.generic], *, compressed: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    os.close(descriptor)
    try:
        with Path(temporary_name).open('wb') as stream:
            if compressed:
                np.savez_compressed(stream, values=values)
            else:
                np.save(stream, values, allow_pickle=False)
            stream.flush()
            os.fsync(stream.fileno())
        Path(temporary_name).replace(path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise
