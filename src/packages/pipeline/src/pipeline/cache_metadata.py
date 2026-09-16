"""Typed compatibility metadata for pipeline-owned derived artifacts."""

from collections.abc import Sequence

import msgspec

from config import derive_payload_identity


class CacheCompatibilityError(ValueError):
    """Raised when a derived artifact does not match the requested inputs."""


class CacheMetadata(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Semantic identity and shape information required for cache reuse."""

    artifact_kind: str
    schema_identity: str
    source_identity: str
    ordered_ids_hash: str
    row_count: int
    shape: tuple[int, ...]
    content_hash: str
    configuration_identity: str
    policy_identity: str
    producer_identity: str

    def __post_init__(self) -> None:
        if not self.artifact_kind.strip():
            raise ValueError('cache artifact kind cannot be empty')
        if self.row_count < 0:
            raise ValueError('cache row count cannot be negative')
        if not self.shape or self.shape[0] != self.row_count or any(dimension < 0 for dimension in self.shape):
            raise ValueError('cache shape must begin with the non-negative row count')
        if any(not value.strip() for value in (self.schema_identity, self.source_identity, self.content_hash)):
            raise ValueError('cache identity fields cannot be empty')


def build_cache_metadata(
    *,
    artifact_kind: str,
    schema_identity: str,
    source_identity: str,
    ordered_ids: Sequence[int],
    shape: Sequence[int],
    content_hash: str,
    configuration_identity: str = '-',
    policy_identity: str = '-',
    producer_identity: str = '-',
) -> CacheMetadata:
    """Build metadata from explicit semantic inputs without touching the filesystem."""
    normalized_ids = tuple(ordered_ids)
    normalized_shape = tuple(shape)
    return CacheMetadata(
        artifact_kind=artifact_kind,
        schema_identity=schema_identity,
        source_identity=source_identity,
        ordered_ids_hash=hash_ordered_ids(normalized_ids),
        row_count=len(normalized_ids),
        shape=normalized_shape,
        content_hash=content_hash,
        configuration_identity=configuration_identity,
        policy_identity=policy_identity,
        producer_identity=producer_identity,
    )


def hash_ordered_ids(ordered_ids: Sequence[int]) -> str:
    """Hash the exact row order used by an aligned artifact."""
    return derive_payload_identity(tuple(ordered_ids))


def validate_cache_metadata(actual: CacheMetadata, expected: CacheMetadata) -> None:
    """Reject a cache unless every semantic and structural field matches."""
    fields = (
        'artifact_kind',
        'schema_identity',
        'source_identity',
        'ordered_ids_hash',
        'row_count',
        'shape',
        'content_hash',
        'configuration_identity',
        'policy_identity',
        'producer_identity',
    )
    for field in fields:
        if getattr(actual, field) != getattr(expected, field):
            raise CacheCompatibilityError(f'cache {field} is incompatible')
