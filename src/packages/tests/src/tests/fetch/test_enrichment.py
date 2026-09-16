from pathlib import Path

import pytest

from fetch.contracts import TenraiAnimeEntry
from fetch.enrichment import enrich_entries
from fetch.errors import FetchError
from storage.json_io import read_json


class FakeFullEntrySource:
    route_name = 'fixture-route'

    def __init__(self, entries: dict[int, TenraiAnimeEntry], failing_id: int | None = None) -> None:
        self.entries = entries
        self.failing_id = failing_id
        self.requested_ids: list[int] = []

    def full_entry(self, anime_id: int) -> TenraiAnimeEntry:
        self.requested_ids.append(anime_id)
        if anime_id == self.failing_id:
            raise FetchError('fixture failure')
        return self.entries[anime_id]


def test_enrichment_writes_sorted_entries_and_removes_resume_state(tmp_path: Path) -> None:
    entries = {10: TenraiAnimeEntry(mal_id=10, title='Ten'), 20: TenraiAnimeEntry(mal_id=20, title='Twenty')}
    source = FakeFullEntrySource(entries)
    output = tmp_path / 'full.json'

    result = enrich_entries(source, [20, 10, 20], output, profile='fixture')

    assert tuple(entry.mal_id for entry in result) == (10, 20)
    assert source.requested_ids == [10, 20]
    assert not output.with_name('full.partial.json').exists()
    assert not output.with_name('full.checkpoint.json').exists()
    assert read_json(output.with_name('full.manifest.json'), dict[str, object])['route'] == 'fixture-route'


def test_enrichment_persists_checkpoint_after_a_failed_request(tmp_path: Path) -> None:
    source = FakeFullEntrySource(
        {10: TenraiAnimeEntry(mal_id=10, title='Ten'), 20: TenraiAnimeEntry(mal_id=20, title='Twenty')},
        failing_id=20,
    )
    output = tmp_path / 'full.json'

    with pytest.raises(FetchError, match='fixture failure'):
        enrich_entries(source, [10, 20], output)

    checkpoint = read_json(output.with_name('full.checkpoint.json'), dict[str, object])
    assert checkpoint['completed_ids'] == [10]
    assert checkpoint['failed_ids'] == [20]


def test_enrichment_resumes_from_completed_partial_records(tmp_path: Path) -> None:
    entries = {10: TenraiAnimeEntry(mal_id=10, title='Ten'), 20: TenraiAnimeEntry(mal_id=20, title='Twenty')}
    output = tmp_path / 'full.json'
    failing_source = FakeFullEntrySource(entries, failing_id=20)

    with pytest.raises(FetchError):
        enrich_entries(failing_source, [10, 20], output)

    resumed_source = FakeFullEntrySource(entries)
    result = enrich_entries(resumed_source, [10, 20], output)

    assert tuple(entry.mal_id for entry in result) == (10, 20)
    assert resumed_source.requested_ids == [20]
