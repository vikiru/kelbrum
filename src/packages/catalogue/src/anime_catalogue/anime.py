"""Immutable indexed access to normalized anime catalogue rows."""

from collections.abc import Mapping, Sequence

import msgspec
import polars as pl


class AnimeEntry(msgspec.Struct, frozen=True):
    """Immutable local view of one catalogue entry with entry-level semantics."""

    anime_id: int
    title: str
    genres: tuple[str, ...]
    themes: tuple[str, ...]
    demographics: tuple[str, ...]
    rating: str
    synopsis_features: str

    def preferred_title(self) -> str:
        """Return the display title selected for this entry."""
        return self.title

    def genre_names(self) -> tuple[str, ...]:
        """Return the normalized genre labels for this entry."""
        return self.genres

    def theme_names(self) -> tuple[str, ...]:
        """Return the normalized theme labels for this entry."""
        return self.themes

    def has_synopsis(self) -> bool:
        """Return whether this entry has usable synopsis text."""
        return bool(self.synopsis_features.strip())


class AnimeCatalogue(msgspec.Struct, frozen=True):
    """Stable row-aligned catalogue facts used by downstream components."""

    anime_ids: tuple[int, ...]
    titles: tuple[str, ...]
    genres: tuple[tuple[str, ...], ...]
    themes: tuple[tuple[str, ...], ...]
    demographics: tuple[tuple[str, ...], ...]
    ratings: tuple[str, ...]
    synopsis_features: tuple[str, ...]
    index_by_id: Mapping[int, int]

    def __post_init__(self) -> None:
        row_count = len(self.anime_ids)
        if any(anime_id <= 0 for anime_id in self.anime_ids):
            raise ValueError('catalogue IDs must be positive')
        if len(set(self.anime_ids)) != row_count:
            raise ValueError('catalogue IDs must be unique')
        aligned = (self.titles, self.genres, self.themes, self.demographics, self.ratings, self.synopsis_features)
        if any(len(values) != row_count for values in aligned):
            raise ValueError('catalogue fields must have equal row counts')
        expected_index = {anime_id: row for row, anime_id in enumerate(self.anime_ids)}
        if dict(self.index_by_id) != expected_index:
            raise ValueError('catalogue ID index does not match row order')

    @classmethod
    def from_frame(cls, frame: pl.DataFrame) -> 'AnimeCatalogue':
        """Build an indexed catalogue from one normalized, ordered frame."""
        required = {'mal_id', 'title', 'genres', 'themes', 'demographics', 'synopsis_features'}
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f'catalogue frame is missing columns: {sorted(missing)}')
        rating_column = 'rating_class' if 'rating_class' in frame.columns else 'rating'
        if rating_column not in frame.columns:
            raise ValueError('catalogue frame is missing rating or rating_class')
        anime_ids = tuple(int(value) for value in frame['mal_id'].to_list())
        return cls(
            anime_ids=anime_ids,
            titles=tuple(str(value) for value in frame['title'].to_list()),
            genres=_tuple_columns(frame['genres'].to_list()),
            themes=_tuple_columns(frame['themes'].to_list()),
            demographics=_tuple_columns(frame['demographics'].to_list()),
            ratings=tuple(str(value or '') for value in frame[rating_column].to_list()),
            synopsis_features=tuple(str(value or '') for value in frame['synopsis_features'].to_list()),
            index_by_id={anime_id: row for row, anime_id in enumerate(anime_ids)},
        )

    @property
    def row_count(self) -> int:
        return len(self.anime_ids)

    def row_for_id(self, anime_id: int) -> int:
        try:
            return self.index_by_id[anime_id]
        except KeyError as error:
            raise KeyError(f'anime ID not found in catalogue: {anime_id}') from error

    def id_for_row(self, row: int) -> int:
        try:
            return self.anime_ids[row]
        except IndexError as error:
            raise IndexError(f'catalogue row out of range: {row}') from error

    def title_for_id(self, anime_id: int) -> str:
        return self.titles[self.row_for_id(anime_id)]

    def entry_for_id(self, anime_id: int) -> AnimeEntry:
        """Return one local entry view without materializing the collection."""
        return self.entry_for_row(self.row_for_id(anime_id))

    def entry_for_row(self, row: int) -> AnimeEntry:
        """Return one local entry view by aligned row number."""
        try:
            return AnimeEntry(
                anime_id=self.anime_ids[row],
                title=self.titles[row],
                genres=self.genres[row],
                themes=self.themes[row],
                demographics=self.demographics[row],
                rating=self.ratings[row],
                synopsis_features=self.synopsis_features[row],
            )
        except IndexError as error:
            raise IndexError(f'catalogue row out of range: {row}') from error

    def synopsis_available(self, anime_id: int) -> bool:
        return bool(self.synopsis_features[self.row_for_id(anime_id)].strip())

    def validate_aligned_ids(self, aligned_ids: Sequence[int], *, source_name: str = 'aligned data') -> None:
        """Reject feature or cache rows that do not use this catalogue's ID order."""
        expected = self.anime_ids
        actual = tuple(aligned_ids)
        if actual != expected:
            raise ValueError(f'{source_name} IDs do not match catalogue row order')


def _tuple_columns(values: Sequence[object]) -> tuple[tuple[str, ...], ...]:
    return tuple(_string_values(row) for row in values)


def _string_values(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError('catalogue list columns must contain sequences or null values')
    return tuple(str(item) for item in value)


def order_catalogue_frame(frame: pl.DataFrame) -> pl.DataFrame:
    """Return the canonical stable MAL-ID row order used by downstream stores."""
    if 'mal_id' not in frame.columns:
        raise ValueError('catalogue frame is missing mal_id')
    return frame.sort('mal_id')
