"""Atomic CSV and Parquet persistence for aligned tabular artifacts."""

from collections.abc import Callable
from pathlib import Path

import polars as pl

from storage.atomic import write_atomic
from storage.errors import CorruptArtifactError, require_artifact


def write_csv(path: Path, frame: pl.DataFrame) -> None:
    """Atomically write a Polars frame as CSV."""
    _write_atomic(path, frame.write_csv)


def read_csv(path: Path) -> pl.DataFrame:
    """Read a CSV frame and normalize storage failures."""
    return _read_table(path, 'CSV', pl.read_csv)


def write_parquet(path: Path, frame: pl.DataFrame) -> None:
    """Atomically write a Polars frame as Parquet."""
    _write_atomic(path, frame.write_parquet)


def read_parquet(path: Path) -> pl.DataFrame:
    """Read a Parquet frame and normalize storage failures."""
    return _read_table(path, 'Parquet', pl.read_parquet)


def _read_table(path: Path, format_name: str, reader: Callable[[Path], pl.DataFrame]) -> pl.DataFrame:
    """Read one tabular artifact through the shared storage error boundary."""
    require_artifact(path, format_name)
    try:
        return reader(path)
    except (OSError, pl.exceptions.PolarsError) as error:
        raise CorruptArtifactError(f'Could not decode {format_name} artifact: {path}') from error


def _write_atomic(path: Path, writer: Callable[[Path], object]) -> None:
    """Write a tabular artifact to a temporary sibling before replacement."""
    try:
        write_atomic(path, writer)
    except (OSError, pl.exceptions.PolarsError) as error:
        raise CorruptArtifactError(f'Could not write tabular artifact: {path}') from error
