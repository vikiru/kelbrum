"""Convert accepted Tenrai entries into canonical records and Parquet."""

import re

import msgspec

from fetch.contracts import Taxonomy, TenraiAnimeEntry
from fetch.types import normalize_media_type
from processing.contracts import CanonicalAnime
from processing.labels import normalize_label
from processing.synopsis import feature_synopsis

_HOURS = re.compile(r'(?P<hours>\d+)\s*hr(?:s)?', re.IGNORECASE)
_MINUTES = re.compile(r'(?P<minutes>\d+)\s*min(?:s)?', re.IGNORECASE)
_SYNOPSIS_ATTRIBUTION = re.compile(
    r'\s*(?:\((?:source|written by|translated by):[^)]*\)|\[(?:source|written by|translated by):[^]]*\])\s*$',
    re.IGNORECASE,
)
_SYNOPSIS_SOURCE = re.compile(r'\s*\(?source:\s*[^)\]]+\)?\s*$', re.IGNORECASE)


def clean_synopsis(value: str | None) -> str | None:
    """Normalize synopsis text and remove trailing attribution boilerplate."""
    if not value:
        return None
    cleaned = ' '.join(value.split())
    cleaned = _SYNOPSIS_ATTRIBUTION.sub('', cleaned).strip()
    cleaned = _SYNOPSIS_SOURCE.sub('', cleaned).strip()
    return feature_synopsis(cleaned) if cleaned else None


def duration_to_minutes(value: str | None) -> int | None:
    """Convert Tenrai duration text such as ``1 hr 25 min`` to minutes."""
    if not value or value.strip().lower() in {'unknown', 'n/a', 'not available'}:
        return None
    hours = _HOURS.search(value)
    minutes = _MINUTES.search(value)
    total = (int(hours.group('hours')) * 60 if hours else 0) + (int(minutes.group('minutes')) if minutes else 0)
    return total or None


def canonicalize(entry: TenraiAnimeEntry) -> CanonicalAnime:
    """Apply deterministic whitespace and missing-value cleaning."""
    synopsis = clean_synopsis(entry.synopsis)
    return CanonicalAnime(
        mal_id=entry.mal_id,
        url=entry.url,
        title=entry.title.strip(),
        title_english=entry.title_english.strip() if entry.title_english else None,
        title_japanese=entry.title_japanese.strip() if entry.title_japanese else None,
        title_synonyms=tuple(value.strip() for value in entry.title_synonyms if value.strip()),
        anime_type=normalize_media_type(entry.type),
        source=entry.source,
        rating=entry.rating,
        season=entry.season,
        episodes=entry.episodes,
        duration_minutes=duration_to_minutes(entry.duration),
        year=entry.year,
        status=entry.status,
        score=entry.score,
        synopsis=synopsis,
        synopsis_features=feature_synopsis(synopsis),
        background=entry.background,
        moreinfo=entry.moreinfo,
        images=entry.images,
        trailer=entry.trailer,
        external=tuple(entry.external),
        studios=tuple(entry.studios),
        producers=tuple(entry.producers),
        licensors=tuple(entry.licensors),
        genres=tuple(_normalize_taxonomy(item) for item in entry.genres),
        themes=tuple(_normalize_taxonomy(item) for item in entry.themes),
        demographics=tuple(entry.demographics),
        relations=tuple(entry.relations),
    )


def _normalize_taxonomy(item: Taxonomy) -> Taxonomy:
    return msgspec.structs.replace(item, name=normalize_label(item.name))
