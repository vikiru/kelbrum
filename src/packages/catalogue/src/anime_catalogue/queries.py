"""Focused, read-only queries over an indexed anime catalogue."""

from collections.abc import Callable, Iterator

from anime_catalogue.anime import AnimeCatalogue, AnimeEntry


def iter_entries(catalogue: AnimeCatalogue) -> Iterator[AnimeEntry]:
    """Yield entry views in the catalogue's stable row order."""
    for row in range(catalogue.row_count):
        yield catalogue.entry_for_row(row)


def ids_with_genre(catalogue: AnimeCatalogue, genre: str) -> tuple[int, ...]:
    """Return IDs whose normalized genre labels contain ``genre``."""
    return _ids_matching(catalogue, lambda entry: genre in entry.genres)


def ids_with_theme(catalogue: AnimeCatalogue, theme: str) -> tuple[int, ...]:
    """Return IDs whose normalized theme labels contain ``theme``."""
    return _ids_matching(catalogue, lambda entry: theme in entry.themes)


def _ids_matching(catalogue: AnimeCatalogue, matches: Callable[[AnimeEntry], bool]) -> tuple[int, ...]:
    return tuple(entry.anime_id for entry in iter_entries(catalogue) if matches(entry))
