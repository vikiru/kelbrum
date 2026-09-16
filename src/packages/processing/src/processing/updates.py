"""Known-record refresh and staged-candidate promotion seams."""

from typing import Literal

import msgspec

from fetch.contracts import TenraiAnimeEntry
from processing.canonicalize import canonicalize
from processing.contracts import CanonicalAnime


class FieldChange(msgspec.Struct, frozen=True):
    field: str
    classification: Literal['display-only', 'feature-bearing', 'catalogue-membership']


class RefreshResult(msgspec.Struct, frozen=True):
    record: CanonicalAnime
    changes: tuple[FieldChange, ...]


class PromotionPolicy(msgspec.Struct, frozen=True):
    require_synopsis: bool = True
    require_year: bool = False
    require_image: bool = True


def refresh_known(existing: CanonicalAnime, update: TenraiAnimeEntry) -> RefreshResult:
    """Convert a Tenrai update and classify changed canonical fields."""
    refreshed = canonicalize(update)
    changes: list[FieldChange] = []
    for field, classification in (
        ('title', 'display-only'),
        ('images', 'display-only'),
        ('synopsis', 'feature-bearing'),
        ('genres', 'feature-bearing'),
        ('themes', 'feature-bearing'),
        ('year', 'feature-bearing'),
        ('episodes', 'feature-bearing'),
    ):
        if getattr(existing, field) != getattr(refreshed, field):
            changes.append(FieldChange(field, classification))
    return RefreshResult(refreshed, tuple(changes))


def promotion_reasons(entry: TenraiAnimeEntry, policy: PromotionPolicy | None = None) -> tuple[str, ...]:
    """Return reasons a staged candidate is not ready for promotion."""
    active_policy = policy or PromotionPolicy()
    reasons: list[str] = []
    if not entry.mal_id or not entry.title.strip():
        reasons.append('missing_identity_or_title')
    if active_policy.require_synopsis and not entry.synopsis:
        reasons.append('missing_synopsis')
    if active_policy.require_year and entry.year is None:
        reasons.append('missing_year')
    if active_policy.require_image and not entry.images:
        reasons.append('missing_image')
    return tuple(reasons)


def promote_candidate(entry: TenraiAnimeEntry, policy: PromotionPolicy | None = None) -> CanonicalAnime:
    """Promote a candidate or fail with actionable missing-field reasons."""
    reasons = promotion_reasons(entry, policy)
    if reasons:
        raise ValueError(f'candidate {entry.mal_id} is not promotion-ready: {", ".join(reasons)}')
    return canonicalize(entry)
