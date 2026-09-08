"""Validation and export of completed recommendation chunks."""

from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path

from export.frontend import write_catalogue_artifacts
from models.tenrai import CanonicalAnime, TenraiAnimeEntry
from storage.json_io import read_json

MIN_RECOMMENDATION_BATCH_SIZE = 50
MAX_RECOMMENDATION_BATCH_SIZE = 1_000


def export_catalogue_stage(
    records: Sequence[CanonicalAnime],
    full_entries: Sequence[TenraiAnimeEntry],
    *,
    recommendation_path: Path,
    output_dir: Path,
    provenance: Mapping[str, object] | None = None,
) -> None:
    """Build frontend artifacts from complete, checksummed recommendation chunks."""
    manifest = read_json(recommendation_path / 'manifest.json', dict[str, object])
    if manifest.get('schema_version') != 'recommendation-chunks-v3':
        raise ValueError('recommendation manifest does not include score and explanation sidecars')
    chunk_size = manifest.get('chunk_size')
    if not isinstance(chunk_size, int) or not (
        MIN_RECOMMENDATION_BATCH_SIZE <= chunk_size <= MAX_RECOMMENDATION_BATCH_SIZE
    ):
        raise ValueError('recommendation manifest has an invalid chunk size')
    expected_chunks = (len(records) + chunk_size - 1) // chunk_size
    completed_chunks = manifest.get('completed_chunks')
    if manifest.get('expected_chunks') != expected_chunks or completed_chunks != list(range(expected_chunks)):
        raise ValueError('recommendation chunks are incomplete')
    checksums = manifest.get('checksums')
    if not isinstance(checksums, dict) or any(
        not isinstance(checksum, str)
        or not (recommendation_path / filename).is_file()
        or _sha256_file(recommendation_path / filename) != checksum
        for filename, checksum in checksums.items()
        if isinstance(filename, str)
    ):
        raise ValueError('recommendation chunk checksums are invalid')
    write_catalogue_artifacts(
        records,
        full_entries=full_entries,
        recommendation_chunks=recommendation_path,
        provenance=provenance,
        output_dir=output_dir,
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()
