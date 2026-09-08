"""Immutable Tenrai snapshot persistence."""

from datetime import UTC, datetime
from pathlib import Path

from fetch.checkpoint import SnapshotManifest, save_manifest
from models.tenrai import TenraiAnimeEntry
from storage.json_io import write_json


def write_snapshot(
    path: Path,
    entries: list[TenraiAnimeEntry],
    *,
    source_url: str,
    mode: str,
    filters: tuple[tuple[str, str], ...],
    completed_pages: int,
) -> SnapshotManifest:
    """Write a minified snapshot and its manifest atomically."""
    payload = {'data': entries}
    fetched_date = datetime.now(UTC).isoformat()
    write_json(path, payload)
    manifest = SnapshotManifest(source_url, mode, filters, completed_pages, len(entries), fetched_date)
    save_manifest(path.with_name(f'{path.stem}.manifest.json'), manifest)
    return manifest
