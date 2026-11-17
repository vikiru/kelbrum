from pathlib import Path

import pytest

from fetch.contracts import (
    AnimeRelation,
    ExternalLink,
    Pagination,
    PaginationItems,
    RelationEntry,
    TenraiAnimeEntry,
    TenraiListResponse,
)
from fetch.filters import CatalogueFilters
from fetch.quality import CatalogueAcceptancePolicy
from fetch.updates import update_anime_records, update_profile_catalogue
from storage.json_io import read_json, write_json


class FakeEntrySource:
    route_name = 'test-route'
    catalogue_url = 'https://test.example/catalogue'

    def __init__(
        self,
        entries_by_id: dict[int, TenraiAnimeEntry],
        pages: list[list[TenraiAnimeEntry]] | None = None,
    ) -> None:
        self.entries_by_id = entries_by_id
        self.pages = pages or []
        self.requested_ids: list[int] = []
        self.requested_pages: list[int] = []

    def full_entry(self, anime_id: int) -> TenraiAnimeEntry:
        self.requested_ids.append(anime_id)
        if anime_id not in self.entries_by_id:
            raise ValueError(f'Anime {anime_id} not found')
        return self.entries_by_id[anime_id]

    def catalogue_page(self, page: int, *, filters: CatalogueFilters) -> TenraiListResponse[TenraiAnimeEntry]:
        del filters
        self.requested_pages.append(page)
        page_entries = self.pages[page - 1] if page <= len(self.pages) else []
        total_items = sum(len(p) for p in self.pages)
        return TenraiListResponse(
            page_entries,
            Pagination(
                last_visible_page=len(self.pages),
                items=PaginationItems(count=len(page_entries), total=total_items),
            ),
        )

    def wait(self) -> None:
        pass


def test_update_anime_records_inserts_and_updates(tmp_path: Path) -> None:
    snapshot_path = tmp_path / 'snapshot.json'
    initial_entry = TenraiAnimeEntry(mal_id=1, title='Old Title', synopsis='Old synopsis')
    write_json(snapshot_path, [initial_entry])

    updated_entry = TenraiAnimeEntry(mal_id=1, title='New Title', synopsis='Updated synopsis')
    new_entry = TenraiAnimeEntry(mal_id=2, title='Second Anime', synopsis='Second synopsis')

    source = FakeEntrySource({1: updated_entry, 2: new_entry})

    result = update_anime_records(
        source,
        [1, 2],
        snapshot_path=snapshot_path,
        acceptance_policy=CatalogueAcceptancePolicy(),
    )

    assert result.requested_count == 2
    assert result.new_count == 1
    assert result.updated_count == 1
    assert result.rejected_count == 0
    assert result.total_catalogue_count == 2
    assert result.failed_ids == ()

    saved_entries = read_json(snapshot_path, list[TenraiAnimeEntry])
    assert len(saved_entries) == 2
    assert saved_entries[0].mal_id == 1
    assert saved_entries[0].title == 'New Title'
    assert saved_entries[1].mal_id == 2
    assert saved_entries[1].title == 'Second Anime'


def test_update_anime_records_handles_failures_gracefully(tmp_path: Path) -> None:
    snapshot_path = tmp_path / 'snapshot.json'
    valid_entry = TenraiAnimeEntry(mal_id=10, title='Valid Anime', synopsis='Valid synopsis')
    source = FakeEntrySource({10: valid_entry})

    result = update_anime_records(
        source,
        [10, 999],
        snapshot_path=snapshot_path,
        acceptance_policy=CatalogueAcceptancePolicy(),
    )

    assert result.requested_count == 2
    assert result.new_count == 1
    assert result.failed_ids == (999,)
    assert result.total_catalogue_count == 1


def test_update_profile_catalogue_scans_pages_and_skips_full_for_existing(tmp_path: Path) -> None:
    snapshot_path = tmp_path / 'snapshot.json'
    full_path = tmp_path / 'snapshot.full.json'

    existing_anime_1 = TenraiAnimeEntry(mal_id=100, title='Anime 100 Initial', synopsis='Syn 100')
    write_json(snapshot_path, [existing_anime_1])
    write_json(full_path, [existing_anime_1])

    refreshed_anime_1 = TenraiAnimeEntry(mal_id=100, title='Anime 100 Updated', synopsis='Syn 100 new')
    new_anime_2 = TenraiAnimeEntry(mal_id=200, title='Anime 200 Fresh', synopsis='Syn 200')
    enriched_anime_2 = TenraiAnimeEntry(mal_id=200, title='Anime 200 Fresh', synopsis='Syn 200 with full details')

    source = FakeEntrySource(
        entries_by_id={200: enriched_anime_2},
        pages=[[refreshed_anime_1, new_anime_2]],
    )

    result = update_profile_catalogue(
        source,
        snapshot_path=snapshot_path,
        filters=CatalogueFilters.sfw_catalogue(),
        full_artifact_path=full_path,
        acceptance_policy=CatalogueAcceptancePolicy(),
        profile_name='test-profile',
    )

    assert result.new_count == 1
    assert result.updated_count == 1
    assert result.total_catalogue_count == 2
    assert source.requested_pages == [1]
    assert source.requested_ids == [200]

    updated_snapshot = read_json(snapshot_path, list[TenraiAnimeEntry])
    assert len(updated_snapshot) == 2
    assert updated_snapshot[0].mal_id == 100
    assert updated_snapshot[0].title == 'Anime 100 Updated'
    assert updated_snapshot[1].mal_id == 200
    assert updated_snapshot[1].synopsis == 'Syn 200 with full details'

    updated_full = read_json(full_path, list[TenraiAnimeEntry])
    assert len(updated_full) == 2
    assert updated_full[0].mal_id == 100
    assert updated_full[1].mal_id == 200


def test_update_profile_catalogue_validates_last_page(tmp_path: Path) -> None:
    source = FakeEntrySource({})
    with pytest.raises(ValueError, match='last_page must be >= 1'):
        update_profile_catalogue(
            source,
            snapshot_path=tmp_path / 'snapshot.json',
            filters=CatalogueFilters.sfw_catalogue(),
            last_page=0,
        )


def test_update_profile_catalogue_preserves_full_fields_and_catches_corrupt_full_manifest(tmp_path: Path) -> None:
    snapshot_path = tmp_path / 'snapshot.json'
    full_path = tmp_path / 'snapshot.full.json'
    full_manifest_path = tmp_path / 'snapshot.full.manifest.json'

    relations = [AnimeRelation(relation='Sequel', entry=[RelationEntry(mal_id=101, type='anime', name='Sequel')])]
    external = [ExternalLink(name='Official', url='https://example.com')]
    existing_full = TenraiAnimeEntry(
        mal_id=100,
        title='Old Title',
        synopsis='Old synopsis',
        relations=relations,
        external=external,
    )
    write_json(snapshot_path, [TenraiAnimeEntry(mal_id=100, title='Old Title', synopsis='Old synopsis')])
    write_json(full_path, [existing_full])
    full_manifest_path.write_text('{not valid json', encoding='utf-8')

    refreshed_summary = TenraiAnimeEntry(mal_id=100, title='New Title', synopsis='New synopsis')
    source = FakeEntrySource(entries_by_id={}, pages=[[refreshed_summary]])

    warnings: list[str] = []

    class CaptureLog:
        def info(self, message: str, *args: object) -> None:
            del message, args

        def warning(self, message: str, *args: object) -> None:
            warnings.append(message.format(*args))

    result = update_profile_catalogue(
        source,
        snapshot_path=snapshot_path,
        filters=CatalogueFilters.sfw_catalogue(),
        full_artifact_path=full_path,
        acceptance_policy=CatalogueAcceptancePolicy(),
        log=CaptureLog(),
    )

    assert result.updated_count == 1
    assert any('Could not update full artifact manifest' in warning for warning in warnings)

    saved_full = read_json(full_path, list[TenraiAnimeEntry])
    assert saved_full[0].title == 'New Title'
    assert saved_full[0].relations == relations
    assert saved_full[0].external == external

    saved_snapshot = read_json(snapshot_path, list[TenraiAnimeEntry])
    assert saved_snapshot[0].relations == relations
    assert saved_snapshot[0].external == external
