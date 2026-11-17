from pathlib import Path

import pytest

from fetch.catalogue import acquire_catalogue
from fetch.checkpoint import FetchCheckpoint, save_checkpoint
from fetch.contracts import Pagination, PaginationItems, TenraiAnimeEntry, TenraiListResponse
from fetch.errors import FetchError
from fetch.filters import CatalogueFilters
from fetch.quality import CatalogueAcceptancePolicy
from storage.json_io import read_json, write_json


class FakeCatalogueSource:
    route_name = 'fixture-route'
    catalogue_url = 'https://fixture.example/catalogue'

    def __init__(self, entries: list[TenraiAnimeEntry]) -> None:
        self.entries = entries
        self.requested_pages: list[int] = []

    def catalogue_page(self, page: int, *, filters: CatalogueFilters) -> TenraiListResponse[TenraiAnimeEntry]:
        del filters
        self.requested_pages.append(page)
        return TenraiListResponse(
            self.entries,
            Pagination(last_visible_page=1, items=PaginationItems(count=len(self.entries), total=len(self.entries))),
        )

    def wait(self) -> None:
        pass


class QuietLogger:
    def info(self, message: str, *args: object) -> None:
        del message, args


def test_catalogue_acquisition_isolated_from_http_and_repository_paths(tmp_path: Path) -> None:
    source = FakeCatalogueSource([TenraiAnimeEntry(mal_id=20, title='Example', synopsis='A story.')])
    output = tmp_path / 'snapshot.json'

    entries, summary = acquire_catalogue(
        source,
        last_page=1,
        entries_path=output,
        filters=CatalogueFilters.all_anime(),
        checkpoint_path=tmp_path / 'checkpoint.json',
        overwrite=False,
        profile_name='fixture',
        acceptance_policy=CatalogueAcceptancePolicy(),
        log=QuietLogger(),
    )

    assert [entry.mal_id for entry in entries] == [20]
    assert source.requested_pages == [1]
    assert summary.record_count == 1
    assert output.is_file()
    assert not Path.cwd().joinpath('snapshot.json').exists()


def test_terminal_resume_returns_only_accepted_entries(tmp_path: Path) -> None:
    accepted = TenraiAnimeEntry(mal_id=1, title='Accepted', synopsis='A story.', approved=True)
    rejected = TenraiAnimeEntry(mal_id=2, title='Rejected', approved=False, synopsis='A story.')
    source = FakeCatalogueSource([accepted, rejected])
    filters = CatalogueFilters.all_anime()
    output = tmp_path / 'snapshot.json'
    raw_path = tmp_path / 'snapshot.raw.json'
    checkpoint_path = tmp_path / 'checkpoint.json'
    write_json(raw_path, (accepted, rejected))
    save_checkpoint(
        checkpoint_path,
        FetchCheckpoint(
            mode='catalogue',
            route=source.route_name,
            profile='fixture',
            next_page=2,
            completed_pages=(1,),
            total_pages=1,
            total_anime=2,
            filter_signature=filters.signature(),
            output_path=str(raw_path.resolve()),
        ),
    )

    entries, summary = acquire_catalogue(
        source,
        last_page=None,
        entries_path=output,
        filters=filters,
        checkpoint_path=checkpoint_path,
        overwrite=False,
        profile_name='fixture',
        acceptance_policy=CatalogueAcceptancePolicy(),
        log=QuietLogger(),
    )

    assert tuple(entry.mal_id for entry in entries) == (1,)
    assert source.requested_pages == []
    assert summary.record_count == 1
    assert [entry.mal_id for entry in read_json(output, list[TenraiAnimeEntry])] == [1]


def test_terminal_resume_rejects_incomplete_raw_counts(tmp_path: Path) -> None:
    source = FakeCatalogueSource([TenraiAnimeEntry(mal_id=1, title='Accepted', synopsis='A story.')])
    filters = CatalogueFilters.all_anime()
    output = tmp_path / 'snapshot.json'
    raw_path = tmp_path / 'snapshot.raw.json'
    checkpoint_path = tmp_path / 'checkpoint.json'
    write_json(raw_path, (source.entries[0],))
    save_checkpoint(
        checkpoint_path,
        FetchCheckpoint(
            mode='catalogue',
            route=source.route_name,
            profile='fixture',
            next_page=2,
            completed_pages=(1,),
            total_pages=1,
            total_anime=2,
            filter_signature=filters.signature(),
            output_path=str(raw_path.resolve()),
        ),
    )

    with pytest.raises(FetchError, match='Resumed snapshot contains 1 entries'):
        acquire_catalogue(
            source,
            last_page=None,
            entries_path=output,
            filters=filters,
            checkpoint_path=checkpoint_path,
            overwrite=False,
            profile_name='fixture',
            acceptance_policy=CatalogueAcceptancePolicy(),
            log=QuietLogger(),
        )
