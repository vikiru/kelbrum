"""Atomic incremental profile refresh and selective enrichment orchestration."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import msgspec

from fetch.checkpoint import SnapshotManifest, load_manifest, save_manifest
from fetch.contracts import TenraiAnimeEntry, TenraiListResponse
from fetch.errors import FetchError
from fetch.filters import CatalogueFilters
from fetch.quality import CatalogueAcceptancePolicy, filter_catalogue
from storage.errors import StorageError
from storage.hashing import sha256_file
from storage.json_io import read_json, write_json


class ProfileUpdateSource(Protocol):
    """Transport and API capabilities required for incremental profile updates."""

    @property
    def route_name(self) -> str: ...

    @property
    def catalogue_url(self) -> str: ...

    def catalogue_page(self, page: int, *, filters: CatalogueFilters) -> TenraiListResponse[TenraiAnimeEntry]: ...

    def full_entry(self, anime_id: int) -> TenraiAnimeEntry: ...

    def wait(self) -> None: ...


class UpdateLogger(Protocol):
    """Minimal logging port for anime update orchestration."""

    def info(self, message: str, *args: object) -> None: ...

    def warning(self, message: str, *args: object) -> None: ...


class UpdateResult(msgspec.Struct, frozen=True):
    """Summary of an anime ingestion or update operation."""

    requested_count: int
    new_count: int
    updated_count: int
    rejected_count: int
    total_catalogue_count: int
    failed_ids: tuple[int, ...]


def _fetch_single_entry(source: ProfileUpdateSource, anime_id: int) -> TenraiAnimeEntry:
    entry = source.full_entry(anime_id)
    if entry.mal_id != anime_id:
        raise ValueError(f'Source returned mal_id {entry.mal_id} for requested {anime_id}')
    return entry


def _merge_refreshed_entry(existing: TenraiAnimeEntry | None, refreshed: TenraiAnimeEntry) -> TenraiAnimeEntry:
    """Refresh catalogue fields while preserving /full-only metadata from an existing record."""
    if existing is None:
        return refreshed
    return msgspec.structs.replace(
        refreshed,
        moreinfo=refreshed.moreinfo if refreshed.moreinfo is not None else existing.moreinfo,
        external=refreshed.external or existing.external,
        relations=refreshed.relations or existing.relations,
    )


def _persist_update_artifacts(
    *,
    snapshot_path: Path,
    snapshot_map: Mapping[int, TenraiAnimeEntry],
    full_artifact_path: Path | None,
    full_map: Mapping[int, TenraiAnimeEntry] | None,
    route_name: str,
    default_source_url: str,
    default_mode: str,
    filters_signature: tuple[tuple[str, str], ...] | None,
    completed_pages: int | None,
    profile_name: str | None,
    rejected_count: int,
    accumulate_rejected: bool,
    log: UpdateLogger | None,
) -> int:
    """Write updated snapshot, full artifact, and their manifests atomically."""
    sorted_snapshot = [snapshot_map[key] for key in sorted(snapshot_map)]
    write_json(snapshot_path, sorted_snapshot)

    manifest_path = snapshot_path.with_name(f'{snapshot_path.stem}.manifest.json')
    now_iso = datetime.now(UTC).isoformat()
    if manifest_path.is_file():
        manifest = load_manifest(manifest_path)
        next_completed_pages = (
            max(manifest.completed_pages, completed_pages) if completed_pages is not None else manifest.completed_pages
        )
        next_rejected = (manifest.rejected_count or 0) + rejected_count if accumulate_rejected else rejected_count
        updated_manifest = SnapshotManifest(
            source_url=manifest.source_url,
            mode=manifest.mode,
            filters=filters_signature if filters_signature is not None else manifest.filters,
            completed_pages=next_completed_pages,
            record_count=len(sorted_snapshot),
            fetched_date=now_iso,
            schema_version=manifest.schema_version,
            route=route_name,
            profile=profile_name if profile_name is not None else manifest.profile,
            accepted_count=len(sorted_snapshot),
            rejected_count=next_rejected,
            rejection_reasons=manifest.rejection_reasons,
        )
    else:
        updated_manifest = SnapshotManifest(
            source_url=default_source_url,
            mode=default_mode,
            filters=filters_signature or (),
            completed_pages=completed_pages or 0,
            record_count=len(sorted_snapshot),
            fetched_date=now_iso,
            route=route_name,
            profile=profile_name or '-',
            accepted_count=len(sorted_snapshot),
            rejected_count=rejected_count,
        )
    save_manifest(manifest_path, updated_manifest)

    if full_artifact_path is not None and full_map is not None:
        sorted_full = [full_map[key] for key in sorted(full_map)]
        write_json(full_artifact_path, sorted_full)
        full_manifest_path = full_artifact_path.with_name(f'{full_artifact_path.stem}.manifest.json')
        if full_manifest_path.is_file():
            try:
                full_manifest_data = read_json(full_manifest_path, dict)
                full_manifest_data['record_count'] = len(sorted_full)
                full_manifest_data['requested_count'] = len(sorted_full)
                full_manifest_data['covered_ids'] = sorted(full_map)
                full_manifest_data['requested_ids'] = sorted(full_map)
                full_manifest_data['artifact_sha256'] = sha256_file(full_artifact_path)
                full_manifest_data['generated_at'] = now_iso
                write_json(full_manifest_path, full_manifest_data)
            except (OSError, StorageError) as error:
                if log is not None:
                    log.warning('Could not update full artifact manifest {}: {}', full_manifest_path, error)

    return len(sorted_snapshot)


def update_anime_records(
    source: ProfileUpdateSource,
    anime_ids: Sequence[int],
    *,
    snapshot_path: Path,
    full_artifact_path: Path | None = None,
    acceptance_policy: CatalogueAcceptancePolicy | None = None,
    log: UpdateLogger | None = None,
) -> UpdateResult:
    """Fetch specific anime records by ID and integrate them into existing snapshot artifacts."""
    if not anime_ids:
        existing_snapshot: list[TenraiAnimeEntry] = (
            read_json(snapshot_path, list[TenraiAnimeEntry]) if snapshot_path.is_file() else []
        )
        return UpdateResult(
            requested_count=0,
            new_count=0,
            updated_count=0,
            rejected_count=0,
            total_catalogue_count=len(existing_snapshot),
            failed_ids=(),
        )

    target_ids = tuple(sorted(dict.fromkeys(anime_ids)))
    for anime_id in target_ids:
        if anime_id <= 0:
            raise ValueError(f'anime_id must be positive, got {anime_id}')

    existing_snapshot_entries: list[TenraiAnimeEntry] = (
        read_json(snapshot_path, list[TenraiAnimeEntry]) if snapshot_path.is_file() else []
    )
    snapshot_map = {entry.mal_id: entry for entry in existing_snapshot_entries}

    full_map: dict[int, TenraiAnimeEntry] | None = None
    if full_artifact_path is not None and full_artifact_path.is_file():
        full_entries = read_json(full_artifact_path, list[TenraiAnimeEntry])
        full_map = {entry.mal_id: entry for entry in full_entries}

    fetched_entries: list[TenraiAnimeEntry] = []
    failed_ids: list[int] = []

    for anime_id in target_ids:
        try:
            entry = _fetch_single_entry(source, anime_id)
            fetched_entries.append(entry)
            source.wait()
        except (FetchError, OSError, ValueError) as error:
            if log is not None:
                log.warning('Failed to fetch anime ID {}: {}', anime_id, error)
            failed_ids.append(anime_id)

    policy = acceptance_policy or CatalogueAcceptancePolicy()
    accepted_fetched, _decisions = filter_catalogue(fetched_entries, policy)

    new_count = 0
    updated_count = 0
    rejected_count = len(fetched_entries) - len(accepted_fetched)

    for entry in accepted_fetched:
        if entry.mal_id in snapshot_map:
            updated_count += 1
        else:
            new_count += 1
        snapshot_map[entry.mal_id] = entry
        if full_map is not None:
            full_map[entry.mal_id] = entry

    total_count = _persist_update_artifacts(
        snapshot_path=snapshot_path,
        snapshot_map=snapshot_map,
        full_artifact_path=full_artifact_path,
        full_map=full_map,
        route_name=source.route_name,
        default_source_url=source.catalogue_url,
        default_mode='all',
        filters_signature=None,
        completed_pages=None,
        profile_name=None,
        rejected_count=rejected_count,
        accumulate_rejected=True,
        log=log,
    )

    if log is not None:
        log.info(
            'Updated catalogue {}: {} new, {} updated, {} rejected, {} failed.',
            snapshot_path.name,
            new_count,
            updated_count,
            rejected_count,
            len(failed_ids),
        )

    return UpdateResult(
        requested_count=len(target_ids),
        new_count=new_count,
        updated_count=updated_count,
        rejected_count=rejected_count,
        total_catalogue_count=total_count,
        failed_ids=tuple(failed_ids),
    )


def update_profile_catalogue(
    source: ProfileUpdateSource,
    *,
    snapshot_path: Path,
    filters: CatalogueFilters,
    last_page: int | None = None,
    full_artifact_path: Path | None = None,
    acceptance_policy: CatalogueAcceptancePolicy | None = None,
    profile_name: str = '-',
    log: UpdateLogger | None = None,
) -> UpdateResult:
    """Repeat catalogue fetch (1..x) with profile filters, updating records and enriching only new IDs."""
    if last_page is not None and last_page < 1:
        raise ValueError(f'last_page must be >= 1, got {last_page}')

    existing_snapshot_entries: list[TenraiAnimeEntry] = (
        read_json(snapshot_path, list[TenraiAnimeEntry]) if snapshot_path.is_file() else []
    )
    existing_snapshot_ids = {entry.mal_id for entry in existing_snapshot_entries}
    snapshot_map = {entry.mal_id: entry for entry in existing_snapshot_entries}

    full_map: dict[int, TenraiAnimeEntry] | None = None
    if full_artifact_path is not None and full_artifact_path.is_file():
        full_entries = read_json(full_artifact_path, list[TenraiAnimeEntry])
        full_map = {entry.mal_id: entry for entry in full_entries}

    first_page_response = source.catalogue_page(1, filters=filters)
    total_pages = first_page_response.pagination.last_visible_page if first_page_response.pagination else 1
    target_last_page = min(total_pages, last_page) if last_page is not None else total_pages

    if log is not None:
        log.info(
            'Scanning catalogue pages 1 through {} for profile "{}"...',
            target_last_page,
            profile_name,
        )

    all_page_entries: list[TenraiAnimeEntry] = list(first_page_response.data)
    source.wait()

    for current_page in range(2, target_last_page + 1):
        page_response = source.catalogue_page(current_page, filters=filters)
        all_page_entries.extend(page_response.data)
        if log is not None:
            log.info('Fetched page {}/{} ({} records).', current_page, target_last_page, len(page_response.data))
        source.wait()

    policy = acceptance_policy or CatalogueAcceptancePolicy()
    accepted_page_entries, _decisions = filter_catalogue(all_page_entries, policy)

    new_ids: list[int] = []
    updated_count = 0
    for entry in accepted_page_entries:
        existing_full = full_map.get(entry.mal_id) if full_map is not None else None
        if entry.mal_id in existing_snapshot_ids:
            merged_entry = _merge_refreshed_entry(existing_full or snapshot_map.get(entry.mal_id), entry)
            snapshot_map[entry.mal_id] = merged_entry
            if full_map is not None and entry.mal_id in full_map:
                full_map[entry.mal_id] = merged_entry
            updated_count += 1
        else:
            snapshot_map[entry.mal_id] = _merge_refreshed_entry(existing_full, entry)
            if full_map is not None and entry.mal_id in full_map:
                full_map[entry.mal_id] = _merge_refreshed_entry(existing_full, entry)
            new_ids.append(entry.mal_id)

    unique_new_ids = tuple(sorted(set(new_ids)))
    failed_enrichment_ids: list[int] = []
    if full_artifact_path is not None and full_map is not None and unique_new_ids:
        if log is not None:
            log.info('Selectively enriching {} newly discovered anime records via /full...', len(unique_new_ids))
        for new_id in unique_new_ids:
            try:
                full_record = _fetch_single_entry(source, new_id)
                full_map[new_id] = full_record
                snapshot_map[new_id] = full_record
                source.wait()
            except (FetchError, OSError, ValueError) as error:
                if log is not None:
                    log.warning('Enrichment failed for new anime ID {}: {}', new_id, error)
                failed_enrichment_ids.append(new_id)

    rejected_count = len(all_page_entries) - len(accepted_page_entries)
    total_count = _persist_update_artifacts(
        snapshot_path=snapshot_path,
        snapshot_map=snapshot_map,
        full_artifact_path=full_artifact_path,
        full_map=full_map,
        route_name=source.route_name,
        default_source_url=source.catalogue_url,
        default_mode='sfw' if filters.sfw_strict else 'all',
        filters_signature=filters.signature(),
        completed_pages=target_last_page,
        profile_name=profile_name,
        rejected_count=rejected_count,
        accumulate_rejected=False,
        log=log,
    )

    if log is not None:
        log.info(
            'Completed profile update for {}: {} new ({} enriched), {} updated, {} rejected.',
            profile_name,
            len(unique_new_ids),
            len(unique_new_ids) - len(failed_enrichment_ids),
            updated_count,
            rejected_count,
        )

    return UpdateResult(
        requested_count=len(all_page_entries),
        new_count=len(unique_new_ids),
        updated_count=updated_count,
        rejected_count=rejected_count,
        total_catalogue_count=total_count,
        failed_ids=tuple(failed_enrichment_ids),
    )
