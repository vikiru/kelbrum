"""Canonical rating normalization for compatibility and eligibility rules."""

from enum import StrEnum

import msgspec


class RatingClass(StrEnum):
    UNKNOWN = 'UNKNOWN'
    G = 'G'
    PG = 'PG'
    PG_13 = 'PG_13'
    R = 'R'
    R_PLUS = 'R_PLUS'


GENERAL_AUDIENCE_RATINGS = frozenset({RatingClass.G, RatingClass.PG, RatingClass.PG_13})
MATURE_RATINGS = frozenset({RatingClass.R, RatingClass.R_PLUS})

DISPLAY_RATINGS = {
    RatingClass.UNKNOWN: 'Unknown',
    RatingClass.G: 'G',
    RatingClass.PG: 'PG',
    RatingClass.PG_13: 'PG-13',
    RatingClass.R: 'R',
    RatingClass.R_PLUS: 'R+',
}


class RatingDecision(msgspec.Struct, frozen=True):
    allowed: bool
    reason: str
    parent_rating: str
    candidate_rating: str


class RatingPolicy:
    """Apply asymmetric maturity rules without changing stored catalogue ratings."""

    def evaluate(self, parent_rating: str | None, candidate_rating: str | None) -> RatingDecision:
        parent = normalize_rating(parent_rating)
        candidate = normalize_rating(candidate_rating)
        if RatingClass.UNKNOWN in (parent, candidate):
            return RatingDecision(False, 'unknown_rating_fail_closed', parent.value, candidate.value)
        allowed = _rating_allowed(parent, candidate)
        return RatingDecision(allowed, 'retained' if allowed else 'rating_excluded', parent.value, candidate.value)


def _rating_allowed(parent: RatingClass, candidate: RatingClass) -> bool:
    if parent in GENERAL_AUDIENCE_RATINGS:
        return candidate in GENERAL_AUDIENCE_RATINGS
    if parent in MATURE_RATINGS:
        return candidate in GENERAL_AUDIENCE_RATINGS | MATURE_RATINGS
    return False


def normalize_rating(value: str | None) -> RatingClass:
    normalized = (value or '').strip().upper()
    if not normalized:
        return RatingClass.UNKNOWN
    if normalized.startswith('RX') or 'R+' in normalized:
        return RatingClass.R_PLUS
    if normalized.startswith('R'):
        return RatingClass.R
    if 'PG-13' in normalized or 'PG 13' in normalized:
        return RatingClass.PG_13
    if normalized.startswith('PG'):
        return RatingClass.PG
    if normalized.startswith('G'):
        return RatingClass.G
    return RatingClass.UNKNOWN


def display_rating(value: str | None) -> str:
    """Return the stable human-facing rating label."""
    return DISPLAY_RATINGS[normalize_rating(value)]
