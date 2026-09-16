"""Fetch-specific failure types."""


class FetchError(RuntimeError):
    """Raised when a Tenrai request or fetch workflow cannot complete."""
