"""Candidate cleanup against relationship families."""

from collections.abc import Mapping, Sequence


def cleanup_candidate_ids(
    anchor_id: int,
    candidate_ids: Sequence[int],
    family_by_id: Mapping[int, frozenset[int]],
    canonical_by_id: Mapping[int, int],
) -> tuple[int, ...]:
    """Remove the anchor family and retain one ID per candidate family."""
    excluded = family_by_id.get(anchor_id, frozenset({anchor_id}))
    retained: list[int] = []
    seen_canonicals: set[int] = set()
    for candidate_id in candidate_ids:
        if candidate_id in excluded:
            continue
        canonical_id = canonical_by_id.get(candidate_id, candidate_id)
        if canonical_id in seen_canonicals:
            continue
        seen_canonicals.add(canonical_id)
        retained.append(canonical_id)
    return tuple(retained)
