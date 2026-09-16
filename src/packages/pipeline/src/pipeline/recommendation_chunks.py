"""Resumable recommendation chunk generation."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import msgspec

from config import LogEvent, bind_logger, derive_payload_identity, emit_event, peak_memory_mb
from export.contracts import RecommendationChunkManifest
from processing.contracts import CanonicalAnime
from recommender.contracts import RecommendationConfig
from recommender.frozen_pipeline import Recommender
from storage.errors import StorageError
from storage.hashing import sha256_file
from storage.json_io import read_json, write_json

MIN_BATCH_SIZE = 50
MAX_BATCH_SIZE = 1_000
DEFAULT_BATCH_SIZE = 250
CHUNK_SCHEMA_VERSION = 'recommendation-chunks-v5'
log = bind_logger(package='pipeline', stage='recommendations')


class RecommendationChunkRequest(msgspec.Struct, frozen=True):
    """Configuration for one resumable recommendation export."""

    output_path: Path
    recommendation_config: RecommendationConfig
    source_identity: str = ''
    batch_size: int = DEFAULT_BATCH_SIZE
    run_id: str = '-'


def write_recommendation_chunks(
    recommender: Recommender,
    records: Sequence[CanonicalAnime],
    request: RecommendationChunkRequest,
) -> None:
    """Persist resumable recommendation IDs."""
    _validate_batch_size(request.batch_size)
    started = perf_counter()
    request.output_path.mkdir(parents=True, exist_ok=True)
    chunk_count = (len(records) + request.batch_size - 1) // request.batch_size
    manifest_path = request.output_path / 'manifest.json'
    expected_identity = _build_identity(
        records, request.recommendation_config, request.source_identity, request.batch_size, chunk_count
    )
    configuration_fingerprint = derive_payload_identity(request.source_identity)
    manifest = _load_reusable_manifest(
        manifest_path,
        expected_identity=expected_identity,
        configuration_fingerprint=configuration_fingerprint,
        records=records,
        batch_size=request.batch_size,
        chunk_count=chunk_count,
    )
    reusable = manifest is not None
    generated_chunks = 0
    log.info('Preparing {} recommendation chunks for {} records.', chunk_count, len(records))
    if manifest is None:
        _clear_chunks(request.output_path)
        manifest = _new_manifest(
            records,
            batch_size=request.batch_size,
            chunk_count=chunk_count,
            identity=expected_identity,
            configuration_fingerprint=configuration_fingerprint,
        )
        write_json(manifest_path, manifest)
    for chunk_number, start in enumerate(range(0, len(records), request.batch_size)):
        paths = _chunk_paths(request.output_path, chunk_number)
        if reusable and _chunk_is_valid(paths, manifest.checksums):
            log.info('Reusing recommendation chunk {} of {}.', chunk_number + 1, chunk_count)
            continue
        chunk_records = records[start : start + request.batch_size]
        recommendation_ids = recommender.recommend_ids_many(
            [record.mal_id for record in chunk_records],
            limit=request.recommendation_config.limit,
        )
        recommendation_ids = {str(anime_id): values for anime_id, values in recommendation_ids.items()}
        path = paths[0]
        write_json(path, recommendation_ids)
        checksums = dict(manifest.checksums)
        checksums[path.name] = sha256_file(path)
        completed = tuple(sorted({*manifest.completed_chunks, chunk_number}))
        manifest = msgspec.structs.replace(
            manifest,
            completed_chunks=completed,
            checksums=checksums,
            generated_at=datetime.now(UTC).isoformat(),
        )
        write_json(manifest_path, manifest)
        generated_chunks += 1
        log.info('Generated recommendation chunk {} of {}.', chunk_number + 1, chunk_count)
        del recommendation_ids
    emit_event(
        log,
        LogEvent(
            event_name='cache.decision',
            package='pipeline',
            stage='recommendations',
            run_id=request.run_id,
            cache_decision='reused' if generated_chunks == 0 else 'rebuilt',
            cache_reason=(
                'identity-and-all-chunks-match' if generated_chunks == 0 else 'missing-stale-or-partial-chunks'
            ),
            duration_ms=(perf_counter() - started) * 1_000,
            memory_mb=peak_memory_mb(),
            artifact_bytes=_directory_size(request.output_path),
            row_count=len(records),
        ),
    )


def _validate_batch_size(batch_size: int) -> None:
    """Reject recommendation batches outside the resumable-cache bounds."""
    if not MIN_BATCH_SIZE <= batch_size <= MAX_BATCH_SIZE:
        raise ValueError(f'batch_size must be between {MIN_BATCH_SIZE} and {MAX_BATCH_SIZE}')


def _build_identity(
    records: Sequence[CanonicalAnime],
    recommendation_config: RecommendationConfig,
    source_identity: str,
    batch_size: int,
    chunk_count: int,
) -> str:
    """Derive the identity that determines whether recommendation chunks can be reused."""
    return derive_payload_identity(
        {
            'source_identity': source_identity,
            'config': recommendation_config,
            'record_ids': [record.mal_id for record in records],
            'chunk_size': batch_size,
            'chunk_count': chunk_count,
        }
    )


def _load_reusable_manifest(
    path: Path,
    *,
    expected_identity: str,
    configuration_fingerprint: str,
    records: Sequence[CanonicalAnime] = (),
    batch_size: int | None = None,
    chunk_count: int | None = None,
) -> RecommendationChunkManifest | None:
    """Load a reusable chunk manifest only when its semantic identity matches."""
    if not path.is_file():
        return None
    try:
        manifest = read_json(path, RecommendationChunkManifest)
    except StorageError:
        return None
    if manifest.schema_version != CHUNK_SCHEMA_VERSION:
        return None
    if manifest.identity != expected_identity or manifest.configuration_fingerprint != configuration_fingerprint:
        return None
    if not _manifest_matches_request(manifest, records, batch_size, chunk_count):
        return None
    if not _completed_chunks_are_valid(manifest):
        return None
    if not _checksum_keys_are_valid(manifest):
        return None
    return manifest


def _manifest_matches_request(
    manifest: RecommendationChunkManifest,
    records: Sequence[CanonicalAnime],
    batch_size: int | None,
    chunk_count: int | None,
) -> bool:
    """Check manifest dimensions and source IDs against the current request."""
    if batch_size is not None and manifest.chunk_size != batch_size:
        return False
    if chunk_count is not None and manifest.expected_chunks != chunk_count:
        return False
    return batch_size is None or manifest.chunk_ids == _chunk_ids(records, batch_size)


def _completed_chunks_are_valid(manifest: RecommendationChunkManifest) -> bool:
    """Ensure completed chunk numbers are unique and within the manifest range."""
    expected = set(range(manifest.expected_chunks))
    completed = manifest.completed_chunks
    return len(set(completed)) == len(completed) and all(number in expected for number in completed)


def _checksum_keys_are_valid(manifest: RecommendationChunkManifest) -> bool:
    """Ensure checksum entries reference only expected chunk files."""
    expected = {f'chunk-{number:04d}.json' for number in range(manifest.expected_chunks)}
    return set(manifest.checksums).issubset(expected)


def _new_manifest(
    records: Sequence[CanonicalAnime],
    *,
    batch_size: int,
    chunk_count: int,
    identity: str,
    configuration_fingerprint: str,
) -> RecommendationChunkManifest:
    """Create an empty manifest describing the expected recommendation chunks."""
    return RecommendationChunkManifest(
        schema_version=CHUNK_SCHEMA_VERSION,
        identity=identity,
        configuration_fingerprint=configuration_fingerprint,
        chunk_size=batch_size,
        expected_chunks=chunk_count,
        chunk_ids=_chunk_ids(records, batch_size),
        completed_chunks=(),
        checksums={},
        generated_at=datetime.now(UTC).isoformat(),
    )


def _chunk_ids(records: Sequence[CanonicalAnime], batch_size: int) -> dict[str, tuple[int, ...]]:
    """Return the exact source IDs assigned to each deterministic chunk."""
    return {
        str(number): tuple(record.mal_id for record in records[start : start + batch_size])
        for number, start in enumerate(range(0, len(records), batch_size))
    }


def _clear_chunks(output_path: Path) -> None:
    """Remove generated recommendation chunks before rebuilding the cache."""
    for pattern in ('chunk-*.json', 'scores-*.json', 'explanations-*.json'):
        for path in output_path.glob(pattern):
            path.unlink(missing_ok=True)


def _chunk_paths(output_path: Path, chunk_number: int) -> tuple[Path]:
    """Return the persisted paths for one recommendation chunk."""
    suffix = f'{chunk_number:04d}.json'
    return (output_path / f'chunk-{suffix}',)


def _chunk_is_valid(paths: Sequence[Path], checksums: Mapping[str, object]) -> bool:
    """Check that every expected chunk exists and matches its recorded checksum."""
    return all(
        isinstance(checksums.get(path.name), str) and path.is_file() and sha256_file(path) == checksums[path.name]
        for path in paths
    )


def _directory_size(path: Path) -> int:
    """Return the byte size of files directly inside a recommendation directory."""
    return sum(item.stat().st_size for item in path.iterdir() if item.is_file())
