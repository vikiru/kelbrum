"""Typed frontend artifact metadata contracts."""

import msgspec


class NumericRange(msgspec.Struct, frozen=True):
    minimum: float | None
    maximum: float | None


class ArtifactManifest(msgspec.Struct, frozen=True):
    schema_version: str
    fetched_date: str
    anime_count: int
    artifacts: tuple[tuple[str, str], ...]
