"""Frontend artifact manifest and projection validation."""

from collections.abc import Sequence
from pathlib import Path

from export.contracts import FrontendArtifactFile, RecommendationChunkManifest
from fetch.contracts import TenraiAnimeEntry
from storage.hashing import sha256_file
from storage.json_io import read_json


def file_manifest(path: Path, root: Path) -> FrontendArtifactFile:
    """Describe one generated file relative to its artifact root."""
    return FrontendArtifactFile(
        path=path.relative_to(root).as_posix(),
        bytes=path.stat().st_size,
        sha256=sha256_file(path),
    )


def validate_id_projection(path: Path, expected_ids: set[int], mode: str) -> None:
    """Verify that an ID or keyed projection contains exactly the accepted IDs."""
    if mode not in {'ids', 'keys'}:
        raise ValueError(f'unsupported projection validation mode: {mode}')
    payload = read_json(path, dict[str, object])
    if not isinstance(payload, dict):
        raise TypeError(f'{path.name} must contain an object')
    if mode == 'ids':
        values = payload.get('ids')
        if not isinstance(values, list):
            raise TypeError(f'{path.name} must contain an ids list')
        actual_values = [int(value) for value in values]
    else:
        actual_values = [int(value) for value in payload]
    if len(actual_values) != len(set(actual_values)):
        raise ValueError(f'{path.name} contains duplicate IDs')
    actual_ids = set(actual_values)
    if actual_ids != expected_ids:
        raise ValueError(f'{path.name} IDs do not match accepted processed IDs')


def validate_full_projection(paths: Sequence[Path], expected_ids: set[int]) -> None:
    """Verify that full-entry chunks contain exactly the accepted IDs."""
    actual_values: list[int] = []
    for path in paths:
        payload = read_json(path, dict[str, object])
        if not isinstance(payload, dict):
            raise TypeError(f'{path.name} must contain an object')
        actual_values.extend(int(anime_id) for anime_id in payload)
    if len(actual_values) != len(set(actual_values)):
        raise ValueError('full-entry projections contain duplicate IDs')
    actual_ids = set(actual_values)
    if actual_ids != expected_ids:
        missing_ids = sorted(expected_ids - actual_ids)
        extra_ids = sorted(actual_ids - expected_ids)
        raise ValueError(
            f'full-entry IDs do not match accepted processed IDs; missing={missing_ids[:10]}, extra={extra_ids[:10]}'
        )


def validate_full_entries(entries: Sequence[TenraiAnimeEntry]) -> None:
    """Validate the minimal identity and fields required by full-entry export."""
    for entry in entries:
        if entry.mal_id <= 0 or not entry.title.strip():
            raise ValueError('full entries contain invalid identity fields')
        if entry.type is None or entry.genres is None or entry.themes is None:
            raise ValueError('full entries are missing required Tenrai fields')


def validate_recommendation_manifest(
    manifest: RecommendationChunkManifest,
    expected_ids: Sequence[int],
    chunks_dir: Path,
    *,
    min_chunk_size: int = 1,
    max_chunk_size: int | None = None,
) -> None:
    """Verify recommendation chunk ranges, completion, and checksums."""
    if not min_chunk_size <= manifest.chunk_size or (
        max_chunk_size is not None and manifest.chunk_size > max_chunk_size
    ):
        raise ValueError('recommendation manifest has an invalid chunk size')
    expected_chunk_count = (len(expected_ids) + manifest.chunk_size - 1) // manifest.chunk_size
    if manifest.expected_chunks != expected_chunk_count:
        raise ValueError('recommendation manifest has an invalid chunk count')
    expected_chunk_ids = {
        str(number): tuple(expected_ids[start : start + manifest.chunk_size])
        for number, start in enumerate(range(0, len(expected_ids), manifest.chunk_size))
    }
    if manifest.chunk_ids != expected_chunk_ids:
        raise ValueError('recommendation chunk IDs do not match expected IDs')
    flattened_ids = tuple(anime_id for values in manifest.chunk_ids.values() for anime_id in values)
    if len(flattened_ids) != len(set(flattened_ids)) or set(flattened_ids) != set(expected_ids):
        raise ValueError('recommendation chunk IDs are incomplete or duplicated')
    expected_chunks = set(range(expected_chunk_count))
    if set(manifest.completed_chunks) != expected_chunks or len(manifest.completed_chunks) != len(expected_chunks):
        raise ValueError('recommendation manifest is incomplete')
    expected_paths = {f'chunk-{number:04d}.json' for number in expected_chunks}
    if set(manifest.checksums) != expected_paths:
        raise ValueError('recommendation manifest checksums are incomplete')
    for filename, checksum in manifest.checksums.items():
        path = chunks_dir / filename
        if not path.is_file() or sha256_file(path) != checksum:
            raise ValueError(f'recommendation chunk checksum is invalid: {filename}')
