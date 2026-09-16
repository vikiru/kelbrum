"""Configurable age-rating compatibility for recommendation candidates."""

import re
from enum import StrEnum

import msgspec


class RatingClass(StrEnum):
    UNKNOWN = 'UNKNOWN'
    G = 'G'
    PG = 'PG'
    PG_13 = 'PG_13'
    R = 'R'
    R_PLUS = 'R_PLUS'
    R_X = 'R_X'


class RatingDecision(msgspec.Struct, frozen=True):
    allowed: bool
    reason: str
    parent_rating: str
    candidate_rating: str


class RatingPolicy:
    """Apply asymmetric maturity rules without coupling recommendation to processing."""

    name = 'rating-compatibility-v3'
    identity = name

    def evaluate(self, parent_rating: str | None, candidate_rating: str | None) -> RatingDecision:
        parent = _normalize_rating(parent_rating)
        candidate = _normalize_rating(candidate_rating)
        if RatingClass.UNKNOWN in (parent, candidate):
            return RatingDecision(False, 'unknown_rating_fail_closed', parent.value, candidate.value)
        allowed = candidate in GENERAL_AUDIENCE_RATINGS or parent in MATURE_RATINGS
        return RatingDecision(allowed, 'retained' if allowed else 'rating_excluded', parent.value, candidate.value)


GENERAL_AUDIENCE_RATINGS = frozenset({RatingClass.G, RatingClass.PG, RatingClass.PG_13})
MATURE_RATINGS = frozenset({RatingClass.R, RatingClass.R_PLUS, RatingClass.R_X})


def _normalize_rating(value: str | None) -> RatingClass:
    normalized = (value or '').strip().upper()
    for pattern, rating_class in _RATING_PATTERNS:
        if pattern.search(normalized):
            return rating_class
    return RatingClass.UNKNOWN


_RATING_PATTERNS: tuple[tuple[re.Pattern[str], RatingClass], ...] = (
    (re.compile(r'^RX'), RatingClass.R_X),
    (re.compile(r'R\+'), RatingClass.R_PLUS),
    (re.compile(r'^R'), RatingClass.R),
    (re.compile(r'PG(?:-13| 13)'), RatingClass.PG_13),
    (re.compile(r'^PG'), RatingClass.PG),
    (re.compile(r'^G'), RatingClass.G),
)
