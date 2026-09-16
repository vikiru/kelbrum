"""Versioned metadata and validation for catalogue feature caches."""

from pathlib import Path

import msgspec
import orjson

from config import derive_payload_identity
from features.tag_assignment import tag_assignment_registry_identity
from features.tags import tag_registry_identity

FEATURE_ALGORITHM_DESCRIPTOR = {
    'text_features': 'bm25-idf-and-latent-synopsis',
    'numeric_features': 'configured-transforms-and-buckets',
    'missingness': 'explicit-row-and-dimension-availability',
}


class FeatureCacheMetadata(msgspec.Struct, frozen=True):
    """Identity information required before reusing a feature cache."""

    schema_version: str
    model_name: str
    catalogue_length: int
    ordered_ids_hash: str
    source_snapshot_id: str | None
    configuration_hash: str


def ordered_ids_hash(ordered_ids: list[int] | tuple[int, ...]) -> str:
    """Hash the exact catalogue row order used by an aligned cache."""
    return derive_payload_identity(ordered_ids)


def configuration_hash(
    configuration: object,
    *,
    tag_vocabulary_identity: str | None = None,
    tag_assignment_identity: str | None = None,
) -> str:
    """Hash JSON-compatible feature configuration deterministically."""
    return derive_payload_identity(
        {
            'feature_algorithm': FEATURE_ALGORITHM_DESCRIPTOR,
            'configuration': configuration,
            'tag_vocabulary_identity': tag_vocabulary_identity or tag_registry_identity(),
            'tag_assignment_identity': tag_assignment_identity or tag_assignment_registry_identity(),
        }
    )


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
    )


def validate_cache_metadata(
    metadata: FeatureCacheMetadata,
    *,
    model_name: str,
    ordered_ids: list[int] | tuple[int, ...],
    source_snapshot_id: str | None,
    configuration: object,
    schema_version: str = 'feature-cache-v1',
) -> None:
    """Raise when cache identity does not match the requested feature build."""
    expected = new_cache_metadata(
        model_name=model_name,
        ordered_ids=ordered_ids,
        source_snapshot_id=source_snapshot_id,
        configuration=configuration,
        schema_version=schema_version,
    )
    if metadata.schema_version != expected.schema_version:
        raise ValueError('feature cache schema is incompatible')
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
    return orjson.dumps(msgspec.to_builtins(metadata), option=orjson.OPT_SORT_KEYS)


def decode_metadata(payload: bytes) -> FeatureCacheMetadata:
    """Decode and validate the typed cache metadata envelope."""
    return msgspec.convert(orjson.loads(payload), type=FeatureCacheMetadata)
