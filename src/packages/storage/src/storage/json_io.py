"""Deterministic, atomic JSON persistence."""

import os
import tempfile
from pathlib import Path

import msgspec
import orjson

from storage.errors import CorruptArtifactError, MissingArtifactError


def write_json(path: Path, value: object) -> None:
    """Atomically write sorted, minified JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = orjson.dumps(msgspec.to_builtins(value), option=orjson.OPT_SORT_KEYS)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        Path(temporary_name).replace(path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def read_json[T](path: Path, target_type: type[T]) -> T:
    """Read and validate JSON using the caller's authoritative type."""
    if not path.is_file():
        raise MissingArtifactError(f'JSON artifact does not exist: {path}')
    try:
        return msgspec.json.decode(path.read_bytes(), type=target_type)
    except (OSError, msgspec.DecodeError, msgspec.ValidationError) as error:
        raise CorruptArtifactError(f'Could not decode JSON artifact: {path}') from error
