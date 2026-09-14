"""Explicit catalogue eligibility rules and audit reporting."""

import re
from collections.abc import Collection
from enum import StrEnum
from urllib.parse import urlparse

import msgspec

from models.tenrai import TenraiAnimeEntry
from models.tenrai_types import AiringStatus, normalize_airing_status, normalize_media_type
from processing.canonicalize import duration_to_minutes
from processing.constants import (
    DEFAULT_ALLOWED_TYPES,
    DEFAULT_EXCLUDED_GENRE_IDS,
    DEFAULT_MAX_YEAR,
    DEFAULT_MIN_MOVIE_DURATION_MINUTES,
    PLACEHOLDER_IMAGE_URL,
)


class EligibilityPolicy(msgspec.Struct, frozen=True):
    """Configurable rules defining membership in the production catalogue."""

    max_year: int = DEFAULT_MAX_YEAR
    require_primary_image: bool = True
    require_trailer: bool = False
    allowed_types: frozenset[str] = DEFAULT_ALLOWED_TYPES
    excluded_genre_ids: frozenset[int] = DEFAULT_EXCLUDED_GENRE_IDS
    min_movie_duration_minutes: int = DEFAULT_MIN_MOVIE_DURATION_MINUTES
    bypass_catalogue_filters: bool = False
    require_semantic_evidence: bool = True


class ExclusionReason(StrEnum):
    """Stable reason codes emitted by catalogue eligibility checks."""

    TYPE_NOT_ALLOWED = 'type_not_allowed'
    EXCLUDED_GENRE = 'excluded_genre'
    MISSING_SEMANTIC_EVIDENCE = 'missing_semantic_evidence'
    YEAR_AFTER_CUTOFF = 'year_after_cutoff'
    NOT_YET_AIRED = 'not_yet_aired'
    SHORT_MOVIE = 'short_movie'
    MISSING_PRIMARY_IMAGE = 'missing_primary_image'
    MISSING_TRAILER = 'missing_trailer'
    RECAP_OR_COMPILATION = 'recap_or_compilation'
    TRAILER_OR_PV = 'trailer_or_pv'
    PROMOTIONAL_CONTENT = 'promotional_content'


class EligibilityAudit(msgspec.Struct, frozen=True):
    accepted_count: int
    rejected_count: int
    rejected_ids: tuple[int, ...]
    reasons_by_rule: tuple[tuple[str, int], ...]
    reasons_by_id: tuple[tuple[int, tuple[str, ...]], ...]
    policy_version: str = 'eligibility-v2'


def is_valid_url(value: str | None) -> bool:
    """Return whether a value is an absolute HTTP(S) URL."""
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)


def has_primary_image(entry: TenraiAnimeEntry) -> bool:
    """Accept WebP first, then JPEG, while rejecting known placeholders."""
    variants = entry.images
    urls = (
        variants.webp.image_url if variants and variants.webp else None,
        variants.jpg.image_url if variants and variants.jpg else None,
    )
    return any(is_valid_url(url) and url != PLACEHOLDER_IMAGE_URL for url in urls)


def has_trailer(entry: TenraiAnimeEntry) -> bool:
    """Return whether the entry has a usable trailer URL or YouTube ID."""
    trailer = entry.trailer
    return bool(trailer and (is_valid_url(trailer.url) or trailer.youtube_id))


def has_recommendation_evidence(entry: TenraiAnimeEntry, tagged_anime_ids: Collection[int] = ()) -> bool:
    """Return whether an entry has meaningful semantic metadata for similarity."""
    return bool(entry.synopsis or entry.genres or entry.themes or entry.mal_id in tagged_anime_ids)


_HIGH_CONFIDENCE_CONTENT = (
    (re.compile(r'\b(?:recap|digest|summary|compilation)\b', re.IGNORECASE), ExclusionReason.RECAP_OR_COMPILATION),
    (re.compile(r'\b(?:pv|trailer|teaser)\b', re.IGNORECASE), ExclusionReason.TRAILER_OR_PV),
)
_CONTEXTUAL_TITLE_MARKER = re.compile(
    r'\b(?:promotional|promo|commercial|advertisement|preview|pilot|prologue|collaboration|crossover|short|mini|special)\b',
    re.IGNORECASE,
)
_PROMOTIONAL_CONTEXT = re.compile(
    r'\b(?:promot|advertis|commercial|campaign|preview|teaser|trailer|pilot film|test film|'
    r'official (?:website|channel|youtube|twitter)|not included in the (?:tv|television) series|'
    r'collaboration|crossover|recap|digest|compilation)\b',
    re.IGNORECASE,
)


def non_recommendable_reason(entry: TenraiAnimeEntry) -> ExclusionReason | None:
    """Classify clearly non-substantive entries without rejecting ambiguous titles alone."""
    title = f'{entry.title} {entry.title_english or ""}'
    for marker, reason in _HIGH_CONFIDENCE_CONTENT:
        if marker.search(title):
            return reason
    if _CONTEXTUAL_TITLE_MARKER.search(title) and _PROMOTIONAL_CONTEXT.search(entry.synopsis or ''):
        return ExclusionReason.PROMOTIONAL_CONTENT
    return None


def filter_non_recommendable_content(
    entries: list[TenraiAnimeEntry],
) -> tuple[list[TenraiAnimeEntry], dict[int, ExclusionReason]]:
    """Remove explicit recaps, trailers, and synopsis-confirmed promotional entries."""
    accepted: list[TenraiAnimeEntry] = []
    rejected: dict[int, ExclusionReason] = {}
    for entry in entries:
        reason = non_recommendable_reason(entry)
        if reason is None:
            accepted.append(entry)
        else:
            rejected[entry.mal_id] = reason
    return accepted, rejected


def filter_entries(
    entries: list[TenraiAnimeEntry],
    policy: EligibilityPolicy | None = None,
    *,
    tagged_anime_ids: Collection[int] = (),
) -> tuple[list[TenraiAnimeEntry], EligibilityAudit]:
    """Filter entries and return accepted records plus deterministic audit data."""
    active_policy = policy or EligibilityPolicy()
    accepted: list[TenraiAnimeEntry] = []
    rejected_ids: list[int] = []
    reason_counts: dict[str, int] = {}
    reasons_by_id: dict[int, tuple[str, ...]] = {}
    for entry in entries:
        reasons: list[ExclusionReason] = []
        if not active_policy.bypass_catalogue_filters:
            if normalize_media_type(entry.type) == 'MOVIE' and _is_short_movie(entry, active_policy):
                reasons.append(ExclusionReason.SHORT_MOVIE)
            if normalize_media_type(entry.type) not in active_policy.allowed_types:
                reasons.append(ExclusionReason.TYPE_NOT_ALLOWED)
            genre_ids = {genre.mal_id for genre in entry.genres}
            excluded_genres = genre_ids & active_policy.excluded_genre_ids
            if excluded_genres:
                reasons.append(ExclusionReason.EXCLUDED_GENRE)
            if active_policy.require_semantic_evidence and not has_recommendation_evidence(entry, tagged_anime_ids):
                reasons.append(ExclusionReason.MISSING_SEMANTIC_EVIDENCE)
        if entry.year is not None and entry.year > active_policy.max_year:
            reasons.append(ExclusionReason.YEAR_AFTER_CUTOFF)
        if normalize_airing_status(entry.status) is AiringStatus.NOT_YET_AIRED:
            reasons.append(ExclusionReason.NOT_YET_AIRED)
        if active_policy.require_primary_image and not has_primary_image(entry):
            reasons.append(ExclusionReason.MISSING_PRIMARY_IMAGE)
        if active_policy.require_trailer and not has_trailer(entry):
            reasons.append(ExclusionReason.MISSING_TRAILER)
        if reasons:
            rejected_ids.append(entry.mal_id)
            reasons_by_id[entry.mal_id] = tuple(reason.value for reason in reasons)
            for reason in reasons:
                reason_counts[reason.value] = reason_counts.get(reason.value, 0) + 1
        else:
            accepted.append(entry)
    audit = EligibilityAudit(
        accepted_count=len(accepted),
        rejected_count=len(rejected_ids),
        rejected_ids=tuple(sorted(rejected_ids)),
        reasons_by_rule=tuple(sorted(reason_counts.items())),
        reasons_by_id=tuple(sorted(reasons_by_id.items())),
    )
    return accepted, audit


def _is_short_movie(entry: TenraiAnimeEntry, policy: EligibilityPolicy) -> bool:
    """Exclude known movie shorts while retaining movies with unknown duration."""
    if policy.min_movie_duration_minutes < 1:
        raise ValueError('min_movie_duration_minutes must be positive')
    duration_minutes = duration_to_minutes(entry.duration)
    return duration_minutes is not None and duration_minutes <= policy.min_movie_duration_minutes
