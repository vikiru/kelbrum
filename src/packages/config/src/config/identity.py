"""Deterministic identities for stages, caches, and generated artifacts."""

from collections.abc import Mapping
from hashlib import sha256

import msgspec
import orjson


class IdentityInputs(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Semantic inputs that determine whether an artifact can be reused."""

    contract_identity: str
    source_identity: str
    ordered_ids: tuple[int, ...] = ()
    configuration_identity: str = '-'
    policy_identity: str = '-'
    registry_identity: str = '-'
    producer_identity: str = '-'


def derive_identity(inputs: IdentityInputs) -> str:
    """Return a stable identity from explicit semantic and implementation inputs."""
    return derive_payload_identity(inputs)


def derive_stage_identity(
    stage: str,
    *,
    contract_identity: str,
    source_identity: str,
    ordered_ids: tuple[int, ...] = (),
    configuration_identity: str = '-',
    policy_identity: str = '-',
    registry_identity: str = '-',
    producer_identity: str = '-',
) -> str:
    """Build one identity for a derived stage from its semantic inputs."""
    if not stage.strip():
        raise ValueError('stage identity requires a non-empty stage')
    return derive_identity(
        IdentityInputs(
            contract_identity=f'{stage}:{contract_identity}',
            source_identity=source_identity,
            ordered_ids=ordered_ids,
            configuration_identity=configuration_identity,
            policy_identity=policy_identity,
            registry_identity=registry_identity,
            producer_identity=producer_identity,
        )
    )


def derive_payload_identity(value: object) -> str:
    """Return a stable hash for a JSON-compatible semantic payload."""
    payload = orjson.dumps(_canonicalize(value), option=orjson.OPT_SORT_KEYS)
    return sha256(payload).hexdigest()


def _canonicalize(value: object) -> object:
    """Normalize unordered containers before serializing an identity payload."""
    if isinstance(value, msgspec.Struct):
        return {field.name: _canonicalize(getattr(value, field.name)) for field in msgspec.structs.fields(type(value))}
    if isinstance(value, Mapping):
        return {key: _canonicalize(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        items = [_canonicalize(item) for item in value]
        return sorted(items, key=_canonical_sort_key)
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_canonicalize(item) for item in value)
    return msgspec.to_builtins(value)


def _canonical_sort_key(value: object) -> bytes:
    return orjson.dumps(value, option=orjson.OPT_SORT_KEYS)
