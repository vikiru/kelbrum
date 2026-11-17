"""Single source of truth for tonal, setting, and demographic conflicts across pipeline stages."""

from enum import Enum
from typing import Final

import msgspec

from anime_catalogue.demographics import (
    ContentSeverityLevel,
    Demographic,
    is_fatal_content_severity_mismatch,
)
from anime_catalogue.taxonomy import SETTING_BACKDROP_THEMES as SETTING_BACKDROP_THEMES
from anime_catalogue.taxonomy import Genre, Theme
from anime_catalogue.tone_space import (
    is_fatal_tonal_contradiction,
)
from features.tags import Tag


class ConflictSeverity(float, Enum):
    HARD_EXCLUDE = 0.0
    SEVERE_DAMPEN = 0.15
    MODERATE_DAMPEN = 0.50
    LIGHT_DAMPEN = 0.70
    NEUTRAL = 1.0


class ConflictProfile(msgspec.Struct, frozen=True):
    is_pure_serious: bool
    is_gag_comedy: bool
    is_iyashikei: bool
    is_sparse: bool
    backdrop_only_themes: frozenset[Theme]


ALL_GENRES: Final[frozenset[Genre]] = frozenset(Genre)

ALL_THEMES: Final[frozenset[Theme]] = frozenset(Theme)

ALL_DEMOGRAPHICS: Final[frozenset[str]] = frozenset(
    {Demographic.JOSEI, Demographic.KIDS, Demographic.SEINEN, Demographic.SHOUJO, Demographic.SHOUNEN}
)

SERIOUS_GENRES: Final[frozenset[Genre]] = frozenset({Genre.SUSPENSE, Genre.HORROR})
SERIOUS_THEMES: Final[frozenset[Theme]] = frozenset({Theme.PSYCHOLOGICAL, Theme.GORE})

GAG_PARODY_GENRES: Final[frozenset[Genre]] = frozenset({Genre.COMEDY})
GAG_PARODY_THEMES: Final[frozenset[Theme]] = frozenset({Theme.PARODY, Theme.GAG_HUMOR})
GAG_PARODY_TAGS: Final[frozenset[str]] = frozenset({Tag.SATIRE, Tag.ABSURDIST})

IYASHIKEI_THEMES: Final[frozenset[Theme]] = frozenset({Theme.IYASHIKEI, Theme.CGDCT, Theme.CHILDCARE})
IYASHIKEI_TAGS: Final[frozenset[str]] = frozenset({Tag.HEARTWARMING, Tag.SLOW_LIFE, Tag.COMMUNITY_LIFE})

BLEAK_NOIR_TAGS: Final[frozenset[str]] = frozenset({Tag.BLEAK, Tag.NOIR, Tag.MELANCHOLIC, Tag.DYSTOPIAN, Tag.TRAGEDY})
DARK_THREAT_TAGS: Final[frozenset[str]] = frozenset(
    {
        Tag.DARK,
        Tag.BLEAK,
        Tag.TRAGEDY,
        Tag.SERIAL_KILLER,
        Tag.ACTS_OF_TERROR,
        Tag.BODY_HORROR,
        Tag.ABUSIVE_TREATMENT,
        Tag.PREDATION,
        Tag.DYSTOPIAN,
    }
)


def is_pure_serious_anchor(
    genres: frozenset[Genre],
    themes: frozenset[Theme],
    tags: frozenset[str] = frozenset(),
) -> bool:
    has_serious = bool((genres & SERIOUS_GENRES) or (themes & SERIOUS_THEMES) or (tags & DARK_THREAT_TAGS))
    has_lighthearted = bool(
        (genres & GAG_PARODY_GENRES)
        or (themes & (GAG_PARODY_THEMES | IYASHIKEI_THEMES))
        or (tags & (GAG_PARODY_TAGS | IYASHIKEI_TAGS))
    )
    return has_serious and not has_lighthearted


def is_pure_lighthearted_candidate(
    genres: frozenset[Genre],
    themes: frozenset[Theme],
    tags: frozenset[str] = frozenset(),
) -> bool:
    has_lighthearted = bool(
        (genres & GAG_PARODY_GENRES)
        or (themes & (GAG_PARODY_THEMES | IYASHIKEI_THEMES))
        or (tags & (GAG_PARODY_TAGS | IYASHIKEI_TAGS))
    )
    has_serious_or_drama = bool(
        (genres & (SERIOUS_GENRES | frozenset({Genre.DRAMA}))) or (themes & SERIOUS_THEMES) or (tags & DARK_THREAT_TAGS)
    )
    return has_lighthearted and not has_serious_or_drama


def is_hard_retrieval_contradiction(
    *,
    source_genres: frozenset[Genre],
    source_themes: frozenset[Theme],
    source_tags: frozenset[str],
    source_tone: float,
    source_content_level: ContentSeverityLevel,
    candidate_genres: frozenset[Genre],
    candidate_themes: frozenset[Theme],
    candidate_tags: frozenset[str] = frozenset(),
    candidate_tone: float,
    candidate_content_level: ContentSeverityLevel,
) -> bool:
    """Stage 1 Hard Candidate Qualification Gate.

    Pure, deterministic check dropping fatal contradictions before scoring budget allocation:
      1. Cohort Isolation: BL <-> GL mutual exclusion, Non-BL <-> BL.
      2. Relationship Topology: Grounded non-harem romance strictly excludes Theme.HAREM.
      3. Tonal Polar Extremes: Distance between tone coordinates >= FATAL_TONAL_DISTANCE_THRESHOLD.
      4. Content Severity Ceiling: Level 0 (G / Universal) <-> Level 3/4 (R / R+) with Gore/Threat.
    """
    is_source_bl = Genre.BOYS_LOVE in source_genres
    is_source_gl = Genre.GIRLS_LOVE in source_genres
    is_candidate_bl = Genre.BOYS_LOVE in candidate_genres
    is_candidate_gl = Genre.GIRLS_LOVE in candidate_genres

    # 1. Cohort Isolation
    if is_source_bl and is_candidate_gl:
        return True
    if is_source_gl and is_candidate_bl:
        return True
    if not is_source_bl and is_candidate_bl:
        return True

    # 2. Relationship Topology
    is_source_grounded_romance = Genre.ROMANCE in source_genres and not (
        source_themes & {Theme.HAREM, Theme.REVERSE_HAREM}
    )
    if is_source_grounded_romance and (candidate_themes & {Theme.HAREM, Theme.REVERSE_HAREM}):
        return True

    # 3. Tonal Polar Extremes
    if is_fatal_tonal_contradiction(source_tone, candidate_tone):
        return True

    # 4. Content Severity Ceiling
    is_source_pure_dark = bool(
        Theme.GORE in source_themes
        or Tag.BODY_HORROR in source_tags
        or (Genre.HORROR in source_genres and (Tag.BLEAK in source_tags or Tag.SERIAL_KILLER in source_tags))
    )
    is_candidate_pure_dark = bool(
        Theme.GORE in candidate_themes
        or Tag.BODY_HORROR in candidate_tags
        or (Genre.HORROR in candidate_genres and (Tag.BLEAK in candidate_tags or Tag.SERIAL_KILLER in candidate_tags))
    )
    if source_content_level == ContentSeverityLevel.LEVEL_0_UNIVERSAL and is_candidate_pure_dark:
        return True
    return is_fatal_content_severity_mismatch(
        source_content_level,
        candidate_content_level,
        anchor_is_pure_dark=is_source_pure_dark,
    )
