from pathlib import Path

import msgspec
import pytest

from export.artifacts import write_filter_index, write_metadata_chunks
from export.contracts import AnimeCardMetadata
from fetch.contracts import Taxonomy
from processing.contracts import CanonicalAnime


def _record(
    anime_id: int,
    *,
    rating: str | None = None,
    year: int | None = None,
    genre: str | None = None,
) -> CanonicalAnime:
    genres = () if genre is None else (Taxonomy(mal_id=anime_id, name=genre),)
    return CanonicalAnime(
        mal_id=anime_id,
        url=None,
        title=f'Anime {anime_id}',
        title_english=None,
        title_japanese=None,
        title_synonyms=(),
        anime_type='TV',
        source=None,
        rating=rating,
        season=None,
        episodes=None,
        duration_minutes=None,
        year=year,
        status=None,
        score=None,
        synopsis=None,
        synopsis_features=None,
        background=None,
        moreinfo=None,
        images=None,
        trailer=None,
        external=(),
        studios=(),
        producers=(),
        licensors=(),
        genres=genres,
        themes=(),
        demographics=(),
        relations=(),
    )


def test_filter_index_sorts_ids_and_postings_without_breaking_numeric_alignment(tmp_path: Path) -> None:
    records = (
        _record(20, rating='R', year=2014, genre='Drama'),
        _record(5, rating='G', year=1988, genre='Drama'),
        _record(12, rating='R', year=None),
    )

    write_filter_index(records, output_dir=tmp_path)
    payload = msgspec.json.decode((tmp_path / 'filter-index.json').read_bytes())

    assert payload['ids'] == [5, 12, 20]
    assert payload['categorical']['rating']['R'] == [12, 20]
    assert payload['categorical']['genre']['Drama'] == [5, 20]
    assert payload['numeric']['year'] == [1988, None, 2014]


def test_filter_index_rejects_duplicate_ids(tmp_path: Path) -> None:
    records = (_record(5), _record(5))

    with pytest.raises(ValueError, match='unique MAL IDs'):
        write_filter_index(records, output_dir=tmp_path)


def test_metadata_writer_rejects_duplicate_ids_before_projection(tmp_path: Path) -> None:
    metadata = (
        msgspec.to_builtins(AnimeCardMetadata(mal_id=1, title='One')),
        msgspec.to_builtins(AnimeCardMetadata(mal_id=1, title='Duplicate')),
    )

    with pytest.raises(ValueError, match='unique anime IDs'):
        write_metadata_chunks(metadata, output_dir=tmp_path)
