import polars as pl
import pytest

from anime_catalogue import AnimeCatalogue, ids_with_genre, ids_with_theme, iter_entries
from anime_catalogue.taxonomy import Genre, Theme


def test_entry_view_exposes_local_semantics_without_changing_catalogue_alignment() -> None:
    catalogue = AnimeCatalogue.from_frame(
        pl.DataFrame(
            {
                'mal_id': [20],
                'title': ['Example'],
                'genres': [['Drama']],
                'themes': [['School']],
                'demographics': [['Shounen']],
                'rating': ['PG'],
                'synopsis_features': ['  has text  '],
            }
        )
    )

    entry = catalogue.entry_for_id(20)

    assert entry.preferred_title() == 'Example'
    assert entry.genres == (Genre.DRAMA,)
    assert entry.themes == (Theme.SCHOOL,)
    assert entry.genre_names() == ('drama',)
    assert entry.theme_names() == ('school',)
    assert entry.has_synopsis()
    assert catalogue.row_for_id(entry.anime_id) == 0


def test_entry_lookup_reports_unknown_ids_and_rows() -> None:
    catalogue = AnimeCatalogue(
        anime_ids=(1,),
        titles=('Example',),
        genres=((),),
        themes=((),),
        demographics=((),),
        ratings=('G',),
        synopsis_features=('',),
        index_by_id={1: 0},
    )

    with pytest.raises(KeyError, match='not found'):
        catalogue.entry_for_id(2)
    with pytest.raises(IndexError, match='out of range'):
        catalogue.entry_for_row(2)


def test_catalogue_queries_preserve_stable_id_order() -> None:
    catalogue = AnimeCatalogue(
        anime_ids=(20, 10),
        titles=('Drama', 'Action'),
        genres=((Genre.DRAMA,), (Genre.DRAMA, Genre.ACTION)),
        themes=((Theme.SCHOOL,), (Theme.ISEKAI,)),
        demographics=((), ()),
        ratings=('PG', 'G'),
        synopsis_features=('', ''),
        index_by_id={20: 0, 10: 1},
    )

    assert tuple(entry.anime_id for entry in iter_entries(catalogue)) == (20, 10)
    assert ids_with_genre(catalogue, 'Drama') == (20, 10)
    assert ids_with_theme(catalogue, Theme.ISEKAI) == (10,)
