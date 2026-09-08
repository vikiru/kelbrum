from pathlib import Path

import msgspec
import polars as pl

from export.artifacts import write_filter_index, write_full_entries, write_metadata_chunks
from models.artifacts import ArtifactManifest
from models.contracts import AnimeMetadata, RecommendationScore
from models.tenrai import CanonicalAnime, Taxonomy, TenraiAnimeEntry


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
        streaming=(),
        theme=None,
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
        type='TV',
        rating='PG - Children',
        duration='24 min per ep',
        synopsis='A short synopsis.',
    )


def test_metadata_writer_output_matches_msgspec_contract(tmp_path: Path) -> None:
    metadata = (
        msgspec.to_builtins(AnimeMetadata(mal_id=1, title='One')),
        msgspec.to_builtins(AnimeMetadata(mal_id=2, title='Two')),
    )

    paths = write_metadata_chunks(metadata, output_dir=tmp_path, chunk_size=2)
    decoded = {}
    for path in paths:
        decoded.update(msgspec.json.decode(path.read_bytes(), type=dict[int, AnimeMetadata]))

    assert tuple(decoded) == (1, 2)
    assert decoded[1].title == 'One'


def test_full_entry_writer_preserves_tenrai_shape_and_recommendation_payload(tmp_path: Path) -> None:
    entries = (_entry(1), _entry(2))
    scores = {1: (RecommendationScore(anime_id=2, score=0.42),)}

    paths = write_full_entries(
        entries,
        output_dir=tmp_path,
        recommendations={1: (2,)},
        recommendation_scores=scores,
        chunk_size=500,
    )
    payload = msgspec.json.decode(paths[0].read_bytes(), type=dict[int, dict[str, object]])
    source_entries = msgspec.json.decode(paths[0].read_bytes(), type=dict[int, TenraiAnimeEntry])

    assert source_entries[1].mal_id == 1
    assert payload[1]['mal_id'] == 1
    assert payload[1]['recommendations'] == [2]
    assert payload[1]['recommendationScores'] == [{'animeId': 2, 'score': 0.42}]


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


def test_artifact_manifest_matches_msgspec_contract() -> None:
    manifest = ArtifactManifest(
        schema_version='search-v1',
        fetched_date='2026-09-06T00:00:00+00:00',
        anime_count=2,
        artifacts=(('metadata', 'metadata.json'),),
    )

    decoded = msgspec.json.decode(msgspec.json.encode(manifest), type=ArtifactManifest)

    assert decoded == manifest


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
