"""Audience demographic compatibility graph and age rating content levels.

Replaces string comparisons and boolean flags with an explicit compatibility matrix
and ordinal content levels (0 = G to 4 = R+).
"""

from enum import IntEnum, StrEnum
from functools import lru_cache
from typing import Final

from normalization.metadata import DEMOGRAPHIC_LABELS
from normalization.ratings import RatingClass, normalize_rating


class Demographic(StrEnum):
    KIDS = 'Kids'
    SHOUNEN = 'Shounen'
    SHOUJO = 'Shoujo'
    SEINEN = 'Seinen'
    JOSEI = 'Josei'
    UNKNOWN = 'Unknown'


class ContentSeverityLevel(IntEnum):
    """Ordinal content ceiling."""

    LEVEL_0_UNIVERSAL = 0  # G, all ages
    LEVEL_1_GUIDANCE = 1  # PG
    LEVEL_2_TEEN = 2  # PG-13
    LEVEL_3_MATURE = 3  # R-17+ (Intense Violence / Horror)
    LEVEL_4_EXPLICIT = 4  # R+ (Mild Nudity / Explicit)


RATING_CLASS_TO_LEVEL: Final[dict[RatingClass, ContentSeverityLevel]] = {
    RatingClass.G: ContentSeverityLevel.LEVEL_0_UNIVERSAL,
    RatingClass.PG: ContentSeverityLevel.LEVEL_1_GUIDANCE,
    RatingClass.PG_13: ContentSeverityLevel.LEVEL_2_TEEN,
    RatingClass.R: ContentSeverityLevel.LEVEL_3_MATURE,
    RatingClass.R_PLUS: ContentSeverityLevel.LEVEL_4_EXPLICIT,
    RatingClass.R_X: ContentSeverityLevel.LEVEL_4_EXPLICIT,
}

NEUTRAL_DEMOGRAPHIC_AFFINITY: Final[float] = 1.0

# Cross-demographic audience resonance matrix S(anchor, candidate) in [0.0, 1.0]
DEMOGRAPHIC_AFFINITY: Final[dict[Demographic, dict[Demographic, float]]] = {
    Demographic.SHOUJO: {
        Demographic.SHOUJO: 1.0,
        Demographic.JOSEI: 0.85,
        Demographic.KIDS: 0.50,
        Demographic.SHOUNEN: 0.40,
        Demographic.SEINEN: 0.25,
    },
    Demographic.JOSEI: {
        Demographic.JOSEI: 1.0,
        Demographic.SHOUJO: 0.85,
        Demographic.SEINEN: 0.65,
        Demographic.SHOUNEN: 0.25,
        Demographic.KIDS: 0.10,
    },
    Demographic.SHOUNEN: {
        Demographic.SHOUNEN: 1.0,
        Demographic.SEINEN: 0.80,
        Demographic.KIDS: 0.50,
        Demographic.SHOUJO: 0.40,
        Demographic.JOSEI: 0.25,
    },
    Demographic.SEINEN: {
        Demographic.SEINEN: 1.0,
        Demographic.SHOUNEN: 0.80,
        Demographic.JOSEI: 0.65,
        Demographic.SHOUJO: 0.25,
        Demographic.KIDS: 0.10,
    },
    Demographic.KIDS: {
        Demographic.KIDS: 1.0,
        Demographic.SHOUNEN: 0.50,
        Demographic.SHOUJO: 0.50,
        Demographic.SEINEN: 0.10,
        Demographic.JOSEI: 0.10,
    },
}


@lru_cache(maxsize=64)
def parse_demographic(value: str) -> Demographic:
    canonical = DEMOGRAPHIC_LABELS.get(value.strip().casefold())
    return Demographic(canonical) if canonical is not None else Demographic.UNKNOWN


def get_content_severity_level(rating_str: str) -> ContentSeverityLevel:
    return RATING_CLASS_TO_LEVEL.get(normalize_rating(rating_str), ContentSeverityLevel.LEVEL_2_TEEN)


def is_fatal_content_severity_mismatch(
    anchor_level: ContentSeverityLevel,
    candidate_level: ContentSeverityLevel,
    anchor_is_pure_dark: bool = False,
) -> bool:
    """Return True if candidate content level fatally contradicts anchor at retrieval.

    Rule:
      - Level 0 (G / Universal) anchor strictly excludes Level 3 & Level 4 (R / R+).
      - Dark/threat anchor (Level 3+) strictly excludes Level 0 (G / Universal).
      - Between Level 1 (PG), Level 2 (PG-13), and Level 3 (R-17+): NEVER fatally exclude;
        allow tone and narrative similarity to govern ranking.
    """
    if (
        anchor_level == ContentSeverityLevel.LEVEL_0_UNIVERSAL
        and candidate_level >= ContentSeverityLevel.LEVEL_3_MATURE
    ):
        return True
    return bool(anchor_is_pure_dark and candidate_level == ContentSeverityLevel.LEVEL_0_UNIVERSAL)


def compute_demographic_affinity_multiplier(anchor_demographic: str, candidate_demographic: str) -> float:
    """Return continuous demographic affinity multiplier in [0.1, 1.0]."""
    anchor = parse_demographic(anchor_demographic)
    candidate = parse_demographic(candidate_demographic)
    if anchor is Demographic.UNKNOWN or candidate is Demographic.UNKNOWN:
        return NEUTRAL_DEMOGRAPHIC_AFFINITY
    return DEMOGRAPHIC_AFFINITY[anchor].get(candidate, NEUTRAL_DEMOGRAPHIC_AFFINITY)
