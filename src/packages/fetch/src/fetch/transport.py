"""HTTP transport for the Tenrai API."""

from collections.abc import Mapping

import msgspec
import niquests

from config import Settings, bind_logger
from fetch.contracts import TenraiAnimeEntry, TenraiListResponse, TenraiObjectResponse
from fetch.decoding import decode_catalogue
from fetch.errors import FetchError
from fetch.filters import CatalogueFilters
from fetch.rate_limit import RequestPacer
from fetch.retry import RETRYABLE_STATUSES, pause, retry_delay
from fetch.routes import CatalogueRoute, TenraiAnimeRoute

HTTP_OK = 200


class TenraiTransport:
    """Perform typed Tenrai requests without checkpoint or file concerns."""

    def __init__(self, settings: Settings, route: CatalogueRoute | None = None) -> None:
        self._settings = settings
        self._route = route or TenraiAnimeRoute()
        self._session = niquests.Session()
        self._pacer = RequestPacer(settings.requests_per_second)
        self._log = bind_logger(package='fetch', stage='catalogue')

    def close(self) -> None:
        self._session.close()

    @property
    def route_name(self) -> str:
        """Return the stable route identity used for resumable artifacts."""
        return self._route.name

    @property
    def catalogue_url(self) -> str:
        """Return the route's catalogue endpoint for provenance metadata."""
        return self._route.catalogue_url(self._settings.tenrai_base_url)

    def _get_with_retries(
        self,
        url: str,
        *,
        target: str,
        params: Mapping[str, str | list[str] | None] | None = None,
    ) -> bytes:
        """Execute a GET request with retries on transient HTTP and transport failures."""
        for attempt in range(self._settings.max_retries + 1):
            try:
                if params is None:
                    response = self._session.get(url, timeout=self._settings.timeout_seconds)
                else:
                    response = self._session.get(url, params=params, timeout=self._settings.timeout_seconds)
            except (niquests.RequestException, TimeoutError) as error:
                if attempt == self._settings.max_retries:
                    raise FetchError(f'Tenrai request failed for {target}: {error}') from error
                delay = retry_delay(0, attempt, None)
                self._log.warning('Retrying {} after transport error ({}) in {:.1f}s.', target, error, delay)
                pause(delay)
                continue

            status_code = response.status_code
            if status_code is None:
                raise FetchError(f'Tenrai response had no status for {target}')
            if status_code == HTTP_OK:
                if response.content is None:
                    raise FetchError(f'Tenrai response had no content for {target}')
                return response.content
            if status_code not in RETRYABLE_STATUSES or attempt == self._settings.max_retries:
                raise FetchError(f'Tenrai request failed with HTTP {status_code} for {target}')
            retry_after = response.headers.get('Retry-After')
            delay = retry_delay(status_code, attempt, retry_after)
            self._log.warning('Retrying {} after HTTP {} in {:.1f}s.', target, status_code, delay)
            pause(delay)
        raise FetchError(f'Tenrai request exhausted retries for {target}')

    def catalogue_page(self, page: int, *, filters: CatalogueFilters) -> TenraiListResponse[TenraiAnimeEntry]:
        """Fetch and decode one filtered catalogue page."""
        url = self._route.catalogue_url(self._settings.tenrai_base_url)
        content = self._get_with_retries(url, params=filters.as_params(page), target=f'page {page}')
        return decode_catalogue(content)

    def full_entry(self, anime_id: int) -> TenraiAnimeEntry:
        """Fetch and decode one complete anime record."""
        url = self._route.full_entry_url(self._settings.tenrai_base_url, anime_id)
        content = self._get_with_retries(url, target=f'anime {anime_id}')
        try:
            envelope = msgspec.json.decode(content, type=TenraiObjectResponse[TenraiAnimeEntry])
        except (msgspec.DecodeError, msgspec.ValidationError) as error:
            raise FetchError(f'Tenrai full response had invalid data for anime {anime_id}') from error
        return envelope.data

    def wait(self) -> None:
        """Respect the configured request rate after a completed request."""
        self._pacer.wait()
