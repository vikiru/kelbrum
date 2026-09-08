"""HTTP transport for the Tenrai API."""

import msgspec
import niquests

from config import Settings, bind_logger
from fetch.filters import CatalogueFilters
from fetch.rate_limit import RequestPacer
from fetch.retry import RETRYABLE_STATUSES, pause, retry_delay
from models.decoding import decode_catalogue
from models.tenrai import TenraiAnimeEntry, TenraiListResponse, TenraiObjectResponse

HTTP_OK = 200


class TenraiTransport:
    """Perform typed Tenrai requests without checkpoint or file concerns."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = niquests.Session()
        self._pacer = RequestPacer(settings.requests_per_second)
        self._log = bind_logger(package='fetch', stage='catalogue')

    def close(self) -> None:
        self._session.close()

    def catalogue_page(self, page: int, *, filters: CatalogueFilters) -> TenraiListResponse[TenraiAnimeEntry]:
        """Fetch and decode one filtered catalogue page."""
        url = f'{self._settings.tenrai_base_url}/anime'
        for attempt in range(self._settings.max_retries + 1):
            response = self._session.get(
                url,
                params=filters.as_params(page),
                timeout=self._settings.timeout_seconds,
            )
            status_code = response.status_code
            if status_code is None:
                raise RuntimeError(f'Tenrai response had no status on page {page}')
            if status_code == HTTP_OK:
                if response.content is None:
                    raise RuntimeError(f'Tenrai response had no content on page {page}')
                return decode_catalogue(response.content)
            if status_code not in RETRYABLE_STATUSES or attempt == self._settings.max_retries:
                raise RuntimeError(f'Tenrai request failed with HTTP {status_code} on page {page}')
            retry_after = response.headers.get('Retry-After')
            delay = retry_delay(status_code, attempt, retry_after)
            self._log.warning('Retrying page {} after HTTP {} in {:.1f}s.', page, status_code, delay)
            pause(delay)
        raise RuntimeError(f'Tenrai request exhausted retries on page {page}')

    def full_entry(self, anime_id: int) -> TenraiAnimeEntry:
        """Fetch and decode one complete anime record."""
        url = f'{self._settings.tenrai_base_url}/anime/{anime_id}/full'
        for attempt in range(self._settings.max_retries + 1):
            response = self._session.get(url, timeout=self._settings.timeout_seconds)
            status_code = response.status_code
            if status_code is None:
                raise RuntimeError(f'Tenrai response had no status for anime {anime_id}')
            if status_code == HTTP_OK:
                if response.content is None:
                    raise RuntimeError(f'Tenrai response had no content for anime {anime_id}')
                try:
                    envelope = msgspec.json.decode(response.content, type=TenraiObjectResponse[TenraiAnimeEntry])
                except (msgspec.DecodeError, msgspec.ValidationError) as error:
                    raise RuntimeError(f'Tenrai full response had invalid data for anime {anime_id}') from error
                return envelope.data
            if status_code not in RETRYABLE_STATUSES or attempt == self._settings.max_retries:
                raise RuntimeError(f'Tenrai full request failed with HTTP {status_code} for anime {anime_id}')
            pause(retry_delay(status_code, attempt, response.headers.get('Retry-After')))
        raise RuntimeError(f'Tenrai full request exhausted retries for anime {anime_id}')

    def wait(self) -> None:
        """Respect the configured request rate after a completed request."""
        self._pacer.wait()
