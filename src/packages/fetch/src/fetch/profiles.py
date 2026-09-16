"""Typed catalogue profiles combining route, request, and acceptance policy."""

import msgspec

from fetch.filters import CatalogueFilters
from fetch.quality import CatalogueAcceptancePolicy
from fetch.routes import CatalogueRoute, TenraiAnimeRoute


class CatalogueProfile(msgspec.Struct, frozen=True):
    """Complete policy for one catalogue acquisition route."""

    name: str
    filters: CatalogueFilters
    acceptance_policy: CatalogueAcceptancePolicy = msgspec.field(default_factory=CatalogueAcceptancePolicy)
    route: CatalogueRoute = msgspec.field(default_factory=TenraiAnimeRoute)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError('catalogue profile name cannot be empty')

    @classmethod
    def sfw(cls, *, limit: int = 50) -> 'CatalogueProfile':
        """Return the standard safe-for-frontend catalogue profile."""
        filters = CatalogueFilters.sfw_catalogue(limit=limit)
        return cls('sfw', filters, _acceptance_policy(filters))

    @classmethod
    def r_plus(cls, *, limit: int = 50) -> 'CatalogueProfile':
        """Return the standard mature catalogue profile."""
        filters = CatalogueFilters.r_plus_catalogue(limit=limit)
        return cls('r-plus', filters, _acceptance_policy(filters))

    @classmethod
    def all_anime(cls, *, limit: int = 50) -> 'CatalogueProfile':
        """Return the unrestricted catalogue profile."""
        filters = CatalogueFilters.all_anime(limit=limit)
        return cls('all', filters, _acceptance_policy(filters))


def _acceptance_policy(filters: CatalogueFilters) -> CatalogueAcceptancePolicy:
    excluded_genres = frozenset(int(value) for value in (filters.genres_exclude or '').split(',') if value.strip())
    return CatalogueAcceptancePolicy(excluded_genre_ids=excluded_genres)
