"""Catalogue input acquisition and source-artifact validation."""

import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from fetch.contracts import TenraiAnimeEntry
from fetch.filters import CatalogueFilters
from pipeline.contracts import CatalogueClient
from storage.json_io import read_json


def load_or_fetch(
    client: CatalogueClient,
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
    client: CatalogueClient,
    entries: Sequence[TenraiAnimeEntry],
    full_artifact: Path,
    overwrite: bool,
    profile: str,
) -> list[TenraiAnimeEntry]:
    """Reuse a full-entry artifact or enrich the requested catalogue entries."""
    if full_artifact.is_file() and not overwrite:
        expected_ids = tuple(sorted(entry.mal_id for entry in entries))
        enriched_entries = read_json(full_artifact, list[TenraiAnimeEntry])
        _validate_enrichment_artifact(client, enriched_entries, full_artifact, profile, expected_ids)
        return enriched_entries
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
    snapshot_entries = read_json(snapshot, list[TenraiAnimeEntry])
    enriched_entries = read_json(enriched, list[TenraiAnimeEntry])
    snapshot_ids = _unique_ids(snapshot_entries, 'snapshot')
    enriched_ids = _unique_ids(enriched_entries, 'enriched artifact')
    if snapshot_ids != enriched_ids:
        missing = sorted(snapshot_ids - enriched_ids)
        unexpected = sorted(enriched_ids - snapshot_ids)
        raise ValueError(f'snapshot/full profile mismatch; missing={missing}, unexpected={unexpected}')


def _validate_enrichment_artifact(
    client: CatalogueClient,
    entries: Sequence[TenraiAnimeEntry],
    artifact_path: Path,
    profile: str | None,
    expected_ids: tuple[int, ...],
) -> None:
    manifest_path = artifact_path.with_name(f'{artifact_path.stem}.manifest.json')
    if not manifest_path.is_file():
        raise ValueError(f'enrichment artifact has no completion manifest: {manifest_path}')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    actual_ids = tuple(entry.mal_id for entry in entries)
    if len(set(actual_ids)) != len(actual_ids):
        raise ValueError('enrichment artifact contains duplicate IDs')
    expected_route = client.route_name
    if (
        manifest.get('schema_version') != 'tenrai-full-v3'
        or manifest.get('route') != expected_route
        or manifest.get('profile') != (profile or '-')
        or tuple(manifest.get('requested_ids', ())) != expected_ids
        or tuple(manifest.get('covered_ids', ())) != expected_ids
        or manifest.get('requested_count') != len(expected_ids)
        or manifest.get('record_count') != len(entries)
        or manifest.get('complete') is not True
        or manifest.get('artifact_sha256') != _sha256(artifact_path)
        or actual_ids != expected_ids
    ):
        raise ValueError('enrichment artifact manifest does not match the requested stage inputs')


def _unique_ids(entries: Sequence[TenraiAnimeEntry], label: str) -> set[int]:
    ids = [entry.mal_id for entry in entries]
    if len(set(ids)) != len(ids):
        raise ValueError(f'{label} contains duplicate anime IDs')
    return set(ids)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()
