"""Storage boundary exceptions."""


class StorageError(RuntimeError):
    """Base class for local persistence failures."""


class CorruptArtifactError(StorageError):
    """Raised when persisted bytes cannot be decoded or validated."""


class MissingArtifactError(StorageError):
    """Raised when an expected artifact does not exist."""


class IncompatibleArtifactError(StorageError):
    """Raised when an artifact's schema or format is unsupported."""
