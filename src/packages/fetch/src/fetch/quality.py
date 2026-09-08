"""Deterministic acceptance rules for fetched catalogue records."""

import re
from collections.abc import Sequence

import msgspec

from models.tenrai import TenraiAnimeEntry
from models.tenrai_types import normalize_media_type

_PROMOTIONAL_MARKERS = re.compile(
    r'\b(?:promo(?:tional)? video|pv|trailer|commercial|game trailer|music video|recap|preview|teaser|short)\b',
    re.IGNORECASE,
)
_EXCLUDED_GENRE_IDS = frozenset({9, 12, 49})


class CatalogueAcceptancePolicy(msgspec.Struct, frozen=True):
    """Explicit production acceptance settings for fetched records."""

    allowed_types: frozenset[str] | None = None
    allowed_ratings: frozenset[str] | None = None
    require_approved: bool = True
    require_synopsis: bool = True
    reject_promotional_ona: bool = True
    excluded_genre_ids: frozenset[int] = _EXCLUDED_GENRE_IDS


class FilterDecision(msgspec.Struct, frozen=True):
    """Auditable acceptance result for one fetched record."""

    anime_id: int
    accepted: bool
    reasons: tuple[str, ...]


def filter_catalogue(
    entries: Sequence[TenraiAnimeEntry],
    policy: CatalogueAcceptancePolicy | None = None,
) -> tuple[tuple[TenraiAnimeEntry, ...], tuple[FilterDecision, ...]]:
    """Return accepted entries and deterministic per-record filter decisions."""
    active_policy = policy or CatalogueAcceptancePolicy()
    accepted: list[TenraiAnimeEntry] = []
    decisions: list[FilterDecision] = []
    for entry in sorted(entries, key=_entry_order):
        reasons = _rejection_reasons(entry, active_policy)
        decision = FilterDecision(entry.mal_id, not reasons, tuple(reasons))
        decisions.append(decision)
        if decision.accepted:
            accepted.append(entry)
    return tuple(accepted), tuple(decisions)


def _entry_order(entry: TenraiAnimeEntry) -> int:
    return entry.mal_id


def _rejection_reasons(entry: TenraiAnimeEntry, policy: CatalogueAcceptancePolicy) -> list[str]:
    reasons: list[str] = []
    entry_type = normalize_media_type(entry.type)
    if policy.allowed_types is not None and entry_type not in policy.allowed_types:
        reasons.append('type_not_allowed')
    if policy.require_approved and entry.approved is False:
        reasons.append('not_approved')
    if policy.require_synopsis and not (entry.synopsis and entry.synopsis.strip()):
        reasons.append('missing_synopsis')
    if policy.allowed_ratings is not None and (entry.rating or '').lower() not in policy.allowed_ratings:
        reasons.append('rating_not_allowed')
    if {genre.mal_id for genre in entry.genres} & policy.excluded_genre_ids:
        reasons.append('excluded_genre')
    if policy.reject_promotional_ona and entry_type == 'ONA' and _is_promotional(entry):
        reasons.append('ona_non_substantive')
    return reasons


def _is_promotional(entry: TenraiAnimeEntry) -> bool:
    searchable = ' '.join((entry.title, entry.title_english or '', entry.synopsis or ''))
    return bool(_PROMOTIONAL_MARKERS.search(searchable))
