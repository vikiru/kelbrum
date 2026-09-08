"""Explicit Tenrai catalogue request filters."""

from collections.abc import Mapping

import msgspec

MAX_PAGE_SIZE = 50


class CatalogueFilters(msgspec.Struct, frozen=True):
    limit: int = MAX_PAGE_SIZE
    anime_types: tuple[str, ...] | None = ('tv', 'ona', 'movie')
    query: str | None = None
    status: str | None = None
    ratings: tuple[str, ...] = ()
    sfw: bool | None = None
    sfw_strict: bool = True
    unapproved: bool | None = None
    score: float | None = None
    min_score: float | None = None
    max_score: float | None = None
    genres: str | None = None
    genres_exclude: str | None = '9,12,49'
    order_by: str | None = None
    sort: str | None = None
    letter: str | None = None
    producers: str | None = None
    start_date: str | None = None
    end_date: str | None = None

    @classmethod
    def sfw_catalogue(cls, *, limit: int = MAX_PAGE_SIZE) -> 'CatalogueFilters':
        """Return the default catalogue policy for safe frontend content."""
        return cls(limit=limit, anime_types=('tv', 'ona', 'movie'), genres_exclude='9,12,49', sfw_strict=False)

    @classmethod
    def all_anime(cls, *, limit: int = MAX_PAGE_SIZE) -> 'CatalogueFilters':
        """Return the unrestricted any-type, any-rating catalogue."""
        return cls(limit=limit, anime_types=None, genres_exclude=None, sfw_strict=False)

    @classmethod
    def r_plus_catalogue(cls, *, limit: int = MAX_PAGE_SIZE) -> 'CatalogueFilters':
        """Return the curated R+ catalogue with supported types and excluded genres."""
        return cls(
            limit=limit,
            anime_types=('tv', 'ona', 'movie'),
            ratings=('r',),
            genres_exclude='9,12,49',
            sfw_strict=False,
        )

    def signature(self) -> tuple[tuple[str, str], ...]:
        """Return the stable request settings used to validate a resume."""
        return tuple(sorted((key, str(value)) for key, value in self.as_params(1).items() if key != 'page'))

    def as_params(self, page: int) -> Mapping[str, str | list[str] | None]:
        if not 1 <= self.limit <= MAX_PAGE_SIZE:
            raise ValueError(f'limit must be between 1 and {MAX_PAGE_SIZE}')
        if page < 1:
            raise ValueError('page must be positive')
        params: dict[str, str | list[str] | None] = {
            'page': str(page),
            'limit': str(self.limit),
        }
        if self.anime_types is not None:
            params['type'] = ','.join(self.anime_types)
        if self.genres_exclude is not None:
            params['genres_exclude'] = self.genres_exclude
        if self.sfw_strict:
            params['sfw-strict'] = 'true'
        optional: dict[str, str | list[str] | None] = {
            'q': self.query,
            'status': self.status,
            'rating': ','.join(self.ratings) or None,
            'sfw': str(self.sfw).lower() if self.sfw is not None else None,
            'unapproved': str(self.unapproved).lower() if self.unapproved is not None else None,
            'score': str(self.score) if self.score is not None else None,
            'min_score': str(self.min_score) if self.min_score is not None else None,
            'max_score': str(self.max_score) if self.max_score is not None else None,
            'genres': self.genres,
            'order_by': self.order_by,
            'sort': self.sort,
            'letter': self.letter,
            'producers': self.producers,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }
        params.update({key: value for key, value in optional.items() if value is not None})
        return params
