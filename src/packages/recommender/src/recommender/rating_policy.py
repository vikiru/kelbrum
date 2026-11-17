"""Configurable age-rating compatibility for recommendation candidates."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import TYPE_CHECKING

import msgspec

from anime_catalogue.demographics import Demographic, parse_demographic
from normalization.ratings import RatingClass, normalize_rating

if TYPE_CHECKING:
    from collections.abc import Collection, Sequence


_cached_normalize_rating = lru_cache(maxsize=64)(normalize_rating)
_cached_parse_demographic = lru_cache(maxsize=64)(parse_demographic)


class RatingPolicyMode(StrEnum):
    BASELINE_A = 'baseline_a'
    POLICY_D_COND = 'policy_d_cond'


class RatingDecision(msgspec.Struct, frozen=True):
    allowed: bool
    reason: str
    parent_rating: str
    candidate_rating: str
    multiplier: float = 1.0


CHILDREN_RATINGS = frozenset({RatingClass.G, RatingClass.PG})
GENERAL_AUDIENCE_RATINGS = frozenset({RatingClass.G, RatingClass.PG, RatingClass.PG_13})
TEEN_COMPATIBLE_RATINGS = frozenset({RatingClass.G, RatingClass.PG, RatingClass.PG_13, RatingClass.R})
UNKNOWN_ANCHOR_COMPATIBLE_RATINGS = TEEN_COMPATIBLE_RATINGS | {RatingClass.UNKNOWN}
MATURE_RATINGS = frozenset({RatingClass.R, RatingClass.R_PLUS, RatingClass.R_X})


class RatingPolicy(msgspec.Struct, frozen=True):
    """Apply asymmetric maturity rules and compatibility multipliers."""

    mode: str = RatingPolicyMode.POLICY_D_COND.value
    name: str = 'rating-compatibility-v8'

    @property
    def identity(self) -> str:
        return f'{self.name}:{self.mode}'

    @classmethod
    def baseline_a(cls) -> RatingPolicy:
        return cls(mode=RatingPolicyMode.BASELINE_A.value, name='rating-compatibility-v6')

    @classmethod
    def policy_d_cond(cls) -> RatingPolicy:
        return cls(mode=RatingPolicyMode.POLICY_D_COND.value, name='rating-compatibility-v8')

    def evaluate(
        self,
        parent_rating: str | None,
        candidate_rating: str | None,
        *,
        parent_demographics: Collection[str] | Sequence[str] | None = None,
        candidate_demographics: Collection[str] | Sequence[str] | None = None,
        shared_themes: Collection[str] | None = None,
        shared_tags: Collection[str] | None = None,
        dense_cosine: float | None = None,
    ) -> RatingDecision:
        parent = _cached_normalize_rating(parent_rating)
        candidate = _cached_normalize_rating(candidate_rating)
        is_adult_demo = bool(parent_demographics) and any(
            _cached_parse_demographic(demographic) in (Demographic.SEINEN, Demographic.JOSEI)
            for demographic in parent_demographics
        )
        is_seinen = bool(parent_demographics) and any(
            _cached_parse_demographic(demographic) == Demographic.SEINEN for demographic in parent_demographics
        )

        if self.mode == RatingPolicyMode.BASELINE_A.value or self.name == 'rating-compatibility-v6':
            if parent is RatingClass.UNKNOWN:
                allowed = candidate in UNKNOWN_ANCHOR_COMPATIBLE_RATINGS
                reason = (
                    'retained'
                    if allowed
                    else 'explicit_content_excluded'
                    if candidate in {RatingClass.R_PLUS, RatingClass.R_X}
                    else 'unknown_anchor_maturity_ceiling'
                )
                return RatingDecision(allowed, reason, parent.value, candidate.value, 1.0 if allowed else 0.0)
            if candidate is RatingClass.UNKNOWN:
                allowed = parent not in CHILDREN_RATINGS
                reason = 'retained' if allowed else 'unknown_candidate_requires_teen_or_mature_anchor'
                return RatingDecision(allowed, reason, parent.value, candidate.value, 1.0 if allowed else 0.0)

            if parent in CHILDREN_RATINGS:
                allowed = candidate in GENERAL_AUDIENCE_RATINGS
            elif parent is RatingClass.PG_13:
                allowed = candidate in TEEN_COMPATIBLE_RATINGS
            else:
                allowed = candidate in GENERAL_AUDIENCE_RATINGS or parent in MATURE_RATINGS

            return RatingDecision(
                allowed,
                'retained' if allowed else 'rating_excluded',
                parent.value,
                candidate.value,
                1.0 if allowed else 0.0,
            )

        # Precedence Level 1: Hard Eligibility Ceilings
        if candidate is RatingClass.R_X:
            return RatingDecision(False, 'explicit_content_excluded', parent.value, candidate.value, 0.0)

        if parent is RatingClass.UNKNOWN:
            allowed = candidate in UNKNOWN_ANCHOR_COMPATIBLE_RATINGS and candidate is not RatingClass.R_X
            reason = (
                'retained'
                if allowed
                else 'explicit_content_excluded'
                if candidate in {RatingClass.R_PLUS, RatingClass.R_X}
                else 'unknown_anchor_maturity_ceiling'
            )
            return RatingDecision(allowed, reason, parent.value, candidate.value, 1.0 if allowed else 0.0)

        if candidate is RatingClass.UNKNOWN:
            allowed = parent not in CHILDREN_RATINGS
            reason = 'retained' if allowed else 'unknown_candidate_requires_teen_or_mature_anchor'
            return RatingDecision(allowed, reason, parent.value, candidate.value, 1.0 if allowed else 0.0)

        if parent in CHILDREN_RATINGS:
            allowed = candidate in GENERAL_AUDIENCE_RATINGS
            if not allowed:
                return RatingDecision(False, 'rating_excluded', parent.value, candidate.value, 0.0)
        elif parent is RatingClass.PG_13:
            allowed = candidate in TEEN_COMPATIBLE_RATINGS or (is_adult_demo and candidate is RatingClass.R_PLUS)
            if not allowed:
                return RatingDecision(False, 'rating_excluded', parent.value, candidate.value, 0.0)
        else:  # Mature parent (R, R+, Rx)
            allowed = candidate in {RatingClass.G, RatingClass.PG, RatingClass.PG_13, RatingClass.R, RatingClass.R_PLUS}
            if not allowed:
                return RatingDecision(False, 'rating_excluded', parent.value, candidate.value, 0.0)

        # Precedence Level 2: Base Cohort Multiplier M_rating
        m_rating = 1.00
        if parent in {RatingClass.R, RatingClass.R_PLUS, RatingClass.R_X} and candidate in CHILDREN_RATINGS:
            m_rating = 0.25 if is_seinen else 0.60
        elif parent is RatingClass.PG_13 and candidate in CHILDREN_RATINGS:
            m_rating = 0.25 if is_seinen else 0.95
        elif parent in CHILDREN_RATINGS and candidate is RatingClass.PG_13:
            m_rating = 0.90

        # Precedence Level 3: Conditional Narrative Multiplier M_narrative
        m_narrative = 1.00
        is_kids = False
        if candidate_demographics:
            is_kids = any(parse_demographic(str(d)) is Demographic.KIDS for d in candidate_demographics)

        if is_kids and parent in {RatingClass.PG_13, RatingClass.R, RatingClass.R_PLUS, RatingClass.R_X}:
            has_strong_narrative = (
                bool(shared_themes) or bool(shared_tags) or (dense_cosine is not None and dense_cosine >= 0.45)
            )
            if has_strong_narrative:
                if candidate is RatingClass.PG_13:
                    m_narrative = 0.90
                elif candidate in CHILDREN_RATINGS:
                    m_narrative = 0.80
                else:
                    m_narrative = 1.00
            else:
                m_narrative = 0.60 if candidate is RatingClass.PG_13 or candidate in CHILDREN_RATINGS else 1.00

        multiplier = round(m_rating * m_narrative, 4)
        return RatingDecision(True, 'retained', parent.value, candidate.value, multiplier)

    def multiplier(
        self,
        parent_rating: str | None,
        candidate_rating: str | None,
        *,
        parent_demographics: Collection[str] | Sequence[str] | None = None,
        candidate_demographics: Collection[str] | Sequence[str] | None = None,
        shared_themes: Collection[str] | None = None,
        shared_tags: Collection[str] | None = None,
        dense_cosine: float | None = None,
    ) -> float:
        decision = self.evaluate(
            parent_rating,
            candidate_rating,
            parent_demographics=parent_demographics,
            candidate_demographics=candidate_demographics,
            shared_themes=shared_themes,
            shared_tags=shared_tags,
            dense_cosine=dense_cosine,
        )
        return decision.multiplier if decision.allowed else 0.0

    def multipliers_batch(
        self,
        parent_rating: str | None,
        candidate_ratings: Sequence[str | None],
        *,
        parent_demographics: Collection[str] | Sequence[str] | None = None,
        candidate_demographics_seq: Sequence[Collection[str] | Sequence[str] | None],
        shared_themes_seq: Sequence[Collection[str] | None],
        shared_tags_seq: Sequence[Collection[str] | None],
        dense_cosines: Sequence[float | None],
    ) -> list[float]:
        """Evaluate rating multipliers for a batch of candidates."""
        evaluate_rating = self.evaluate
        return [
            decision.multiplier if decision.allowed else 0.0
            for decision in (
                evaluate_rating(
                    parent_rating,
                    candidate_rating,
                    parent_demographics=parent_demographics,
                    candidate_demographics=candidate_demographics,
                    shared_themes=shared_themes,
                    shared_tags=shared_tags,
                    dense_cosine=dense_cosine,
                )
                for candidate_rating, candidate_demographics, shared_themes, shared_tags, dense_cosine in zip(
                    candidate_ratings,
                    candidate_demographics_seq,
                    shared_themes_seq,
                    shared_tags_seq,
                    dense_cosines,
                    strict=True,
                )
            )
        ]
