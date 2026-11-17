"""Resumable enrichment of accepted catalogue IDs."""

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from fetch.checkpoint import EnrichmentCheckpoint, load_enrichment_checkpoint, save_enrichment_checkpoint
from fetch.contracts import TenraiAnimeEntry
from fetch.errors import FetchError
from storage.hashing import sha256_file
from storage.json_io import read_json, write_json


class FullEntrySource(Protocol):
    """Minimal source port required by enrichment orchestration."""

    @property
    def route_name(self) -> str: ...

    def full_entry(self, anime_id: int) -> TenraiAnimeEntry: ...


def enrich_entries(
    source: FullEntrySource,
    anime_ids: Sequence[int],
    output_path: Path,
    *,
    overwrite: bool = False,
    profile: str | None = None,
) -> tuple[TenraiAnimeEntry, ...]:
    """Fetch and persist a deterministic merged full catalogue for explicit IDs."""
    requested_ids = _requested_ids(anime_ids)
    checkpoint_path = output_path.with_name(f'{output_path.stem}.checkpoint.json')
    partial_path = output_path.with_name(f'{output_path.stem}.partial.json')
    if output_path.is_file() and not overwrite:
        raise FileExistsError(f'enrichment output already exists: {output_path}')
    checkpoint = None if overwrite else _load_checkpoint(checkpoint_path)
    if checkpoint is not None:
        _validate_checkpoint(checkpoint, requested_ids, source.route_name, profile, partial_path)
    partial_entries = _load_entries(partial_path) if checkpoint is not None else []
    entries_by_id = _entries_by_id(partial_entries, requested_ids)
    if checkpoint is not None and not set(checkpoint.completed_ids).issubset(entries_by_id):
        raise ValueError('enrichment checkpoint completed IDs are missing from partial output')
    completed_ids = set(entries_by_id)
    failed_ids: set[int] = set(checkpoint.failed_ids if checkpoint is not None else ())
    failed_ids.difference_update(completed_ids)
    for anime_id in requested_ids:
        if anime_id in completed_ids:
            continue
        try:
            entry = source.full_entry(anime_id)
        except FetchError:
            failed_ids.add(anime_id)
            _save_checkpoint(
                checkpoint_path, requested_ids, completed_ids, failed_ids, partial_path, source.route_name, profile
            )
            raise
        if entry.mal_id != anime_id:
            raise ValueError(f'enrichment returned ID {entry.mal_id} for requested ID {anime_id}')
        entries_by_id[anime_id] = entry
        completed_ids.add(anime_id)
        failed_ids.discard(anime_id)
        write_json(partial_path, tuple(entries_by_id.values()))
        _save_checkpoint(
            checkpoint_path, requested_ids, completed_ids, failed_ids, partial_path, source.route_name, profile
        )
    missing_ids = tuple(anime_id for anime_id in requested_ids if anime_id not in entries_by_id)
    if missing_ids:
        raise FetchError(f'enrichment did not cover requested IDs: {missing_ids}')
    entries = tuple(entries_by_id[anime_id] for anime_id in requested_ids)
    write_json(output_path, entries)
    write_json(
        output_path.with_name(f'{output_path.stem}.manifest.json'),
        {
            'schema_version': 'tenrai-full-v3',
            'route': source.route_name,
            'endpoint': '/full',
            'profile': profile,
            'requested_ids': requested_ids,
            'requested_count': len(requested_ids),
            'covered_ids': tuple(entry.mal_id for entry in entries),
            'failed_ids': tuple(sorted(failed_ids)),
            'complete': True,
            'record_count': len(entries),
            'artifact_sha256': sha256_file(output_path),
            'relations_modeled': True,
            'relations_present_count': sum(bool(entry.relations) for entry in entries),
            'generated_at': datetime.now(UTC).isoformat(),
        },
    )
    partial_path.unlink(missing_ok=True)
    checkpoint_path.unlink(missing_ok=True)
    return entries


def _requested_ids(anime_ids: Sequence[int]) -> tuple[int, ...]:
    requested_ids = tuple(sorted(set(anime_ids)))
    if not requested_ids or any(anime_id <= 0 for anime_id in requested_ids):
        raise ValueError('enrichment requires positive anime IDs')
    return requested_ids


def _load_checkpoint(path: Path) -> EnrichmentCheckpoint | None:
    if not path.is_file():
        return None
    return load_enrichment_checkpoint(path)


def _load_entries(path: Path) -> list[TenraiAnimeEntry]:
    if not path.is_file():
        return []
    return read_json(path, list[TenraiAnimeEntry])


def _save_checkpoint(
    path: Path,
    requested_ids: tuple[int, ...],
    completed_ids: set[int],
    failed_ids: set[int],
    partial_path: Path,
    route: str,
    profile: str | None,
) -> None:
    save_enrichment_checkpoint(
        path,
        EnrichmentCheckpoint(
            requested_ids,
            tuple(sorted(completed_ids)),
            tuple(sorted(failed_ids)),
            str(partial_path.resolve()),
            route,
            profile or '-',
            'enrichment-checkpoint-v2',
        ),
    )


def _validate_checkpoint(
    checkpoint: EnrichmentCheckpoint,
    requested_ids: tuple[int, ...],
    route: str,
    profile: str | None,
    partial_path: Path,
) -> None:
    if checkpoint.schema_version != 'enrichment-checkpoint-v2':
        raise ValueError('unsupported enrichment checkpoint schema')
    if checkpoint.requested_ids != requested_ids:
        raise ValueError('enrichment checkpoint IDs do not match the requested IDs')
    if checkpoint.route != route or checkpoint.profile != (profile or '-'):
        raise ValueError('enrichment checkpoint route or profile does not match the request')
    if checkpoint.partial_output_path != str(partial_path.resolve()):
        raise ValueError('enrichment checkpoint partial output path does not match')
    if not set(checkpoint.completed_ids).issubset(requested_ids) or not set(checkpoint.failed_ids).issubset(
        requested_ids
    ):
        raise ValueError('enrichment checkpoint contains IDs outside the request')
    if set(checkpoint.completed_ids) & set(checkpoint.failed_ids):
        raise ValueError('enrichment checkpoint marks an ID as both complete and failed')


def _entries_by_id(entries: Sequence[TenraiAnimeEntry], requested_ids: tuple[int, ...]) -> dict[int, TenraiAnimeEntry]:
    result: dict[int, TenraiAnimeEntry] = {}
    for entry in entries:
        if entry.mal_id not in requested_ids:
            raise ValueError(f'enrichment partial output contains unexpected ID {entry.mal_id}')
        if entry.mal_id in result:
            raise ValueError(f'enrichment partial output contains duplicate ID {entry.mal_id}')
        result[entry.mal_id] = entry
    return result
