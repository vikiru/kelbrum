"""Route adapters for typed catalogue endpoints."""

from typing import Protocol


class CatalogueRoute(Protocol):
    """URL strategy for paginated catalogue and full-entry requests."""

    name: str

    def catalogue_url(self, base_url: str) -> str: ...

    def full_entry_url(self, base_url: str, anime_id: int) -> str: ...


class TenraiAnimeRoute:
    """Default Tenrai anime route."""

    name = 'tenrai-anime'

    def catalogue_url(self, base_url: str) -> str:
        return f'{base_url.rstrip("/")}/anime'

    def full_entry_url(self, base_url: str, anime_id: int) -> str:
        if anime_id <= 0:
            raise ValueError('anime_id must be positive')
        return f'{base_url.rstrip("/")}/anime/{anime_id}/full'
