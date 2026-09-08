"""Catalogue input acquisition and source-artifact validation."""

from collections.abc import Sequence
from pathlib import Path

from fetch.client import TenraiClient
from fetch.filters import CatalogueFilters
from models.tenrai import TenraiAnimeEntry
from storage.json_io import read_json


def load_or_fetch(
    client: TenraiClient,
    snapshot: Path,
    checkpoint: Path,
    filters: CatalogueFilters,
    overwrite: bool,
) -> list[TenraiAnimeEntry]:
    """Reuse a compatible snapshot or fetch a resumable catalogue snapshot."""
    if snapshot.is_file() and not overwrite:
        return read_json(snapshot, list[TenraiAnimeEntry])
    return client.catalogue(
        filters=filters,
        checkpoint_path=checkpoint,
        entries_path=snapshot,
        overwrite=overwrite,
    )


def load_or_enrich(
    client: TenraiClient,
    entries: Sequence[TenraiAnimeEntry],
    full_artifact: Path,
    overwrite: bool,
    profile: str,
) -> list[TenraiAnimeEntry]:
    """Reuse a full-entry artifact or enrich the requested catalogue entries."""
    if full_artifact.is_file() and not overwrite:
        return read_json(full_artifact, list[TenraiAnimeEntry])
    return list(
        client.enrich(
            tuple(entry.mal_id for entry in entries),
            full_artifact,
            overwrite=overwrite,
            profile=profile,
        )
    )


def validate_entrypoint_pair(snapshot: Path, enriched: Path) -> None:
    """Ensure snapshot and full-entry artifacts describe the same IDs."""
    snapshot_ids = {entry.mal_id for entry in read_json(snapshot, list[TenraiAnimeEntry])}
    enriched_ids = {entry.mal_id for entry in read_json(enriched, list[TenraiAnimeEntry])}
    if snapshot_ids != enriched_ids:
        missing = sorted(snapshot_ids - enriched_ids)
        unexpected = sorted(enriched_ids - snapshot_ids)
        raise ValueError(f'snapshot/full profile mismatch; missing={missing}, unexpected={unexpected}')
