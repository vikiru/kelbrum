"""Kelbrum fetch package."""

from fetch.profiles import CatalogueProfile
from fetch.quality import CatalogueAcceptancePolicy, FilterDecision, filter_catalogue
from fetch.routes import CatalogueRoute, TenraiAnimeRoute

__all__ = [
    'CatalogueAcceptancePolicy',
    'CatalogueProfile',
    'CatalogueRoute',
    'FilterDecision',
    'TenraiAnimeRoute',
    'filter_catalogue',
]
