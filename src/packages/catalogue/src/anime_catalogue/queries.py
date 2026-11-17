"""Focused, read-only queries over an indexed anime catalogue."""

from collections.abc import Iterator

from anime_catalogue.anime import AnimeCatalogue, AnimeEntry
from anime_catalogue.taxonomy import Genre, Theme, parse_genre, parse_theme


def iter_entries(catalogue: AnimeCatalogue) -> Iterator[AnimeEntry]:
    """Yield entry views in the catalogue's stable row order."""
    for row in range(catalogue.row_count):
        yield catalogue.entry_for_row(row)


def ids_with_genre(catalogue: AnimeCatalogue, genre: str | Genre) -> tuple[int, ...]:
    """Return IDs whose normalized genre labels contain ``genre``."""
    genre_id = parse_genre(genre)
    return tuple(
        anime_id for anime_id, genres in zip(catalogue.anime_ids, catalogue.genres, strict=True) if genre_id in genres
    )


def ids_with_theme(catalogue: AnimeCatalogue, theme: str | Theme) -> tuple[int, ...]:
    """Return IDs whose normalized theme labels contain ``theme``."""
    theme_id = parse_theme(theme)
    return tuple(
        anime_id for anime_id, themes in zip(catalogue.anime_ids, catalogue.themes, strict=True) if theme_id in themes
    )
