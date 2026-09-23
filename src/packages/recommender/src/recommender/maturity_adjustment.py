"""Optional maturity mismatch adjustment for weakly supported matches."""

from __future__ import annotations

from typing import TYPE_CHECKING

from recommender.rating_policy import RatingClass

if TYPE_CHECKING:
    from collections.abc import Collection

RATING_LEVELS: dict[RatingClass, int] = {
    RatingClass.G: 0,
    RatingClass.PG: 1,
    RatingClass.PG_13: 2,
    RatingClass.R: 3,
    RatingClass.R_PLUS: 4,
    RatingClass.R_X: 5,
}


def weak_maturity_penalty(
    source_rating: RatingClass,
    candidate_rating: RatingClass,
    shared_genres: Collection[str],
    shared_themes: Collection[str],
    semantic_percentile: float,
    *,
    semantic_threshold: float = 0.25,
    penalty: float = 0.02,
) -> float:
    """Return a bounded penalty for lower-rated, weakly supported PG-13 matches."""
    if source_rating is not RatingClass.PG_13 or not _is_lower_rating(source_rating, candidate_rating):
        return 0.0
    if shared_genres or len(shared_themes) > 1 or semantic_percentile > semantic_threshold:
        return 0.0
    return penalty


def _is_lower_rating(source_rating: RatingClass, candidate_rating: RatingClass) -> bool:
    source_level = RATING_LEVELS.get(source_rating)
    candidate_level = RATING_LEVELS.get(candidate_rating)
    return source_level is not None and candidate_level is not None and candidate_level < source_level


def is_weak_special_maturity_mismatch(
    source_rating: RatingClass,
    candidate_rating: RatingClass,
    candidate_type: str | None,
    candidate_episodes: int | None,
    candidate_source: str | None,
    candidate_score: float | None,
    shared_genres: Collection[str],
    shared_themes: Collection[str],
) -> bool:
    """Identify the narrow, low-evidence special-case mismatch for soft demotion."""
    return (
        source_rating is RatingClass.PG_13
        and _is_lower_rating(source_rating, candidate_rating)
        and candidate_type in {'MOVIE', 'OVA', 'ONA', 'Movie', 'Ova', 'Ona'}
        and candidate_episodes == 1
        and candidate_source in {None, '', 'Unknown'}
        and candidate_score is not None
        and candidate_score <= 6.5
        and not shared_genres
        and len(shared_themes) <= 1
    )
