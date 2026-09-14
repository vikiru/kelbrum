"""Deterministic cleanup rules for non-narrative ONA entries."""

import re

import msgspec

from models.tenrai import TenraiAnimeEntry
from models.tenrai_types import normalize_media_type
from processing.canonicalize import duration_to_minutes

_PROMOTIONAL_TITLE = re.compile(
    r'\b(?:pv|trailer|teaser|promotional|promo|commercial|cm|recap|digest|summary|preview|prologue|specials?|extra|install)\b|\bepisode\s+0\b',
    re.IGNORECASE,
)


class OnaCleanupAudit(msgspec.Struct, frozen=True):
    removed_ids: tuple[int, ...]
    unknown_duration_ids: tuple[int, ...]
    missing_metadata_ids: tuple[int, ...]
    promotional_ids: tuple[int, ...]
    short_form_ids: tuple[int, ...]


def cleanup_ona(
    entries: list[TenraiAnimeEntry], *, min_duration_minutes: int = 20
) -> tuple[list[TenraiAnimeEntry], OnaCleanupAudit]:
    """Remove obvious promotional ONA and known entries shorter than the duration threshold."""
    if min_duration_minutes < 1:
        raise ValueError('min_duration_minutes must be positive')

    cleaned: list[TenraiAnimeEntry] = []
    removed_ids: list[int] = []
    unknown_duration_ids: list[int] = []
    missing_metadata_ids: list[int] = []
    promotional_ids: list[int] = []
    short_form_ids: list[int] = []
    for entry in entries:
        if normalize_media_type(entry.type) != 'ONA':
            cleaned.append(entry)
            continue

        title = f'{entry.title} {entry.title_english or ""}'
        duration_minutes = duration_to_minutes(entry.duration)
        is_too_short = _is_short_form(entry, duration_minutes, min_duration_minutes)
        has_metadata = bool(entry.synopsis or entry.genres or entry.themes)
        missing_metadata = not has_metadata
        is_promotional = bool(_PROMOTIONAL_TITLE.search(title))
        if is_promotional or is_too_short or missing_metadata:
            removed_ids.append(entry.mal_id)
            if missing_metadata:
                missing_metadata_ids.append(entry.mal_id)
            if is_promotional:
                promotional_ids.append(entry.mal_id)
            if is_too_short:
                short_form_ids.append(entry.mal_id)
            continue
        if duration_minutes is None:
            unknown_duration_ids.append(entry.mal_id)
        cleaned.append(entry)

    return cleaned, OnaCleanupAudit(
        removed_ids=tuple(sorted(removed_ids)),
        unknown_duration_ids=tuple(sorted(unknown_duration_ids)),
        missing_metadata_ids=tuple(sorted(missing_metadata_ids)),
        promotional_ids=tuple(sorted(promotional_ids)),
        short_form_ids=tuple(sorted(short_form_ids)),
    )


def _is_short_form(entry: TenraiAnimeEntry, duration_minutes: int | None, threshold: int) -> bool:
    """Compare total runtime when the source duration is expressed per episode."""
    if duration_minutes is None:
        return False
    if entry.episodes is not None and 'per ep' in (entry.duration or '').casefold():
        return duration_minutes * entry.episodes <= threshold
    return duration_minutes <= threshold
