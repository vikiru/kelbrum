"""Resumable catalogue acquisition orchestration."""

from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Protocol

import msgspec

from fetch.checkpoint import FetchCheckpoint, SnapshotManifest, load_checkpoint, save_checkpoint, save_manifest
from fetch.contracts import TenraiAnimeEntry, TenraiListResponse
from fetch.errors import FetchError
from fetch.filters import CatalogueFilters
from fetch.progress import FetchProgress
from fetch.quality import CatalogueAcceptancePolicy, FilterDecision, filter_catalogue
from storage.json_io import read_json, write_json


class CatalogueSource(Protocol):
    """Transport capabilities required by catalogue acquisition."""

    @property
    def route_name(self) -> str: ...

    @property
    def catalogue_url(self) -> str: ...

    def catalogue_page(self, page: int, *, filters: CatalogueFilters) -> TenraiListResponse[TenraiAnimeEntry]: ...

    def wait(self) -> None: ...


class FetchLogger(Protocol):
    """Small logging port used by acquisition orchestration."""

    def info(self, message: str, *args: object) -> None: ...


class FetchSummary(msgspec.Struct, frozen=True):
    requested_pages: int
    completed_pages: int
    record_count: int
    failed_pages: tuple[int, ...]
    total_seconds: float


def acquire_catalogue(
    source: CatalogueSource,
    *,
    last_page: int | None,
    entries_path: Path,
    filters: CatalogueFilters,
    checkpoint_path: Path | None,
    overwrite: bool,
    profile_name: str,
    acceptance_policy: CatalogueAcceptancePolicy,
    log: FetchLogger,
) -> tuple[list[TenraiAnimeEntry], FetchSummary]:
    """Fetch, accept, and persist one deterministic catalogue snapshot."""
    if last_page is not None and last_page < 1:
        raise ValueError('last_page must be positive')
    checkpoint, raw_entries_path, entries = _prepare_snapshot(
        source,
        entries_path=entries_path,
        filters=filters,
        checkpoint_path=checkpoint_path,
        overwrite=overwrite,
        profile_name=profile_name,
    )
    start_page = checkpoint.next_page if checkpoint else 1
    first_response: TenraiListResponse[TenraiAnimeEntry] | None = None
    total_anime = checkpoint.total_anime if checkpoint and checkpoint.total_anime is not None else 0
    if total_anime == 0 and last_page is not None:
        total_anime = last_page * filters.limit
    if start_page == 1:
        first_response = source.catalogue_page(start_page, filters=filters)
    last_page, total_anime = _resolve_pagination(first_response, checkpoint, last_page, total_anime)
    if last_page < start_page:
        if checkpoint and start_page == last_page + 1:
            return entries, FetchSummary(last_page, 0, len(entries), (), 0.0)
        raise ValueError('last_page cannot precede the checkpoint page')
    started_at = monotonic()
    log.info('Starting catalogue fetch from page {} through {} into {}.', start_page, last_page, entries_path)
    with FetchProgress(last_page) as progress:
        if start_page > 1:
            progress.complete(start_page - 1)
        for page in range(start_page, last_page + 1):
            response = (
                first_response
                if page == start_page and first_response is not None
                else source.catalogue_page(page, filters=filters)
            )
            entries.extend(response.data)
            log.info('Fetched page {}/{} with {} entries.', page, last_page, len(response.data))
            progress.update(page=page, anime_count=len(entries), total_anime=total_anime)
            progress.advance()
            write_json(raw_entries_path, entries)
            if checkpoint_path is not None:
                save_checkpoint(
                    checkpoint_path,
                    FetchCheckpoint(
                        mode='catalogue',
                        route=source.route_name,
                        profile=profile_name,
                        next_page=page + 1,
                        completed_pages=tuple(range(1, page + 1)),
                        total_pages=last_page,
                        total_anime=total_anime,
                        filter_signature=filters.signature(),
                        output_path=str(raw_entries_path.resolve()),
                    ),
                )
            source.wait()
    total_seconds = monotonic() - started_at
    _validate_catalogue(entries, total_anime, last_page, start_page)
    accepted_entries, decisions = filter_catalogue(entries, acceptance_policy)
    write_json(entries_path, accepted_entries)
    write_json(
        entries_path.with_name(f'{entries_path.stem}.filter-audit.json'),
        {'accepted_count': len(accepted_entries), 'decisions': decisions},
    )
    rejection_reasons = _rejection_counts(decisions)
    save_manifest(
        entries_path.with_name(f'{entries_path.stem}.manifest.json'),
        SnapshotManifest(
            source_url=source.catalogue_url,
            mode='sfw' if filters.sfw_strict else 'all',
            filters=filters.signature(),
            completed_pages=last_page,
            record_count=len(accepted_entries),
            fetched_date=datetime.now(UTC).isoformat(),
            route=source.route_name,
            profile=profile_name,
            accepted_count=len(accepted_entries),
            rejected_count=len(entries) - len(accepted_entries),
            rejection_reasons=tuple(sorted(rejection_reasons.items())),
        ),
    )
    summary = FetchSummary(last_page, last_page - start_page + 1, len(accepted_entries), (), total_seconds)
    log.info('Completed catalogue fetch with {} accepted entries in {:.2f}s.', len(accepted_entries), total_seconds)
    return list(accepted_entries), summary


def _prepare_snapshot(
    source: CatalogueSource,
    *,
    entries_path: Path,
    filters: CatalogueFilters,
    checkpoint_path: Path | None,
    overwrite: bool,
    profile_name: str,
) -> tuple[FetchCheckpoint | None, Path, list[TenraiAnimeEntry]]:
    """Validate resume state and load the raw entries for an acquisition."""
    checkpoint = _load_or_create_checkpoint(checkpoint_path)
    if checkpoint is None and entries_path.is_file() and not overwrite:
        raise FileExistsError(f'snapshot already exists; pass overwrite=True to replace it: {entries_path}')

    raw_entries_path = _raw_path(entries_path)
    if checkpoint is not None:
        _validate_checkpoint(checkpoint, filters, entries_path, source.route_name, profile_name)
        if not raw_entries_path.is_file():
            raise ValueError('checkpoint exists but its snapshot is missing')
    return checkpoint, raw_entries_path, _load_entries(raw_entries_path) if checkpoint else []


def _resolve_pagination(
    first_response: TenraiListResponse[TenraiAnimeEntry] | None,
    checkpoint: FetchCheckpoint | None,
    last_page: int | None,
    total_anime: int,
) -> tuple[int, int]:
    if last_page is None:
        if checkpoint and checkpoint.total_pages is not None:
            last_page = checkpoint.total_pages
        elif first_response and first_response.pagination:
            last_page = first_response.pagination.last_visible_page
        else:
            raise FetchError('Unable to discover the final page without pagination metadata')
    if first_response and first_response.pagination and first_response.pagination.items:
        total_anime = first_response.pagination.items.total
    return last_page, total_anime


def _load_or_create_checkpoint(path: Path | None) -> FetchCheckpoint | None:
    return load_checkpoint(path) if path is not None and path.is_file() else None


def _raw_path(path: Path) -> Path:
    return path.with_name(f'{path.stem}.raw.json')


def _load_entries(path: Path) -> list[TenraiAnimeEntry]:
    return read_json(path, list[TenraiAnimeEntry]) if path.is_file() else []


def _validate_catalogue(entries: list[TenraiAnimeEntry], total_anime: int, last_page: int, start_page: int) -> None:
    if start_page == 1 and len(entries) != total_anime:
        raise FetchError(f'Fetched {len(entries)} entries but the API reported {total_anime}')
    ids = [entry.mal_id for entry in entries]
    if len(ids) != len(set(ids)):
        raise FetchError(f'Fetched duplicate MAL IDs through page {last_page}')


def _validate_checkpoint(
    checkpoint: FetchCheckpoint,
    filters: CatalogueFilters,
    entries_path: Path,
    route_name: str,
    profile_name: str,
) -> None:
    if not checkpoint.filter_signature:
        raise ValueError('checkpoint has no filter metadata; start a fresh fetch')
    if checkpoint.filter_signature != filters.signature():
        raise ValueError('checkpoint filters do not match the requested fetch')
    if checkpoint.route != route_name:
        raise ValueError('checkpoint route does not match the requested route')
    if checkpoint.profile != profile_name:
        raise ValueError('checkpoint profile does not match the requested profile')
    if checkpoint.output_path != str(_raw_path(entries_path).resolve()):
        raise ValueError('checkpoint output path does not match the requested output')


def _rejection_counts(decisions: tuple[FilterDecision, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for decision in decisions:
        for reason in decision.reasons:
            counts[reason] = counts.get(reason, 0) + 1
    return counts
