"""Deterministic, atomic JSON persistence."""

from pathlib import Path

import msgspec
import orjson

from storage.atomic import write_atomic
from storage.errors import CorruptArtifactError, require_artifact


def write_json(path: Path, value: object) -> None:
    """Atomically write sorted, minified JSON."""
    payload = orjson.dumps(msgspec.to_builtins(value), option=orjson.OPT_SORT_KEYS)
    write_atomic(path, lambda temporary_path: temporary_path.write_bytes(payload))


def read_json[T](path: Path, target_type: type[T]) -> T:
    """Read and validate JSON using the caller's authoritative type."""
    require_artifact(path, 'JSON')
    try:
        return msgspec.convert(orjson.loads(path.read_bytes()), type=target_type)
    except (OSError, orjson.JSONDecodeError, msgspec.ValidationError, TypeError) as error:
        raise CorruptArtifactError(f'Could not decode JSON artifact: {path}') from error
