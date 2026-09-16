from pathlib import Path

import msgspec
import polars as pl
import pytest

from export.artifacts import write_filter_index, write_full_entries, write_metadata_chunks
from export.catalogue import write_catalogue_artifacts
from export.contracts import AnimeCardMetadata, FrontendArtifactManifest
from export.manifest import validate_full_projection, validate_id_projection
from fetch.contracts import ExternalLink, Taxonomy, TenraiAnimeEntry, Trailer
from processing.artifacts import build_filter_metadata, validate_filter_metadata
from processing.contracts import CanonicalAnime, FilterMetadata, ProcessingArtifactManifest


def _record(anime_id: int, *, genre: str = 'Drama') -> CanonicalAnime:
    return CanonicalAnime(
        mal_id=anime_id,
        url=f'https://myanimelist.net/anime/{anime_id}',
        title=f'Anime {anime_id}',
        title_english=None,
        title_japanese=None,
        title_synonyms=(),
        anime_type='TV',
        source='Original',
        rating='PG - Children',
        season=None,
        episodes=12,
        duration_minutes=24,
        year=2024,
        status='Finished Airing',
        score=8.0,
        synopsis='A short synopsis.',
        synopsis_features='A short synopsis.',
        background=None,
        moreinfo=None,
        images=None,
        trailer=None,
        external=(),
        studios=(),
        producers=(),
        licensors=(),
        genres=(Taxonomy(mal_id=anime_id, name=genre),),
        themes=(),
        demographics=(),
        relations=(),
    )


def _entry(anime_id: int) -> TenraiAnimeEntry:
    return TenraiAnimeEntry(
        mal_id=anime_id,
        title=f'Anime {anime_id}',
        url=f'https://myanimelist.net/anime/{anime_id}',
        type='TV',
        rating='PG - Children',
        duration='24 min per ep',
        synopsis='A short synopsis.',
        trailer=Trailer(url='https://www.youtube.com/watch?v=example'),
        external=[ExternalLink(name='Official site', url='https://example.com')],
    )


def test_metadata_writer_output_matches_msgspec_contract(tmp_path: Path) -> None:
    metadata = (
        msgspec.to_builtins(AnimeCardMetadata(mal_id=1, title='One')),
        msgspec.to_builtins(AnimeCardMetadata(mal_id=2, title='Two')),
    )

    paths = write_metadata_chunks(metadata, output_dir=tmp_path, chunk_size=2)
    decoded = {}
    for path in paths:
        decoded.update(msgspec.json.decode(path.read_bytes(), type=dict[int, AnimeCardMetadata]))

    assert tuple(decoded) == (1, 2)
    assert decoded[1].title == 'One'


def test_full_entry_writer_emits_details_projection_and_recommendations(tmp_path: Path) -> None:
    entries = (_entry(1), _entry(2))

    paths = write_full_entries(
        entries,
        output_dir=tmp_path,
        recommendations={1: (2,)},
        chunk_size=500,
    )
    payload = msgspec.json.decode(paths[0].read_bytes(), type=dict[int, dict[str, object]])
    assert payload[1]['mal_id'] == 1
    assert payload[1]['url'] == 'https://myanimelist.net/anime/1'
    assert payload[1]['trailer'] == {'url': 'https://www.youtube.com/watch?v=example'}
    assert payload[1]['recommendations'] == [2]
    assert set(payload[1]) == {
        'mal_id',
        'title',
        'url',
        'title_english',
        'title_japanese',
        'type',
        'source',
        'episodes',
        'duration',
        'durationMinutes',
        'status',
        'year',
        'rating',
        'season',
        'score',
        'synopsis',
        'images',
        'trailer',
        'genres',
        'themes',
        'demographics',
        'studios',
        'recommendations',
    }


def test_filter_index_writer_output_has_aligned_postings_and_numeric_values(tmp_path: Path) -> None:
    records = (_record(20), _record(5, genre='Comedy'), _record(12))

    path = write_filter_index(records, output_dir=tmp_path)
    payload = msgspec.json.decode(path.read_bytes(), type=dict[str, object])
    ids = msgspec.convert(payload['ids'], type=list[int])
    numeric = msgspec.convert(payload['numeric'], type=dict[str, list[object]])
    categorical = msgspec.convert(payload['categorical'], type=dict[str, dict[str, list[int]]])

    assert ids == [5, 12, 20]
    assert numeric['episodes'] == [12, 12, 12]
    assert categorical['genre']['Drama'] == [12, 20]


def test_catalogue_writer_emits_typed_frontend_manifest(tmp_path: Path) -> None:
    write_catalogue_artifacts(
        (_record(1),),
        full_entries=(_entry(1),),
        output_dir=tmp_path,
        include_full_entries=False,
    )

    manifest = msgspec.json.decode((tmp_path / 'artifact-manifest.json').read_bytes(), type=FrontendArtifactManifest)

    assert manifest.metadata_count == 1
    assert manifest.full_entry_count == 0
    assert manifest.files
    assert manifest.search_metadata == 'search/anime-metadata-search.json'


def test_catalogue_writer_can_skip_full_entries_without_input(tmp_path: Path) -> None:
    write_catalogue_artifacts(
        (_record(1),),
        output_dir=tmp_path,
        include_full_entries=False,
    )

    manifest = msgspec.json.decode((tmp_path / 'artifact-manifest.json').read_bytes(), type=FrontendArtifactManifest)

    assert manifest.full_entry_count == 0
    assert manifest.full_files == ()


def test_catalogue_writer_rejects_duplicate_full_entries_before_projection(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match='unique anime IDs'):
        write_catalogue_artifacts(
            (_record(1),),
            full_entries=(_entry(1), _entry(1)),
            output_dir=tmp_path,
        )


def test_artifact_manifest_matches_msgspec_contract() -> None:
    manifest = ProcessingArtifactManifest(
        schema_version='search-v1',
        fetched_date='2026-09-06T00:00:00+00:00',
        anime_count=2,
        artifacts=(('metadata', 'metadata.json'),),
    )

    decoded = msgspec.json.decode(msgspec.json.encode(manifest), type=ProcessingArtifactManifest)

    assert decoded == manifest


def test_filter_metadata_uses_a_typed_aligned_contract() -> None:
    frame = pl.DataFrame(
        {
            'mal_id': [2, 1],
            'genres': [['Drama'], ['Comedy']],
            'themes': [[], ['School']],
            'studios': [[], ['Studio A']],
            'score': [8.0, None],
            'year': [2024, 2023],
            'episodes': [12, 24],
            'duration_minutes': [24, 86],
        }
    )

    metadata = build_filter_metadata(frame)

    assert isinstance(metadata, FilterMetadata)
    assert metadata.anime_ids == (1, 2)
    assert metadata.posting_lists['genres']['Drama'] == (2,)
    validate_filter_metadata(frame, metadata)


def test_canonical_parquet_fixture_has_expected_schema_and_alignment(tmp_path: Path) -> None:
    frame = pl.DataFrame(
        {
            'mal_id': [2, 1],
            'title': ['Two', 'One'],
            'anime_type': ['TV', 'MOVIE'],
            'rating_class': ['PG', 'G'],
            'genres': [['Drama'], ['Comedy']],
            'themes': [[], ['School']],
            'synopsis_features': ['A synopsis.', 'Another synopsis.'],
            'duration_minutes': [24, 86],
        }
    )
    path = tmp_path / 'canonical.parquet'
    frame.write_parquet(path)
    loaded = pl.read_parquet(path)

    assert loaded.schema['mal_id'] == pl.Int64
    assert loaded.schema['duration_minutes'] == pl.Int64
    assert loaded.get_column('mal_id').n_unique() == loaded.height
    assert loaded.get_column('mal_id').to_list() == [2, 1]


def test_projection_validators_reject_duplicate_ids(tmp_path: Path) -> None:
    ids_path = tmp_path / 'ids.json'
    ids_path.write_text('{"ids": [1, 1]}', encoding='utf-8')
    full_path = tmp_path / 'full.json'
    full_path.write_text('{"1": {}, "2": {}}', encoding='utf-8')

    with pytest.raises(ValueError, match='duplicate IDs'):
        validate_id_projection(ids_path, {1}, 'ids')
    with pytest.raises(ValueError, match='duplicate IDs'):
        validate_full_projection((full_path, full_path), {1, 2})
