"""Resumable-friendly Tenrai HTTP boundary."""

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic

import msgspec

from config import Settings, bind_logger, tenrai_snapshot_path
from fetch.checkpoint import (
    EnrichmentCheckpoint,
    FetchCheckpoint,
    SnapshotManifest,
    load_checkpoint,
    load_enrichment_checkpoint,
    save_checkpoint,
    save_enrichment_checkpoint,
    save_manifest,
)
from fetch.filters import CatalogueFilters
from fetch.progress import FetchProgress
from fetch.quality import CatalogueAcceptancePolicy, filter_catalogue
from fetch.transport import TenraiTransport
from models.tenrai import TenraiAnimeEntry, TenraiListResponse
from storage.json_io import read_json, write_json


class FetchError(RuntimeError):
    """Raised when a Tenrai request cannot be completed."""


class FetchSummary(msgspec.Struct, frozen=True):
    requested_pages: int
    completed_pages: int
    record_count: int
    failed_pages: tuple[int, ...]
    total_seconds: float


class TenraiClient:
    """Small synchronous client with retryable status handling."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self._transport = TenraiTransport(self.settings)
        self.last_summary: FetchSummary | None = None
        self._log = bind_logger(package='fetch', stage='catalogue')

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> 'TenraiClient':
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def catalogue_page(
        self, page: int, *, filters: CatalogueFilters | None = None
    ) -> TenraiListResponse[TenraiAnimeEntry]:
        """Fetch and type-check one filtered Tenrai catalogue page."""
        active_filters = filters or CatalogueFilters.sfw_catalogue()
        try:
            return self._transport.catalogue_page(page, filters=active_filters)
        except RuntimeError as error:
            raise FetchError(str(error)) from error

    def full_entry(self, anime_id: int) -> TenraiAnimeEntry:
        """Fetch one complete anime record for explicit enrichment."""
        if anime_id <= 0:
            raise ValueError('anime_id must be positive')
        try:
            return self._transport.full_entry(anime_id)
        except RuntimeError as error:
            raise FetchError(str(error)) from error

    def enrich(
        self,
        anime_ids: Sequence[int],
        output_path: Path,
        *,
        overwrite: bool = False,
        profile: str | None = None,
    ) -> tuple[TenraiAnimeEntry, ...]:
        """Fetch and persist a deterministic merged full catalogue for explicit IDs."""
        requested_ids = tuple(sorted(set(anime_ids)))
        if not requested_ids or any(anime_id <= 0 for anime_id in requested_ids):
            raise ValueError('enrichment requires positive anime IDs')
        checkpoint_path = output_path.with_name(f'{output_path.stem}.checkpoint.json')
        partial_path = output_path.with_name(f'{output_path.stem}.partial.json')
        if output_path.is_file() and not overwrite:
            raise FileExistsError(f'enrichment output already exists: {output_path}')
        checkpoint = None if overwrite else _load_enrichment_checkpoint(checkpoint_path)
        if checkpoint is not None and checkpoint.requested_ids != requested_ids:
            raise ValueError('enrichment checkpoint IDs do not match the requested IDs')
        entries_by_id = {
            entry.mal_id: entry for entry in (_load_entries(partial_path) if checkpoint is not None else ())
        }
        completed_ids = set(entries_by_id)
        failed_ids: set[int] = set(checkpoint.failed_ids if checkpoint is not None else ())
        for anime_id in requested_ids:
            if anime_id in completed_ids:
                continue
            try:
                entry = self.full_entry(anime_id)
            except FetchError:
                failed_ids.add(anime_id)
                save_enrichment_checkpoint(
                    checkpoint_path,
                    EnrichmentCheckpoint(
                        requested_ids,
                        tuple(sorted(completed_ids)),
                        tuple(sorted(failed_ids)),
                        str(partial_path.resolve()),
                    ),
                )
                raise
            entries_by_id[anime_id] = entry
            completed_ids.add(anime_id)
            write_json(partial_path, tuple(entries_by_id.values()))
            save_enrichment_checkpoint(
                checkpoint_path,
                EnrichmentCheckpoint(
                    requested_ids,
                    tuple(sorted(completed_ids)),
                    tuple(sorted(failed_ids)),
                    str(partial_path.resolve()),
                ),
            )
        missing_ids = tuple(anime_id for anime_id in requested_ids if anime_id not in entries_by_id)
        if missing_ids:
            raise FetchError(f'enrichment did not cover requested IDs: {missing_ids}')
        entries = tuple(entries_by_id[anime_id] for anime_id in requested_ids)
        write_json(output_path, entries)
        write_json(
            output_path.with_name(f'{output_path.stem}.manifest.json'),
            {
                'schema_version': 'tenrai-full-v2',
                'endpoint': '/full',
                'profile': profile,
                'requested_ids': requested_ids,
                'covered_ids': tuple(entry.mal_id for entry in entries),
                'failed_ids': tuple(sorted(failed_ids)),
                'complete': True,
                'record_count': len(entries),
                'relations_modeled': True,
                'relations_present_count': sum(bool(entry.relations) for entry in entries),
                'generated_at': datetime.now(UTC).isoformat(),
            },
        )
        partial_path.unlink(missing_ok=True)
        checkpoint_path.unlink(missing_ok=True)
        return entries

    def catalogue(
        self,
        last_page: int | None = None,
        *,
        filters: CatalogueFilters | None = None,
        checkpoint_path: Path | None = None,
        entries_path: Path | None = None,
        overwrite: bool = False,
    ) -> list[TenraiAnimeEntry]:
        """Fetch pages with Rich progress reporting."""
        if last_page is not None and last_page < 1:
            raise ValueError('last_page must be positive')
        entries_path = entries_path or tenrai_snapshot_path()
        active_filters = filters or CatalogueFilters.sfw_catalogue()
        checkpoint = _load_or_create_checkpoint(checkpoint_path)
        if checkpoint is None and entries_path.is_file() and not overwrite:
            raise FileExistsError(f'snapshot already exists; pass overwrite=True to replace it: {entries_path}')
        if checkpoint is not None:
            _validate_checkpoint(checkpoint, active_filters, entries_path)
            raw_entries_path = entries_path.with_name(f'{entries_path.stem}.raw.json')
            if not raw_entries_path.is_file():
                raise ValueError('checkpoint exists but its snapshot is missing')
        start_page = checkpoint.next_page if checkpoint else 1
        raw_entries_path = entries_path.with_name(f'{entries_path.stem}.raw.json')
        entries: list[TenraiAnimeEntry] = _load_entries(raw_entries_path) if checkpoint else []
        first_response: TenraiListResponse[TenraiAnimeEntry] | None = None
        total_anime = checkpoint.total_anime if checkpoint and checkpoint.total_anime is not None else 0
        if total_anime == 0 and last_page is not None:
            total_anime = last_page * active_filters.limit
        if start_page == 1:
            first_response = self.catalogue_page(start_page, filters=active_filters)
        if last_page is None:
            if checkpoint and checkpoint.total_pages is not None:
                last_page = checkpoint.total_pages
            elif first_response is not None:
                pagination = first_response.pagination
                last_page = pagination.last_visible_page if pagination else start_page
            else:
                raise FetchError('Unable to discover the final page without checkpoint metadata or page one')
        if first_response and first_response.pagination and first_response.pagination.items:
            total_anime = first_response.pagination.items.total
        if last_page < start_page:
            if checkpoint and start_page == last_page + 1:
                self.last_summary = FetchSummary(last_page, 0, len(entries), (), 0.0)
                return entries
            raise ValueError('last_page cannot precede the checkpoint page')
        started_at = monotonic()
        self._log.info(
            'Starting {} catalogue fetch from page {} through {} into {}.',
            'SFW' if active_filters.sfw_strict else 'all-anime',
            start_page,
            last_page,
            entries_path,
        )
        with FetchProgress(last_page) as progress:
            if start_page > 1:
                progress.complete(start_page - 1)
            for page in range(start_page, last_page + 1):
                response = (
                    first_response
                    if page == start_page and first_response is not None
                    else self.catalogue_page(page, filters=active_filters)
                )
                entries.extend(response.data)
                elapsed_seconds = monotonic() - started_at
                self._log.info(
                    'Fetched page {}/{} with {} entries ({}/{} anime, {:.2f}s elapsed).',
                    page,
                    last_page,
                    len(response.data),
                    len(entries),
                    total_anime,
                    elapsed_seconds,
                )
                progress.update(
                    page=page,
                    anime_count=len(entries),
                    total_anime=total_anime,
                )
                progress.advance()
                write_json(raw_entries_path, entries)
                if checkpoint_path is not None:
                    save_checkpoint(
                        checkpoint_path,
                        FetchCheckpoint(
                            mode='catalogue',
                            next_page=page + 1,
                            completed_pages=tuple(range(1, page + 1)),
                            total_pages=last_page,
                            total_anime=total_anime,
                            filter_signature=active_filters.signature(),
                            output_path=str(raw_entries_path.resolve()),
                        ),
                    )
                self._transport.wait()
        total_seconds = monotonic() - started_at
        _validate_catalogue(entries, total_anime, last_page, start_page)
        write_json(raw_entries_path, entries)
        excluded_genres = frozenset(int(value) for value in (active_filters.genres_exclude or '').split(',') if value)
        accepted_entries, decisions = filter_catalogue(
            entries,
            CatalogueAcceptancePolicy(excluded_genre_ids=excluded_genres),
        )
        write_json(entries_path, accepted_entries)
        write_json(
            entries_path.with_name(f'{entries_path.stem}.filter-audit.json'),
            {'accepted_count': len(accepted_entries), 'decisions': decisions},
        )
        rejected_count = sum(not decision.accepted for decision in decisions)
        rejection_reasons: dict[str, int] = {}
        for decision in decisions:
            for reason in decision.reasons:
                rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
        manifest_path = entries_path.with_name(f'{entries_path.stem}.manifest.json')
        save_manifest(
            manifest_path,
            SnapshotManifest(
                source_url=f'{self.settings.tenrai_base_url}/anime',
                mode='sfw' if active_filters.sfw_strict else 'all',
                filters=active_filters.signature(),
                completed_pages=last_page,
                record_count=len(accepted_entries),
                fetched_date=datetime.now(UTC).isoformat(),
                accepted_count=len(accepted_entries),
                rejected_count=rejected_count,
                rejection_reasons=tuple(sorted(rejection_reasons.items())),
            ),
        )
        self.last_summary = FetchSummary(
            last_page, last_page - start_page + 1, len(accepted_entries), (), total_seconds
        )
        self._log.info(
            'Completed catalogue fetch with {} accepted entries ({} filtered) in {:.2f}s.',
            len(accepted_entries),
            rejected_count,
            total_seconds,
        )
        return list(accepted_entries)


def _load_or_create_checkpoint(path: Path | None) -> FetchCheckpoint | None:
    if path is None or not path.is_file():
        return None
    return load_checkpoint(path)


def _load_entries(path: Path | None) -> list[TenraiAnimeEntry]:
    if path is None or not path.is_file():
        return []
    return read_json(path, list[TenraiAnimeEntry])


def _validate_catalogue(entries: list[TenraiAnimeEntry], total_anime: int, last_page: int, start_page: int) -> None:
    """Validate that a completed fetch produced the expected catalogue."""
    if start_page == 1 and len(entries) != total_anime:
        raise FetchError(f'Fetched {len(entries)} entries but the API reported {total_anime}')
    ids = [entry.mal_id for entry in entries]
    if len(ids) != len(set(ids)):
        raise FetchError(f'Fetched duplicate MAL IDs through page {last_page}')


def _validate_checkpoint(
    checkpoint: FetchCheckpoint,
    filters: CatalogueFilters,
    entries_path: Path,
) -> None:
    """Reject resumes that could combine incompatible fetch artifacts."""
    if not checkpoint.filter_signature:
        raise ValueError('checkpoint has no filter metadata; start a fresh fetch')
    if checkpoint.filter_signature != filters.signature():
        raise ValueError('checkpoint filters do not match the requested fetch')
    raw_entries_path = entries_path.with_name(f'{entries_path.stem}.raw.json')
    if checkpoint.output_path != str(raw_entries_path.resolve()):
        raise ValueError('checkpoint output path does not match the requested output')


def _load_enrichment_checkpoint(path: Path) -> EnrichmentCheckpoint | None:
    if not path.is_file():
        return None
    return load_enrichment_checkpoint(path)
