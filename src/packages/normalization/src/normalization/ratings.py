"""Canonical rating values and parsing shared across pipeline stages."""

from enum import StrEnum
from functools import lru_cache

from normalization.metadata import MetadataState


class RatingClass(StrEnum):
    UNKNOWN = 'UNKNOWN'
    G = 'G'
    PG = 'PG'
    PG_13 = 'PG_13'
    R = 'R'
    R_PLUS = 'R_PLUS'
    R_X = 'R_X'


DISPLAY_RATINGS = {
    RatingClass.UNKNOWN: 'Unknown',
    RatingClass.G: 'G',
    RatingClass.PG: 'PG',
    RatingClass.PG_13: 'PG-13',
    RatingClass.R: 'R',
    RatingClass.R_PLUS: 'R+',
    RatingClass.R_X: 'Rx',
}

_SOURCE_RATINGS = {
    'G - ALL AGES': RatingClass.G,
    'PG - CHILDREN': RatingClass.PG,
    'PG-13': RatingClass.PG_13,
    'PG-13 - TEENS 13 OR OLDER': RatingClass.PG_13,
    'R-17+': RatingClass.R,
    'R - 17+ (VIOLENCE & PROFANITY)': RatingClass.R,
    'R+': RatingClass.R_PLUS,
    'R+ - MILD NUDITY': RatingClass.R_PLUS,
    'RX': RatingClass.R_X,
    'RX - HENTAI': RatingClass.R_X,
}


@lru_cache(maxsize=64)
def normalize_rating(value: str | None) -> RatingClass:
    """Normalize display/API strings and canonical enum values consistently."""
    normalized = ' '.join((value or '').split()).upper()
    try:
        return RatingClass(normalized)
    except ValueError:
        return _SOURCE_RATINGS.get(normalized, RatingClass.UNKNOWN)


def rating_metadata_state(value: str | None) -> MetadataState:
    """Distinguish an unknown age rating from an observed blank value."""
    if value is None:
        return MetadataState.UNKNOWN
    if not value.strip():
        return MetadataState.OBSERVED_ABSENT
    if normalize_rating(value) is RatingClass.UNKNOWN:
        return MetadataState.UNKNOWN
    return MetadataState.OBSERVED


def display_rating(value: str | None) -> str:
    """Return the stable human-facing rating label."""
    return DISPLAY_RATINGS[normalize_rating(value)]
