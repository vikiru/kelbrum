from pathlib import Path

from fetch.catalogue import acquire_catalogue
from fetch.contracts import Pagination, PaginationItems, TenraiAnimeEntry, TenraiListResponse
from fetch.filters import CatalogueFilters
from fetch.quality import CatalogueAcceptancePolicy


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
