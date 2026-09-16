"""Synchronous Tenrai client composed from transport and fetch workflows."""

from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from pathlib import Path  # noqa: TC003

import loguru  # noqa: TC002

from config import Settings, bind_logger
from fetch.catalogue import FetchSummary, acquire_catalogue
from fetch.contracts import TenraiAnimeEntry, TenraiListResponse  # noqa: TC001
from fetch.enrichment import enrich_entries
from fetch.errors import FetchError
from fetch.filters import CatalogueFilters
from fetch.profiles import CatalogueProfile  # noqa: TC001
from fetch.quality import CatalogueAcceptancePolicy
from fetch.routes import CatalogueRoute  # noqa: TC001
from fetch.transport import TenraiTransport


class _FetchLoggerAdapter:
    def __init__(self, logger: loguru.Logger) -> None:
        self._logger = logger

    def info(self, message: str, *args: object) -> None:
        self._logger.info(message, *args)


class TenraiClient:
    """Small synchronous client with independently testable fetch workflows."""

    def __init__(
        self,
        settings: Settings | None = None,
        route: CatalogueRoute | None = None,
        *,
        profile: CatalogueProfile | None = None,
    ) -> None:
        self.settings = settings or Settings()
        if route is not None and profile is not None and route.name != profile.route.name:
            raise ValueError('explicit route does not match the catalogue profile route')
        self._profile = profile
        self._transport = TenraiTransport(self.settings, route=route or (profile.route if profile else None))
        self.last_summary: FetchSummary | None = None
        self._log = bind_logger(package='fetch', stage='catalogue')

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> TenraiClient:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    @property
    def route_name(self) -> str:
        """Return the configured route identity for persisted fetch artifacts."""
        return self._transport.route_name

    @property
    def catalogue_url(self) -> str:
        """Return the configured catalogue endpoint for persisted provenance."""
        return self._transport.catalogue_url

    def catalogue_page(
        self, page: int, *, filters: CatalogueFilters | None = None
    ) -> TenraiListResponse[TenraiAnimeEntry]:
        """Fetch and type-check one filtered Tenrai catalogue page."""
        active_filters = filters or (self._profile.filters if self._profile else CatalogueFilters.sfw_catalogue())
        try:
            return self._transport.catalogue_page(page, filters=active_filters)
        except RuntimeError as error:
            raise FetchError(str(error)) from error

    def full_entry(self, anime_id: int) -> TenraiAnimeEntry:
        """Fetch one complete anime record for explicit enrichment."""
        if anime_id <= 0:
            raise ValueError('anime_id must be positive')
        try:
            return self._transport.full_entry(anime_id)
        except RuntimeError as error:
            raise FetchError(str(error)) from error

    def wait(self) -> None:
        """Respect the configured request rate after a completed request."""
        self._transport.wait()

    def enrich(
        self,
        anime_ids: Sequence[int],
        output_path: Path,
        *,
        overwrite: bool = False,
        profile: str | None = None,
    ) -> tuple[TenraiAnimeEntry, ...]:
        """Fetch and persist a deterministic merged full catalogue for explicit IDs."""
        return enrich_entries(self, anime_ids, output_path, overwrite=overwrite, profile=profile)

    def catalogue(
        self,
        last_page: int | None = None,
        *,
        entries_path: Path,
        filters: CatalogueFilters | None = None,
        checkpoint_path: Path | None = None,
        overwrite: bool = False,
    ) -> list[TenraiAnimeEntry]:
        """Fetch, accept, and persist one deterministic catalogue snapshot."""
        if self._profile is not None and filters is not None and filters != self._profile.filters:
            raise ValueError('explicit filters do not match the catalogue profile')
        active_filters = self._resolve_filters(filters)
        entries, summary = acquire_catalogue(
            self,
            last_page=last_page,
            entries_path=entries_path,
            filters=active_filters,
            checkpoint_path=checkpoint_path,
            overwrite=overwrite,
            profile_name=self._profile_name,
            acceptance_policy=self._resolve_acceptance_policy(active_filters),
            log=_FetchLoggerAdapter(self._log),
        )
        self.last_summary = summary
        return entries

    @property
    def _profile_name(self) -> str:
        return self._profile.name if self._profile is not None else '-'

    def _resolve_filters(self, filters: CatalogueFilters | None) -> CatalogueFilters:
        """Resolve explicit, profile, or default catalogue filters."""
        return filters or (self._profile.filters if self._profile else CatalogueFilters.sfw_catalogue())

    def _resolve_acceptance_policy(self, filters: CatalogueFilters) -> CatalogueAcceptancePolicy:
        """Resolve the profile policy or derive one from filter exclusions."""
        if self._profile is not None:
            return self._profile.acceptance_policy
        excluded_genre_ids = frozenset(int(value) for value in (filters.genres_exclude or '').split(',') if value)
        return CatalogueAcceptancePolicy(excluded_genre_ids=excluded_genre_ids)
