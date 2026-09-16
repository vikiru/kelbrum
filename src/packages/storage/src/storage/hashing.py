"""Streaming file hashing primitives."""

from hashlib import sha256
from pathlib import Path

DEFAULT_HASH_CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path, *, chunk_size: int = DEFAULT_HASH_CHUNK_SIZE) -> str:
    """Return a SHA-256 digest without materializing the file in memory."""
    if chunk_size < 1:
        raise ValueError('chunk_size must be positive')
    digest = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b''):
            digest.update(chunk)
    return digest.hexdigest()
