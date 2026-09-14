"""Resumable recommendation chunk generation."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from gc import collect
from hashlib import sha256
from pathlib import Path
from typing import cast

import msgspec

from config import bind_logger
from models.contracts import RecommendationConfig
from models.tenrai import CanonicalAnime
from recommender.frozen_pipeline import Recommender
from storage.json_io import read_json, write_json

MIN_BATCH_SIZE = 50
MAX_BATCH_SIZE = 1_000
DEFAULT_BATCH_SIZE = 250
CHUNK_SCHEMA_VERSION = 'recommendation-chunks-v4'
log = bind_logger(package='pipeline', stage='recommendations')


def write_recommendation_chunks(
    recommender: Recommender,
    records: Sequence[CanonicalAnime],
    *,
    output_path: Path,
    recommendation_config: RecommendationConfig,
    source_identity: str = '',
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """Persist resumable recommendation IDs."""
    _validate_batch_size(batch_size)
    output_path.mkdir(parents=True, exist_ok=True)
    chunk_count = (len(records) + batch_size - 1) // batch_size
    manifest_path = output_path / 'manifest.json'
    expected_identity = _build_identity(records, recommendation_config, source_identity, batch_size, chunk_count)
    configuration_fingerprint = sha256(source_identity.encode('utf-8')).hexdigest()
    manifest = _load_reusable_manifest(
        manifest_path,
        expected_identity=expected_identity,
        configuration_fingerprint=configuration_fingerprint,
    )
    reusable = manifest is not None
    log.info('Preparing {} recommendation chunks for {} records.', chunk_count, len(records))
    if manifest is None:
        _clear_chunks(output_path)
        manifest = _new_manifest(
            records,
            batch_size=batch_size,
            chunk_count=chunk_count,
            identity=expected_identity,
            configuration_fingerprint=configuration_fingerprint,
        )
    for chunk_number, start in enumerate(range(0, len(records), batch_size)):
        paths = _chunk_paths(output_path, chunk_number)
        checksums = cast('dict[str, object]', manifest['checksums'])
        if reusable and _chunk_is_valid(paths, checksums):
            log.info('Reusing recommendation chunk {} of {}.', chunk_number + 1, chunk_count)
            continue
        chunk_records = records[start : start + batch_size]
        recommendation_ids = recommender.recommend_ids_many(
            [record.mal_id for record in chunk_records],
            limit=recommendation_config.limit,
        )
        recommendation_ids = {str(anime_id): values for anime_id, values in recommendation_ids.items()}
        path = paths[0]
        write_json(path, recommendation_ids)
        checksums[path.name] = _sha256_file(path)
        completed = cast('list[int]', manifest['completed_chunks'])
        completed.append(chunk_number)
        manifest['generated_at'] = datetime.now(UTC).isoformat()
        write_json(manifest_path, manifest)
        log.info('Generated recommendation chunk {} of {}.', chunk_number + 1, chunk_count)
        del recommendation_ids
        collect()


def _validate_batch_size(batch_size: int) -> None:
    if not MIN_BATCH_SIZE <= batch_size <= MAX_BATCH_SIZE:
        raise ValueError(f'batch_size must be between {MIN_BATCH_SIZE} and {MAX_BATCH_SIZE}')


def _build_identity(
    records: Sequence[CanonicalAnime],
    recommendation_config: RecommendationConfig,
    source_identity: str,
    batch_size: int,
    chunk_count: int,
) -> str:
    return sha256(
        msgspec.json.encode(
            {
                'source_identity': source_identity,
                'config': msgspec.to_builtins(recommendation_config),
                'record_ids': [record.mal_id for record in records],
                'chunk_size': batch_size,
                'chunk_count': chunk_count,
            }
        )
    ).hexdigest()


def _load_reusable_manifest(
    path: Path,
    *,
    expected_identity: str,
    configuration_fingerprint: str,
) -> dict[str, object] | None:
    if not path.is_file():
        return None
    manifest = read_json(path, dict[str, object])
    if (
        manifest.get('schema_version') == CHUNK_SCHEMA_VERSION
        and manifest.get('identity') == expected_identity
        and manifest.get('configuration_fingerprint') == configuration_fingerprint
        and isinstance(manifest.get('checksums'), dict)
    ):
        return manifest
    return None


def _new_manifest(
    records: Sequence[CanonicalAnime],
    *,
    batch_size: int,
    chunk_count: int,
    identity: str,
    configuration_fingerprint: str,
) -> dict[str, object]:
    return {
        'schema_version': CHUNK_SCHEMA_VERSION,
        'identity': identity,
        'configuration_fingerprint': configuration_fingerprint,
        'chunk_size': batch_size,
        'expected_chunks': chunk_count,
        'chunk_ids': {
            str(number): [record.mal_id for record in records[start : start + batch_size]]
            for number, start in enumerate(range(0, len(records), batch_size))
        },
        'completed_chunks': [],
        'checksums': {},
    }


def _clear_chunks(output_path: Path) -> None:
    for pattern in ('chunk-*.json', 'scores-*.json', 'explanations-*.json'):
        for path in output_path.glob(pattern):
            path.unlink(missing_ok=True)


def _chunk_paths(output_path: Path, chunk_number: int) -> tuple[Path]:
    suffix = f'{chunk_number:04d}.json'
    return (output_path / f'chunk-{suffix}',)


def _chunk_is_valid(paths: Sequence[Path], checksums: Mapping[str, object]) -> bool:
    return all(
        isinstance(checksums.get(path.name), str) and path.is_file() and _sha256_file(path) == checksums[path.name]
        for path in paths
    )


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()
