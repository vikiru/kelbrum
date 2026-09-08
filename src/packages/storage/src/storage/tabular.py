"""Atomic CSV and Parquet persistence for aligned tabular artifacts."""

import tempfile
from collections.abc import Callable
from pathlib import Path

import polars as pl

from storage.errors import CorruptArtifactError, MissingArtifactError


def write_csv(path: Path, frame: pl.DataFrame) -> None:
    """Atomically write a Polars frame as CSV."""
    _write_atomic(path, frame.write_csv)


def read_csv(path: Path) -> pl.DataFrame:
    """Read a CSV frame and normalize storage failures."""
    if not path.is_file():
        raise MissingArtifactError(f'CSV artifact does not exist: {path}')
    try:
        return pl.read_csv(path)
    except (OSError, pl.exceptions.PolarsError) as error:
        raise CorruptArtifactError(f'Could not decode CSV artifact: {path}') from error


def write_parquet(path: Path, frame: pl.DataFrame) -> None:
    """Atomically write a Polars frame as Parquet."""
    _write_atomic(path, frame.write_parquet)


def read_parquet(path: Path) -> pl.DataFrame:
    """Read a Parquet frame and normalize storage failures."""
    if not path.is_file():
        raise MissingArtifactError(f'Parquet artifact does not exist: {path}')
    try:
        return pl.read_parquet(path)
    except (OSError, pl.exceptions.PolarsError) as error:
        raise CorruptArtifactError(f'Could not decode Parquet artifact: {path}') from error


def _write_atomic(path: Path, writer: Callable[[Path], object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f'.{path.name}.', dir=path.parent) as directory:
        temporary_path = Path(directory) / path.name
        try:
            writer(temporary_path)
            temporary_path.replace(path)
        except (OSError, pl.exceptions.PolarsError) as error:
            raise CorruptArtifactError(f'Could not write tabular artifact: {path}') from error
