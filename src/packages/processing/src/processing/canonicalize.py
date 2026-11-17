"""Convert accepted Tenrai entries into canonical records and Parquet."""

import re

import msgspec

from anime_catalogue.taxonomy import parse_genre, parse_theme
from fetch.contracts import Taxonomy, TenraiAnimeEntry
from fetch.types import normalize_media_type
from normalization.metadata import collection_state, normalize_demographic, scalar_state
from normalization.ratings import rating_metadata_state
from processing.contracts import CanonicalAnime
from processing.synopsis import ATTRIBUTION_PATTERN, SOURCE_CITATION_PATTERN, feature_synopsis

_HOURS = re.compile(r'(?P<hours>\d+)\s*hr(?:s)?', re.IGNORECASE)
_MINUTES = re.compile(r'(?P<minutes>\d+)\s*min(?:s)?', re.IGNORECASE)
_SECONDS = re.compile(r'(?P<seconds>\d+)\s*sec(?:s)?', re.IGNORECASE)
_SYNOPSIS_ATTRIBUTION = re.compile(ATTRIBUTION_PATTERN)
_SYNOPSIS_SOURCE = re.compile(SOURCE_CITATION_PATTERN)


def clean_synopsis(value: str | None) -> str | None:
    """Normalize synopsis text and remove trailing attribution boilerplate."""
    if not value:
        return None
    cleaned = ' '.join(value.split())
    cleaned = _SYNOPSIS_ATTRIBUTION.sub('', cleaned).strip()
    cleaned = _SYNOPSIS_SOURCE.sub('', cleaned).strip()
    return feature_synopsis(cleaned) if cleaned else None


def duration_to_minutes(value: str | None) -> int | None:
    """Convert Tenrai duration text to whole minutes, flooring any seconds."""
    if not value or value.strip().lower() in {'unknown', 'n/a', 'not available'}:
        return None
    hours = _HOURS.search(value)
    minutes = _MINUTES.search(value)
    seconds = _SECONDS.search(value)
    if hours is None and minutes is None and seconds is None:
        return None
    return (
        (int(hours.group('hours')) * 60 if hours else 0)
        + (int(minutes.group('minutes')) if minutes else 0)
        + (int(seconds.group('seconds')) // 60 if seconds else 0)
    )


def canonicalize(
    entry: TenraiAnimeEntry,
    *,
    parent_synopsis_fallback: str | None = None,
) -> CanonicalAnime:
    """Apply deterministic whitespace and missing-value cleaning with parent synopsis fallback for stubs."""
    synopsis = clean_synopsis(entry.synopsis)
    feat_synopsis = feature_synopsis(synopsis)

    # Short Sequel/Franchise Stub Enrichment:
    # If the feature synopsis is very short (< 90 chars) and a substantive parent/prequel synopsis exists,
    # append the parent series narrative premise to synopsis_features so text and embedding models receive
    # complete semantic tokens. The user-facing display synopsis remains clean and unmutated.
    if parent_synopsis_fallback and (feat_synopsis is None or len(feat_synopsis) < 90):
        cleaned_parent = clean_synopsis(parent_synopsis_fallback)
        feat_parent = feature_synopsis(cleaned_parent)
        if feat_parent and len(feat_parent) >= 90:
            prefix = feat_synopsis + ' ' if feat_synopsis else ''
            feat_synopsis = f'{prefix}[Series Premise: {feat_parent}]'

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
        synopsis_features=feat_synopsis,
        background=entry.background,
        moreinfo=entry.moreinfo,
        images=entry.images,
        trailer=entry.trailer,
        external=tuple(entry.external),
        studios=tuple(entry.studios),
        producers=tuple(entry.producers),
        licensors=tuple(entry.licensors),
        genres=tuple(msgspec.structs.replace(item, name=parse_genre(item.name).value) for item in entry.genres or ()),
        themes=tuple(msgspec.structs.replace(item, name=parse_theme(item.name).value) for item in entry.themes or ()),
        demographics=tuple(_normalize_demographic(item) for item in entry.demographics or ()),
        relations=tuple(entry.relations),
        synopsis_state=scalar_state(entry.synopsis),
        genres_state=collection_state(entry.genres),
        themes_state=collection_state(entry.themes),
        demographics_state=collection_state(entry.demographics),
        type_state=scalar_state(entry.type),
        rating_state=rating_metadata_state(entry.rating),
    )


def _normalize_demographic(item: Taxonomy) -> Taxonomy:
    return msgspec.structs.replace(item, name=normalize_demographic(item.name))
