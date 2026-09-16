from pathlib import Path

import msgspec

from fetch.contracts import AnimeRelation, NamedResource, RelationEntry, Taxonomy
from processing.build import ProcessingResult, canonical_frame
from processing.contracts import CanonicalAnime
from processing.eligibility import EligibilityAudit
from processing.persistence import load_canonical_parquet, write_canonical_parquet


def _record(anime_id: int) -> CanonicalAnime:
    return CanonicalAnime(
        mal_id=anime_id,
        url=None,
        title=f'Anime {anime_id}',
        title_english=None,
        title_japanese=None,
        title_synonyms=(),
        anime_type='TV',
        source='Original',
        rating='PG',
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
        genres=(),
        themes=(),
        demographics=(),
        relations=(),
    )


def test_canonical_parquet_round_trip_preserves_downstream_fields(tmp_path: Path) -> None:
    record = msgspec.structs.replace(
        _record(10),
        url='https://example.test/anime/10',
        title_synonyms=('Alias',),
        season='spring',
        background='Background',
        moreinfo='More information',
        studios=(NamedResource(20, 'Studio', 'anime', 'https://example.test/studio/20'),),
        genres=(Taxonomy(30, 'Drama', 'anime', 'https://example.test/genre/30'),),
        relations=(AnimeRelation('Sequel', [RelationEntry(11, 'anime', 'Next')]),),
    )
    result = ProcessingResult(
        records=(record,),
        audit=EligibilityAudit(1, 0, (), (), ()),
        duplicate_ids=(),
    )
    path = tmp_path / 'canonical.parquet'

    write_canonical_parquet(result, path)

    assert load_canonical_parquet(path) == (record,)
    assert canonical_frame((record,)).height == 1
