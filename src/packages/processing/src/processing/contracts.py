"""Processing-owned canonical catalogue contracts."""

import msgspec

from fetch.contracts import (
    AnimeRelation,
    ExternalLink,
    Images,
    NamedResource,
    Taxonomy,
    Trailer,
)


class CanonicalAnime(msgspec.Struct, frozen=True):
    """Stable, cleaned anime record produced by processing."""

    mal_id: int
    url: str | None
    title: str
    title_english: str | None
    title_japanese: str | None
    title_synonyms: tuple[str, ...]
    anime_type: str | None
    source: str | None
    rating: str | None
    season: str | None
    episodes: int | None
    duration_minutes: int | None
    year: int | None
    status: str | None
    score: float | None
    synopsis: str | None
    synopsis_features: str | None
    background: str | None
    moreinfo: str | None
    images: Images | None
    trailer: Trailer | None
    external: tuple[ExternalLink, ...]
    studios: tuple[NamedResource, ...]
    producers: tuple[NamedResource, ...]
    licensors: tuple[NamedResource, ...]
    genres: tuple[Taxonomy, ...]
    themes: tuple[Taxonomy, ...]
    demographics: tuple[Taxonomy, ...]
    relations: tuple[AnimeRelation, ...]


class NumericRange(msgspec.Struct, frozen=True):
    minimum: float | None
    maximum: float | None


class FilterMetadata(msgspec.Struct, frozen=True):
    """Typed search-filter data aligned to the canonical catalogue order."""

    anime_ids: tuple[int, ...]
    posting_lists: dict[str, dict[str, tuple[int, ...]]]
    numeric_arrays: dict[str, tuple[int | float | None, ...]]
    numeric_ranges: dict[str, NumericRange]


class ProcessingArtifactManifest(msgspec.Struct, frozen=True):
    schema_version: str
    fetched_date: str
    anime_count: int
    artifacts: tuple[tuple[str, str], ...]
