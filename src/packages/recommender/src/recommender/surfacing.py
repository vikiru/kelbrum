"""Conservative variable-length display policy for ranked recommendations."""

from collections.abc import Mapping, Sequence

import msgspec

from recommender.contracts import (
    CanonicalStorylineEntry,
    FranchiseRecommendationSlot,
    RawRecommendation,
)

DEFAULT_MINIMUM_SCORE = 0.08
DEFAULT_MAXIMUM_RESULTS = 100
DEFAULT_MAX_PER_FRANCHISE = 2
DEFAULT_MAX_STORYLINES_PER_FRANCHISE = 3


class SurfacingPolicy(msgspec.Struct, frozen=True):
    """Apply display floor and franchise diversity cap without changing similarity scores."""

    name = 'surfacing-diversity-v1'
    minimum_score: float = DEFAULT_MINIMUM_SCORE
    maximum_results: int = DEFAULT_MAXIMUM_RESULTS
    max_per_franchise: int = DEFAULT_MAX_PER_FRANCHISE

    canonical_entrypoint_surfacing: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_score <= 1.0:
            raise ValueError('minimum_score must be between 0 and 1')
        if not 1 <= self.maximum_results <= DEFAULT_MAXIMUM_RESULTS:
            raise ValueError(f'maximum_results must be between 1 and {DEFAULT_MAXIMUM_RESULTS}')
        if self.max_per_franchise < 1:
            raise ValueError('max_per_franchise must be at least 1')

    def surface(
        self,
        ranked_items: Sequence[RawRecommendation],
        franchise_by_id: Mapping[int, frozenset[int]] | None = None,
        same_story_exclusions_by_id: Mapping[int, frozenset[int]] | None = None,
        story_line_by_id: Mapping[int, int] | None = None,
        source_anime_id: int | None = None,
        year_by_id: Mapping[int, int | None] | None = None,
        sequel_hops_by_id: Mapping[int, int] | None = None,
    ) -> tuple[RawRecommendation, ...]:
        storylines_by_canonical_id: dict[int, StorylineWitnessAccumulator] = {}
        original_order: list[int] = []
        for item in ranked_items:
            if item.score < self.minimum_score:
                continue
            canonical_id = (
                story_line_by_id.get(item.anime_id, item.anime_id) if story_line_by_id is not None else item.anime_id
            )
            accumulator = storylines_by_canonical_id.get(canonical_id)
            if accumulator is None:
                accumulator = StorylineWitnessAccumulator(canonical_id)
                storylines_by_canonical_id[canonical_id] = accumulator
                original_order.append(canonical_id)
            accumulator.record_witness(item)

        canonical_candidates: list[RawRecommendation] = []
        for canonical_id in original_order:
            acc = storylines_by_canonical_id[canonical_id]
            canonical_candidates.append(
                acc.to_raw_recommendation()
                if self.canonical_entrypoint_surfacing
                else acc.to_best_witness_recommendation()
            )

        anchor_franchise = (
            franchise_by_id.get(source_anime_id)
            if (source_anime_id is not None and franchise_by_id is not None)
            else None
        )
        anchor_year = (
            year_by_id.get(source_anime_id) if (source_anime_id is not None and year_by_id is not None) else None
        )
        canonical_candidates.sort(
            key=lambda item: (
                item.score
                + _franchise_tiebreak_bonus(
                    item.anime_id,
                    anchor_franchise=anchor_franchise,
                    anchor_year=anchor_year,
                    year_by_id=year_by_id,
                    sequel_hops_by_id=sequel_hops_by_id,
                )
            ),
            reverse=True,
        )

        surfaced: list[RawRecommendation] = []
        surfaced_ids: set[int] = set()
        franchise_counts: dict[frozenset[int], int] = {}

        for item in canonical_candidates:
            if len(surfaced) >= self.maximum_results:
                break

            franchise_key = (
                franchise_by_id.get(item.anime_id, frozenset({item.anime_id}))
                if franchise_by_id is not None
                else frozenset({item.anime_id})
            )
            if franchise_counts.get(franchise_key, 0) >= self.max_per_franchise:
                continue

            if same_story_exclusions_by_id is not None:
                exclusions = same_story_exclusions_by_id.get(item.anime_id, frozenset())
                if not exclusions.isdisjoint(surfaced_ids) or any(
                    item.anime_id in same_story_exclusions_by_id.get(prev_id, frozenset()) for prev_id in surfaced_ids
                ):
                    continue

            surfaced.append(item)
            surfaced_ids.add(item.anime_id)
            franchise_counts[franchise_key] = franchise_counts.get(franchise_key, 0) + 1

        return tuple(surfaced)


class StorylineWitnessAccumulator:
    """Accumulates and preserves the strongest similarity evidence across constituent member witnesses."""

    def __init__(self, canonical_anime_id: int) -> None:
        self.canonical_anime_id = canonical_anime_id
        self.best_witness_anime_id = canonical_anime_id
        self.maximum_similarity_score = -1.0
        self.retrieval_paths: set[str] = set()
        self.semantic_available = False
        self.categorical_available = False

    def record_witness(self, recommendation: RawRecommendation) -> None:
        """Update preserved evidence if the candidate exhibits higher similarity to the anchor."""
        if recommendation.score > self.maximum_similarity_score:
            self.maximum_similarity_score = recommendation.score
            self.best_witness_anime_id = recommendation.witness_member_id
        self.retrieval_paths.update(recommendation.retrieval_paths)
        self.semantic_available = self.semantic_available or recommendation.semantic_available
        self.categorical_available = self.categorical_available or recommendation.categorical_available

    def to_canonical_entry(self) -> CanonicalStorylineEntry:
        """Produce the immutable canonical storyline entry contract."""
        return CanonicalStorylineEntry(
            canonical_anime_id=self.canonical_anime_id,
            best_witness_anime_id=self.best_witness_anime_id,
            similarity_score=max(0.0, self.maximum_similarity_score),
            retrieval_paths=tuple(sorted(self.retrieval_paths)),
            semantic_available=self.semantic_available,
            categorical_available=self.categorical_available,
        )

    def to_raw_recommendation(self) -> RawRecommendation:
        return RawRecommendation(
            anime_id=self.canonical_anime_id,
            witness_member_id=self.best_witness_anime_id,
            score=max(0.0, self.maximum_similarity_score),
            retrieval_paths=tuple(sorted(self.retrieval_paths)),
            semantic_available=self.semantic_available,
            categorical_available=self.categorical_available,
        )

    def to_best_witness_recommendation(self) -> RawRecommendation:
        return RawRecommendation(
            anime_id=self.best_witness_anime_id,
            witness_member_id=self.best_witness_anime_id,
            score=max(0.0, self.maximum_similarity_score),
            retrieval_paths=tuple(sorted(self.retrieval_paths)),
            semantic_available=self.semantic_available,
            categorical_available=self.categorical_available,
        )


def collapse_to_franchise_containers(
    ranked_items: Sequence[RawRecommendation],
    *,
    franchise_by_id: Mapping[int, frozenset[int]],
    story_line_by_id: Mapping[int, int],
    minimum_similarity_score: float = DEFAULT_MINIMUM_SCORE,
    maximum_storylines_per_franchise: int = DEFAULT_MAX_STORYLINES_PER_FRANCHISE,
    maximum_display_slots: int = DEFAULT_MAXIMUM_RESULTS,
) -> tuple[FranchiseRecommendationSlot, ...]:
    """Collapse candidates to canonical storylines and organize into ranked franchise containers."""
    if maximum_storylines_per_franchise < 1:
        raise ValueError('maximum_storylines_per_franchise must be at least 1')
    if maximum_display_slots < 1:
        raise ValueError('maximum_display_slots must be at least 1')

    # 1. Aggregate member evidence into distinct canonical storylines
    storylines_by_canonical_id: dict[int, StorylineWitnessAccumulator] = {}
    for item in ranked_items:
        if item.score < minimum_similarity_score:
            continue
        canonical_id = story_line_by_id.get(item.anime_id, item.anime_id)
        accumulator = storylines_by_canonical_id.setdefault(canonical_id, StorylineWitnessAccumulator(canonical_id))
        accumulator.record_witness(item)

    # 2. Group canonical storylines into overarching franchise containers
    storylines_by_franchise_key: dict[frozenset[int], list[StorylineWitnessAccumulator]] = {}
    for canonical_id, accumulator in storylines_by_canonical_id.items():
        franchise_key = franchise_by_id.get(canonical_id, frozenset({canonical_id}))
        storylines_by_franchise_key.setdefault(franchise_key, []).append(accumulator)

    # 3. Assemble and rank franchise slots by peak similarity score
    franchise_slots: list[FranchiseRecommendationSlot] = []
    for franchise_key, accumulators in storylines_by_franchise_key.items():
        accumulators.sort(key=lambda acc: acc.maximum_similarity_score, reverse=True)
        top_entries = tuple(acc.to_canonical_entry() for acc in accumulators[:maximum_storylines_per_franchise])
        representative_franchise_id = min(franchise_key)
        franchise_slots.append(
            FranchiseRecommendationSlot(
                franchise_id=representative_franchise_id,
                primary_anime_id=top_entries[0].canonical_anime_id,
                maximum_similarity_score=top_entries[0].similarity_score,
                storyline_entries=top_entries,
            )
        )

    franchise_slots.sort(key=lambda slot: slot.maximum_similarity_score, reverse=True)
    return tuple(franchise_slots[:maximum_display_slots])


def _franchise_tiebreak_bonus(
    candidate_id: int,
    *,
    anchor_franchise: frozenset[int] | None,
    anchor_year: int | None,
    year_by_id: Mapping[int, int | None] | None,
    sequel_hops_by_id: Mapping[int, int] | None,
) -> float:
    """Small intra-franchise tie-breaker favoring era proximity and direct sequel hops."""
    if anchor_franchise is None or candidate_id not in anchor_franchise:
        return 0.0
    bonus = 0.0
    if anchor_year is not None and year_by_id is not None:
        cand_year = year_by_id.get(candidate_id)
        if cand_year is not None:
            bonus += 0.06 * max(0.0, 1.0 - abs(cand_year - anchor_year) / 20.0)
    if sequel_hops_by_id is not None:
        hops = sequel_hops_by_id.get(candidate_id)
        if hops is not None and 1 <= hops <= 3:
            bonus += 0.08 / hops
    return bonus
