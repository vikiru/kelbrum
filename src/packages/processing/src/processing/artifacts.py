"""Build and validate deterministic frontend search artifacts."""

import math
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import polars as pl

from anime_catalogue import order_catalogue_frame
from models.artifacts import ArtifactManifest, NumericRange
from storage.json_io import write_json

NUMERIC_COLUMNS = ('score', 'year', 'episodes', 'duration_minutes')
POSTING_COLUMNS = ('genres', 'themes', 'studios')


def build_filter_metadata(frame: pl.DataFrame) -> dict[str, object]:
    """Build posting lists, aligned numeric arrays, and numeric ranges."""
    _require_columns(frame, ('mal_id', *POSTING_COLUMNS, *NUMERIC_COLUMNS))
    ordered = order_catalogue_frame(frame)
    anime_ids = [int(value) for value in ordered.get_column('mal_id').to_list()]
    posting_lists = {column: _posting_list(ordered, column, anime_ids) for column in POSTING_COLUMNS}
    numeric_arrays = {column: list(ordered.get_column(column).to_list()) for column in NUMERIC_COLUMNS}
    numeric_ranges = {
        column: NumericRange(
            minimum=_finite_min(values),
            maximum=_finite_max(values),
        )
        for column, values in numeric_arrays.items()
    }
    return {
        'anime_ids': anime_ids,
        'posting_lists': posting_lists,
        'numeric_arrays': numeric_arrays,
        'numeric_ranges': numeric_ranges,
    }


def write_filter_artifacts(
    frame: pl.DataFrame,
    output_dir: Path,
    *,
    canonical_parquet: Path,
    schema_version: str = 'search-v1',
) -> ArtifactManifest:
    """Validate and atomically write filter metadata plus its manifest."""
    if not canonical_parquet.is_file():
        raise FileNotFoundError(f'canonical Parquet does not exist: {canonical_parquet}')
    metadata = build_filter_metadata(frame)
    validate_filter_metadata(frame, metadata)
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = output_dir / 'filter-metadata.json'
    write_json(metadata_path, metadata)
    manifest = ArtifactManifest(
        schema_version=schema_version,
        fetched_date=datetime.now(UTC).isoformat(),
        anime_count=frame.height,
        artifacts=(('filter-metadata', str(metadata_path.name)),),
    )
    write_json(output_dir / 'artifact-manifest.json', manifest)
    return manifest


def validate_filter_metadata(frame: pl.DataFrame, metadata: dict[str, object]) -> None:
    """Verify IDs, posting-list references, array lengths, and ranges."""
    _require_columns(frame, ('mal_id', *POSTING_COLUMNS, *NUMERIC_COLUMNS))
    expected_ids = [int(value) for value in order_catalogue_frame(frame).get_column('mal_id').to_list()]
    if metadata.get('anime_ids') != expected_ids:
        raise ValueError('filter metadata anime_ids do not match canonical Parquet order')
    numeric_arrays = cast('dict[str, list[object]]', metadata['numeric_arrays'])
    for column in NUMERIC_COLUMNS:
        if len(numeric_arrays[column]) != len(expected_ids):
            raise ValueError(f'filter metadata array has invalid length: {column}')
    posting_lists = cast('dict[str, dict[str, list[int]]]', metadata['posting_lists'])
    valid_ids = set(expected_ids)
    for column in POSTING_COLUMNS:
        for ids in posting_lists[column].values():
            if not set(ids).issubset(valid_ids):
                raise ValueError(f'posting list contains an unknown anime ID: {column}')


def _posting_list(frame: pl.DataFrame, column: str, anime_ids: list[int]) -> dict[str, list[int]]:
    lists = frame.get_column(column).to_list()
    result: dict[str, list[int]] = {}
    for anime_id, values in zip(anime_ids, lists, strict=True):
        for value in _values(values):
            result.setdefault(value, []).append(anime_id)
    return {key: result[key] for key in sorted(result)}


def _values(value: object) -> Iterable[str]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (item.strip() for item in value.split(',') if item.strip())
    if isinstance(value, list):
        return (str(item).strip() for item in value if str(item).strip())
    return ()


def _finite_min(values: list[object]) -> float | None:
    finite = _finite_values(values)
    return min(finite) if finite else None


def _finite_max(values: list[object]) -> float | None:
    finite = _finite_values(values)
    return max(finite) if finite else None


def _finite_values(values: list[object]) -> list[float]:
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
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f'canonical Parquet is missing required artifact columns: {", ".join(missing)}')
