"""Canonical genre/theme identities and explicit external-label boundaries."""

import msgspec
import pytest

from anime_catalogue.taxonomy import Genre, Theme, parse_genre, parse_theme


@pytest.mark.parametrize('label', ['sci_fi', 'Sci-Fi', 'Sci Fi', ' SCI-FI '])
def test_genre_labels_parse_to_one_canonical_member(label: str) -> None:
    assert parse_genre(label) is Genre.SCI_FI


@pytest.mark.parametrize('label', ['slice_of_life', 'Slice of Life', 'slice-of-life'])
def test_compound_genre_labels_parse_consistently(label: str) -> None:
    assert parse_genre(label) is Genre.SLICE_OF_LIFE


def test_theme_labels_parse_at_the_boundary() -> None:
    assert parse_theme('High Stakes Game') is Theme.HIGH_STAKES_GAME
    assert parse_theme(Theme.SCHOOL) is Theme.SCHOOL
    assert parse_genre(Genre.DRAMA) is Genre.DRAMA


@pytest.mark.parametrize('label', ['erotica', 'hentai', 'Hentai', 'Erotica'])
def test_explicit_categories_are_not_supported(label: str) -> None:
    with pytest.raises(ValueError, match='genre'):
        parse_genre(label)
    with pytest.raises(ValueError, match='theme'):
        parse_theme(label)


def test_unknown_and_wrong_field_labels_are_rejected() -> None:
    with pytest.raises(ValueError, match='genre'):
        parse_genre('music')
    with pytest.raises(ValueError, match='theme'):
        parse_theme('action')
    with pytest.raises(TypeError, match='genre'):
        parse_genre(Theme.GOURMET)
    with pytest.raises(TypeError, match='theme'):
        parse_theme(Genre.SLICE_OF_LIFE)


def test_enum_values_preserve_wire_format() -> None:
    assert msgspec.json.encode((Genre.SCI_FI, Theme.SCHOOL)) == b'["sci_fi","school"]'
    assert isinstance(Genre.DRAMA, str)
    assert {'sci_fi': 2.0}[Genre.SCI_FI] == 2.0
    assert {member.value for member in Genre}.isdisjoint({'erotica', 'hentai'})
    assert {member.value for member in Theme}.isdisjoint({'erotica', 'hentai'})


def test_invalid_enum_member_names_fail_immediately() -> None:
    assert not hasattr(Genre, 'MUSIC')
    assert not hasattr(Theme, 'ACTION')
    assert not hasattr(Theme, 'REHABILITATION')


@pytest.mark.parametrize('label', ['disability', 'magic', 'mystery', 'fantasy'])
def test_genres_and_tags_are_not_accepted_as_themes(label: str) -> None:
    with pytest.raises(ValueError, match='theme'):
        parse_theme(label)
