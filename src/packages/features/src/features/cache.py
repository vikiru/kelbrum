"""Versioned metadata and validation for catalogue feature caches."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import msgspec


class FeatureCacheMetadata(msgspec.Struct, frozen=True):
    """Identity information required before reusing a feature cache."""

    schema_version: str
    model_name: str
    catalogue_length: int
    ordered_ids_hash: str
    source_snapshot_id: str | None
    configuration_hash: str
    created_at: str


def ordered_ids_hash(ordered_ids: list[int] | tuple[int, ...]) -> str:
    """Hash the exact catalogue row order used by an aligned cache."""
    payload = json.dumps([int(value) for value in ordered_ids], separators=(',', ':')).encode()
    return hashlib.sha256(payload).hexdigest()


def configuration_hash(configuration: object) -> str:
    """Hash JSON-compatible feature configuration deterministically."""
    payload = json.dumps(configuration, sort_keys=True, separators=(',', ':'), default=str).encode()
    return hashlib.sha256(payload).hexdigest()


def new_cache_metadata(
    *,
    model_name: str,
    ordered_ids: list[int] | tuple[int, ...],
    source_snapshot_id: str | None,
    configuration: object,
    schema_version: str = 'feature-cache-v1',
) -> FeatureCacheMetadata:
    """Create metadata for a newly generated aligned cache."""
    return FeatureCacheMetadata(
        schema_version=schema_version,
        model_name=model_name,
        catalogue_length=len(ordered_ids),
        ordered_ids_hash=ordered_ids_hash(ordered_ids),
        source_snapshot_id=source_snapshot_id,
        configuration_hash=configuration_hash(configuration),
        created_at=datetime.now(UTC).isoformat(),
    )


def validate_cache_metadata(
    metadata: FeatureCacheMetadata,
    *,
    model_name: str,
    ordered_ids: list[int] | tuple[int, ...],
    source_snapshot_id: str | None,
    configuration: object,
) -> None:
    """Raise when cache identity does not match the requested feature build."""
    expected = new_cache_metadata(
        model_name=model_name,
        ordered_ids=ordered_ids,
        source_snapshot_id=source_snapshot_id,
        configuration=configuration,
        schema_version=metadata.schema_version,
    )
    if metadata.model_name != expected.model_name:
        raise ValueError('feature cache model does not match the requested model')
    if metadata.catalogue_length != expected.catalogue_length:
        raise ValueError('feature cache catalogue length is stale')
    if metadata.ordered_ids_hash != expected.ordered_ids_hash:
        raise ValueError('feature cache row order is stale')
    if metadata.source_snapshot_id != expected.source_snapshot_id:
        raise ValueError('feature cache source snapshot is stale')
    if metadata.configuration_hash != expected.configuration_hash:
        raise ValueError('feature cache configuration is stale')


def metadata_path(cache_path: Path) -> Path:
    """Return the sidecar metadata path for a feature cache file."""
    return cache_path.with_suffix(cache_path.suffix + '.metadata.json')


def encode_metadata(metadata: FeatureCacheMetadata) -> bytes:
    """Encode cache metadata as compact typed JSON for a sidecar writer."""
    return msgspec.json.encode(metadata)


def decode_metadata(payload: bytes) -> FeatureCacheMetadata:
    """Decode and validate the typed cache metadata envelope."""
    return msgspec.json.decode(payload, type=FeatureCacheMetadata)
