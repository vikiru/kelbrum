"""Atomic resumable fetch state and immutable snapshot manifests."""

from datetime import UTC, datetime
from pathlib import Path

import msgspec

from storage.json_io import read_json, write_json


class FetchCheckpoint(msgspec.Struct, frozen=True):
    mode: str
    next_page: int = 1
    completed_pages: tuple[int, ...] = ()
    failed_pages: tuple[int, ...] = ()
    total_pages: int | None = None
    total_anime: int | None = None
    filter_signature: tuple[tuple[str, str], ...] = ()
    output_path: str | None = None
    updated_at: str = msgspec.field(default_factory=lambda: datetime.now(UTC).isoformat())


class EnrichmentCheckpoint(msgspec.Struct, frozen=True):
    requested_ids: tuple[int, ...]
    completed_ids: tuple[int, ...] = ()
    failed_ids: tuple[int, ...] = ()
    partial_output_path: str | None = None
    updated_at: str = msgspec.field(default_factory=lambda: datetime.now(UTC).isoformat())


class SnapshotManifest(msgspec.Struct, frozen=True):
    source_url: str
    mode: str
    filters: tuple[tuple[str, str], ...]
    completed_pages: int
    record_count: int
    fetched_date: str
    schema_version: str = 'tenrai-v1'
    accepted_count: int | None = None
    rejected_count: int | None = None
    rejection_reasons: tuple[tuple[str, int], ...] = ()


def save_checkpoint(path: Path, checkpoint: FetchCheckpoint) -> None:
    write_json(path, checkpoint)


def load_checkpoint(path: Path) -> FetchCheckpoint:
    return read_json(path, FetchCheckpoint)


def save_enrichment_checkpoint(path: Path, checkpoint: EnrichmentCheckpoint) -> None:
    write_json(path, checkpoint)


def load_enrichment_checkpoint(path: Path) -> EnrichmentCheckpoint:
    return read_json(path, EnrichmentCheckpoint)


def save_manifest(path: Path, manifest: SnapshotManifest) -> None:
    write_json(path, manifest)
