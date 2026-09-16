"""Canonical rating normalization for compatibility and eligibility rules."""

import re
from enum import StrEnum


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

_RATING_PATTERNS: tuple[tuple[re.Pattern[str], RatingClass], ...] = (
    (re.compile(r'^RX'), RatingClass.R_X),
    (re.compile(r'R\+'), RatingClass.R_PLUS),
    (re.compile(r'^R'), RatingClass.R),
    (re.compile(r'PG(?:-13| 13)'), RatingClass.PG_13),
    (re.compile(r'^PG'), RatingClass.PG),
    (re.compile(r'^G'), RatingClass.G),
)


def normalize_rating(value: str | None) -> RatingClass:
    """Map an API rating string to the normalized rating class used by policy."""
    normalized = (value or '').strip().upper()
    for pattern, rating_class in _RATING_PATTERNS:
        if pattern.search(normalized):
            return rating_class
    return RatingClass.UNKNOWN


def display_rating(value: str | None) -> str:
    """Return the stable human-facing rating label."""
    return DISPLAY_RATINGS[normalize_rating(value)]
