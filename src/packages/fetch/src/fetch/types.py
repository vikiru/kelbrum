"""Canonical values for Tenrai response enums owned by fetch."""

from enum import StrEnum


class MediaType(StrEnum):
    """Supported Tenrai media types used by catalogue policies."""

    TV = 'TV'
    TV_SPECIAL = 'TV_SPECIAL'
    MOVIE = 'MOVIE'
    OVA = 'OVA'
    ONA = 'ONA'
    SPECIAL = 'SPECIAL'
    MUSIC = 'MUSIC'
    CM = 'CM'
    PV = 'PV'
    UNKNOWN = 'UNKNOWN'


class AiringStatus(StrEnum):
    """Known MAL airing-status values."""

    FINISHED_AIRING = 'Finished Airing'
    CURRENTLY_AIRING = 'Currently Airing'
    NOT_YET_AIRED = 'Not yet aired'


def normalize_media_type(value: str | None) -> MediaType | None:
    """Normalize Tenrai response media types to stable uppercase values."""
    if value is None:
        return None
    normalized = value.strip().upper().replace('-', '_').replace(' ', '_')
    try:
        return MediaType(normalized)
    except ValueError:
        return MediaType.UNKNOWN if normalized else None


def normalize_airing_status(value: str | None) -> AiringStatus | None:
    """Normalize a Tenrai airing status to a known enum value."""
    if value is None:
        return None
    normalized = value.strip().casefold()
    return next((status for status in AiringStatus if status.casefold() == normalized), None)
