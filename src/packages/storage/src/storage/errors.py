"""Storage boundary exceptions."""

from pathlib import Path


class StorageError(RuntimeError):
    """Base class for local persistence failures."""


class CorruptArtifactError(StorageError):
    """Raised when persisted bytes cannot be decoded or validated."""


class MissingArtifactError(StorageError):
    """Raised when an expected artifact does not exist."""


class IncompatibleArtifactError(StorageError):
    """Raised when an artifact's schema or format is unsupported."""


def require_artifact(path: Path, artifact_type: str) -> None:
    """Raise the shared missing-artifact error before a format reader runs."""
    if not path.is_file():
        raise MissingArtifactError(f'{artifact_type} artifact does not exist: {path}')
