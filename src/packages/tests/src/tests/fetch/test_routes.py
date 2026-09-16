from pathlib import Path
from typing import ClassVar

import msgspec
import pytest

from config import Settings
from fetch.catalogue import _validate_checkpoint
from fetch.checkpoint import FetchCheckpoint
from fetch.client import TenraiClient
from fetch.filters import CatalogueFilters
from fetch.profiles import CatalogueProfile
from fetch.routes import TenraiAnimeRoute


class AlternateCatalogueRoute:
    name = 'tenrai-discovery'

    def catalogue_url(self, base_url: str) -> str:
        return f'{base_url.rstrip("/")}/discovery'

    def full_entry_url(self, base_url: str, anime_id: int) -> str:
        return f'{base_url.rstrip("/")}/discovery/{anime_id}'


class _FakeResponse:
    status_code = 200
    content = msgspec.json.encode({'data': [], 'pagination': {'last_visible_page': 1}})
    headers: ClassVar[dict[str, str]] = {}


class _FakeSession:
    def __init__(self) -> None:
        self.urls: list[str] = []

    def get(self, url: str, **_kwargs: object) -> _FakeResponse:
        self.urls.append(url)
        return _FakeResponse()

    def close(self) -> None:
        pass


def test_tenrai_route_builds_urls_from_the_configured_base() -> None:
    route = TenraiAnimeRoute()

    assert route.catalogue_url('https://api.example/') == 'https://api.example/anime'
    assert route.full_entry_url('https://api.example/', 42) == 'https://api.example/anime/42/full'


def test_tenrai_route_rejects_invalid_entry_ids() -> None:
    with pytest.raises(ValueError, match='positive'):
        TenraiAnimeRoute().full_entry_url('https://api.example', 0)


def test_alternate_route_has_independent_endpoints() -> None:
    route = AlternateCatalogueRoute()

    assert route.catalogue_url('https://api.example') == 'https://api.example/discovery'
    assert route.full_entry_url('https://api.example', 42) == 'https://api.example/discovery/42'


def test_client_uses_a_profile_route_without_changing_transport_logic(monkeypatch: pytest.MonkeyPatch) -> None:
    session = _FakeSession()
    monkeypatch.setattr('fetch.transport.niquests.Session', lambda: session)
    profile = CatalogueProfile('discovery', CatalogueFilters.all_anime(), route=AlternateCatalogueRoute())
    client = TenraiClient(Settings(requests_per_second=100), profile=profile)

    response = client.catalogue_page(1)
    client.close()

    assert response.data == []
    assert session.urls == ['https://api.tenrai.org/v1/discovery']


def test_checkpoint_cannot_resume_with_a_different_route(tmp_path: Path) -> None:
    checkpoint = FetchCheckpoint(
        mode='catalogue',
        route='tenrai-anime',
        filter_signature=CatalogueFilters.sfw_catalogue().signature(),
        output_path=str((tmp_path / 'entries.raw.json').resolve()),
    )

    with pytest.raises(ValueError, match='route'):
        _validate_checkpoint(
            checkpoint,
            CatalogueFilters.sfw_catalogue(),
            tmp_path / 'entries.json',
            'tenrai-discovery',
            '-',
        )


def test_catalogue_profile_owns_filters_acceptance_and_route() -> None:
    profile = CatalogueProfile.r_plus(limit=25)

    assert profile.name == 'r-plus'
    assert profile.filters.limit == 25
    assert profile.acceptance_policy.excluded_genre_ids == frozenset({9, 12, 49})
    assert profile.route.name == 'tenrai-anime'
