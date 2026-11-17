"""Kelbrum fetch package."""

from fetch.profiles import CatalogueProfile
from fetch.quality import CatalogueAcceptancePolicy, FilterDecision, filter_catalogue
from fetch.routes import CatalogueRoute, TenraiAnimeRoute
from fetch.updates import UpdateResult, update_anime_records, update_profile_catalogue

__all__ = [
    'CatalogueAcceptancePolicy',
    'CatalogueProfile',
    'CatalogueRoute',
    'FilterDecision',
    'TenraiAnimeRoute',
    'UpdateResult',
    'filter_catalogue',
    'update_anime_records',
    'update_profile_catalogue',
]
