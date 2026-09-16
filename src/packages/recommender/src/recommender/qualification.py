"""Candidate eligibility and same-story exclusion policy."""

from collections.abc import Callable, Sequence

from graph import RelationshipIndex
from recommender.union import UnionCandidate


def qualify_candidates(
    source_anime_id: int,
    candidates: Sequence[UnionCandidate],
    *,
    relationship_index: RelationshipIndex | None = None,
    is_eligible: Callable[[int], bool] | None = None,
) -> tuple[UnionCandidate, ...]:
    """Remove self, ineligible, and same-story candidates before scoring."""
    qualified: list[UnionCandidate] = []
    for candidate in candidates:
        candidate_id = candidate.anime_id
        if candidate_id == source_anime_id:
            continue
        if is_eligible is not None and not is_eligible(candidate_id):
            continue
        if relationship_index is not None and relationship_index.is_same_story(source_anime_id, candidate_id):
            continue
        qualified.append(candidate)
    return tuple(qualified)


def canonical_candidate_ids(
    candidates: Sequence[UnionCandidate], relationship_index: RelationshipIndex | None = None
) -> dict[int, int]:
    """Map each qualified alias ID to its canonical recommendation ID."""
    if relationship_index is None:
        return {candidate.anime_id: candidate.anime_id for candidate in candidates}
    return {candidate.anime_id: relationship_index.canonical_id(candidate.anime_id) for candidate in candidates}
