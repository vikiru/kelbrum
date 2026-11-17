"""Recommendation-owned runtime and persisted result contracts."""

from typing import Literal

import msgspec

MAX_RECOMMENDATIONS = 100


class RecommendationExplanation(msgspec.Struct, frozen=True):
    retrieval_paths: tuple[str, ...]
    synopsis_score: float
    tag_score: float
    theme_score: float
    genre_score: float
    demographic_score: float
    qualification_reason: Literal['evidence-consensus', 'standalone-tag']
    recommendation_entity_id: int


class RecommendationItem(msgspec.Struct, frozen=True):
    anime_id: int
    score: float
    contributions: tuple[tuple[str, float], ...]
    explanation: RecommendationExplanation | None = None


class RawRecommendation(msgspec.Struct, frozen=True):
    """Ranked candidate evidence before display or qualification policy."""

    anime_id: int
    witness_member_id: int
    score: float
    retrieval_paths: tuple[str, ...]
    semantic_available: bool
    categorical_available: bool


class RecommendationResult(msgspec.Struct, frozen=True):
    source_anime_id: int
    items: tuple[RecommendationItem, ...]
    fetched_date: str


class RecommendationConfig(msgspec.Struct, frozen=True):
    limit: int = 100

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= MAX_RECOMMENDATIONS:
            raise ValueError('recommendation limit must be between 1 and 100')


class CanonicalStorylineEntry(msgspec.Struct, frozen=True):
    """Canonical storyline representative preserving the strongest constituent witness evidence."""

    canonical_anime_id: int
    best_witness_anime_id: int
    similarity_score: float
    retrieval_paths: tuple[str, ...]
    semantic_available: bool
    categorical_available: bool


class FranchiseRecommendationSlot(msgspec.Struct, frozen=True):
    """A surfaced slot representing an overarching franchise with an array of distinct canonical storylines."""

    franchise_id: int
    primary_anime_id: int
    maximum_similarity_score: float
    storyline_entries: tuple[CanonicalStorylineEntry, ...]
