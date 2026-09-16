"""Shared atomic file replacement primitive."""

import os
import tempfile
from collections.abc import Callable
from pathlib import Path


def write_atomic(path: Path, writer: Callable[[Path], object]) -> None:
    """Write a temporary sibling, flush it, then replace the destination."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f'.{path.name}.', suffix=path.suffix, dir=path.parent)
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        writer(temporary_path)
        with temporary_path.open('rb') as stream:
            stream.flush()
            os.fsync(stream.fileno())
        temporary_path.replace(path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
