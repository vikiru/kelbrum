"""Build and validate deterministic frontend search artifacts."""

import math
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from anime_catalogue import order_catalogue_frame
from processing.contracts import FilterMetadata, NumericRange, ProcessingArtifactManifest
from storage.json_io import write_json

NUMERIC_COLUMNS = ('score', 'year', 'episodes', 'duration_minutes')
POSTING_COLUMNS = ('genres', 'themes', 'studios')


def build_filter_metadata(frame: pl.DataFrame) -> FilterMetadata:
    """Build posting lists, aligned numeric arrays, and numeric ranges."""
    _require_columns(frame, ('mal_id', *POSTING_COLUMNS, *NUMERIC_COLUMNS))
    ordered = order_catalogue_frame(frame)
    anime_ids = [int(value) for value in ordered.get_column('mal_id').to_list()]
    posting_lists = {column: _posting_list(ordered, column, anime_ids) for column in POSTING_COLUMNS}
    numeric_arrays = {column: tuple(ordered.get_column(column).to_list()) for column in NUMERIC_COLUMNS}
    numeric_ranges = {
        column: NumericRange(
            minimum=_finite_min(values),
            maximum=_finite_max(values),
        )
        for column, values in numeric_arrays.items()
    }
    return FilterMetadata(
        anime_ids=tuple(anime_ids),
        posting_lists={
            column: {value: tuple(ids) for value, ids in lists.items()} for column, lists in posting_lists.items()
        },
        numeric_arrays=numeric_arrays,
        numeric_ranges=numeric_ranges,
    )


def write_filter_artifacts(
    frame: pl.DataFrame,
    output_dir: Path,
    *,
    canonical_parquet: Path,
    schema_version: str = 'search-v1',
) -> ProcessingArtifactManifest:
    """Validate and atomically write filter metadata plus its manifest."""
    if not canonical_parquet.is_file():
        raise FileNotFoundError(f'canonical Parquet does not exist: {canonical_parquet}')
    metadata = build_filter_metadata(frame)
    validate_filter_metadata(frame, metadata)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'artifact-manifest.json').unlink(missing_ok=True)
    metadata_path = output_dir / 'filter-metadata.json'
    write_json(metadata_path, metadata)
    manifest = ProcessingArtifactManifest(
        schema_version=schema_version,
        fetched_date=datetime.now(UTC).isoformat(),
        anime_count=frame.height,
        artifacts=(('filter-metadata', metadata_path.name),),
    )
    write_json(output_dir / 'artifact-manifest.json', manifest)
    return manifest


def validate_filter_metadata(frame: pl.DataFrame, metadata: FilterMetadata) -> None:
    """Verify IDs, posting-list references, array lengths, and ranges."""
    _require_columns(frame, ('mal_id', *POSTING_COLUMNS, *NUMERIC_COLUMNS))
    expected_ids = [int(value) for value in order_catalogue_frame(frame).get_column('mal_id').to_list()]
    if metadata.anime_ids != tuple(expected_ids):
        raise ValueError('filter metadata anime_ids do not match canonical Parquet order')
    for column in NUMERIC_COLUMNS:
        if len(metadata.numeric_arrays[column]) != len(expected_ids):
            raise ValueError(f'filter metadata array has invalid length: {column}')
    valid_ids = set(expected_ids)
    for column in POSTING_COLUMNS:
        for ids in metadata.posting_lists[column].values():
            if not set(ids).issubset(valid_ids):
                raise ValueError(f'posting list contains an unknown anime ID: {column}')


def _posting_list(frame: pl.DataFrame, column: str, anime_ids: list[int]) -> dict[str, list[int]]:
    """Build sorted ID postings for one normalized categorical column."""
    lists = frame.get_column(column).to_list()
    result: dict[str, list[int]] = {}
    for anime_id, values in zip(anime_ids, lists, strict=True):
        for value in _values(values):
            result.setdefault(value, []).append(anime_id)
    return {key: result[key] for key in sorted(result)}


def _values(value: object) -> Iterable[str]:
    """Normalize list or comma-separated categorical values for indexing."""
    if value is None:
        return ()
    if isinstance(value, str):
        return (item.strip() for item in value.split(',') if item.strip())
    if isinstance(value, (list, tuple)):
        return (str(item).strip() for item in value if str(item).strip())
    return ()


def _finite_min(values: Sequence[object]) -> float | None:
    """Return the minimum finite numeric value or no range when none exists."""
    finite = _finite_values(values)
    return min(finite) if finite else None


def _finite_max(values: Sequence[object]) -> float | None:
    """Return the maximum finite numeric value or no range when none exists."""
    finite = _finite_values(values)
    return max(finite) if finite else None


def _finite_values(values: Sequence[object]) -> list[float]:
    """Filter nullable and non-finite values before computing numeric ranges."""
    finite: list[float] = []
    for value in values:
        if value is None:
            continue
        if not isinstance(value, (int, float)):
            continue
        numeric = float(value)
        if math.isfinite(numeric):
            finite.append(numeric)
    return finite


def _require_columns(frame: pl.DataFrame, columns: tuple[str, ...]) -> None:
    """Reject frames that cannot produce the requested processing artifact."""
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f'canonical Parquet is missing required artifact columns: {", ".join(missing)}')
