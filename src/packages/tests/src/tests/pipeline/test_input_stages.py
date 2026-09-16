from collections.abc import Sequence
from pathlib import Path

from fetch.contracts import TenraiAnimeEntry
from fetch.filters import CatalogueFilters
from pipeline.input_stages import load_or_enrich, load_or_fetch
from storage.json_io import write_json


class FakeCatalogueClient:
    def __init__(self, entries: list[TenraiAnimeEntry]) -> None:
        self.entries = entries
        self.catalogue_calls: list[tuple[Path, Path]] = []
        self.enrich_calls: list[tuple[tuple[int, ...], Path]] = []

    def catalogue(
        self,
        *,
        filters: CatalogueFilters,
        checkpoint_path: Path,
        entries_path: Path,
        overwrite: bool,
    ) -> list[TenraiAnimeEntry]:
        del filters, overwrite
        self.catalogue_calls.append((checkpoint_path, entries_path))
        write_json(entries_path, self.entries)
        return self.entries

    def enrich(
        self,
        anime_ids: Sequence[int],
        output_path: Path,
        *,
        overwrite: bool,
        profile: str | None,
    ) -> list[TenraiAnimeEntry]:
        del overwrite, profile
        self.enrich_calls.append((tuple(anime_ids), output_path))
        write_json(output_path, self.entries)
        return self.entries


def test_input_workflow_uses_only_explicit_temporary_paths(tmp_path: Path) -> None:
    entries = [TenraiAnimeEntry(mal_id=20, title='Example')]
    client = FakeCatalogueClient(entries)
    snapshot = tmp_path / 'snapshot.json'
    checkpoint = tmp_path / 'checkpoint.json'
    full_artifact = tmp_path / 'full.json'

    fetched = load_or_fetch(client, snapshot, checkpoint, CatalogueFilters.all_anime(), overwrite=False)
    enriched = load_or_enrich(client, fetched, full_artifact, overwrite=False, profile='fixture')

    assert enriched == entries
    assert client.catalogue_calls == [(checkpoint, snapshot)]
    assert client.enrich_calls == [((20,), full_artifact)]
    assert set(tmp_path.iterdir()) == {snapshot, full_artifact}
