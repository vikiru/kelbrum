from collections.abc import Callable, Sequence

from graph import RelationshipIndex
from recommender.union import PathEvidence, UnionCandidate

STORYLINE_WITNESS_SCORE_MULTIPLIER = 0.98


def qualify_candidates(
    source_anime_id: int,
    candidates: Sequence[UnionCandidate],
    *,
    relationship_index: RelationshipIndex | None = None,
    is_eligible: Callable[[int], bool] | None = None,
    is_canonical_eligible: Callable[[int], bool] | None = None,
) -> tuple[UnionCandidate, ...]:
    """Remove self, ineligible, and same-story candidates before scoring."""
    exclusions = (
        relationship_index.same_story_exclusions(source_anime_id) if relationship_index is not None else frozenset()
    )
    qualified: list[UnionCandidate] = []
    for candidate in candidates:
        candidate_id = candidate.anime_id
        if candidate_id == source_anime_id:
            continue
        if is_eligible is not None and not is_eligible(candidate_id):
            continue
        if is_canonical_eligible is not None:
            recommendation_entity_id = (
                relationship_index.recommendation_entity_id(candidate_id)
                if relationship_index is not None
                else candidate_id
            )
            if not is_canonical_eligible(recommendation_entity_id):
                continue
        if candidate_id in exclusions:
            continue
        qualified.append(candidate)
    return tuple(qualified)


def recommendation_entity_ids(
    candidates: Sequence[UnionCandidate], relationship_index: RelationshipIndex | None = None
) -> dict[int, int]:
    """Map member IDs to reviewed recommendation entity IDs."""
    if relationship_index is None:
        return {candidate.anime_id: candidate.anime_id for candidate in candidates}
    return {
        candidate.anime_id: relationship_index.recommendation_entity_id(candidate.anime_id) for candidate in candidates
    }


def canonical_candidate_ids(
    candidates: Sequence[UnionCandidate], relationship_index: RelationshipIndex | None = None
) -> dict[int, int]:
    """Deprecated compatibility alias for recommendation_entity_ids."""
    return recommendation_entity_ids(candidates, relationship_index)


def nominate_story_line_entrypoints(
    source_anime_id: int,
    candidates: Sequence[UnionCandidate],
    *,
    relationship_index: RelationshipIndex | None = None,
    is_eligible: Callable[[int], bool] | None = None,
    is_canonical_eligible: Callable[[int], bool] | None = None,
) -> tuple[tuple[UnionCandidate, ...], dict[int, tuple[int, ...]]]:
    """Nominate story-line entrypoints for qualified candidates under Option A proxy.

    For each candidate C, its story-line entrypoint E = story_line_entrypoint(C) is nominated.
    Entrypoint evidence is merged from every retrieved member that nominates it,
    including its own direct evidence when present.
    Returns (entrypoint_candidates, nomination_provenance) where nomination_provenance maps
    entrypoint_id -> tuple of member IDs that nominated it in stable sorted order.
    """
    if relationship_index is None:
        return tuple(candidates), {c.anime_id: (c.anime_id,) for c in candidates}

    retrieved_by_id = {c.anime_id: c for c in candidates}
    nominations: dict[int, set[int]] = {}
    same_story_excluded = relationship_index.same_story_exclusions(source_anime_id)

    for c in candidates:
        member_id = c.anime_id
        entrypoint_id = relationship_index.story_line_entrypoint(member_id)

        if entrypoint_id == source_anime_id:
            continue
        if entrypoint_id in same_story_excluded:
            continue
        if is_eligible is not None and not is_eligible(entrypoint_id):
            continue
        if is_canonical_eligible is not None:
            rec_id = relationship_index.recommendation_entity_id(entrypoint_id)
            if not is_canonical_eligible(rec_id):
                continue

        nominations.setdefault(entrypoint_id, set()).add(member_id)

    # Order entrypoints deterministically: first those retrieved directly in candidate order,
    # then newly nominated entrypoints sorted by ID
    seen_entrypoints: set[int] = set()
    ordered_entrypoints: list[UnionCandidate] = []
    provenance: dict[int, tuple[int, ...]] = {}

    def build_entrypoint_candidate(entrypoint_id: int) -> UnionCandidate:
        best_by_path: dict[str, tuple[tuple[float, int, int], PathEvidence]] = {}
        witness_list: list[PathEvidence] = []
        for member_id in sorted(nominations[entrypoint_id]):
            member_candidate = retrieved_by_id.get(member_id)
            if member_candidate is None:
                continue
            for item in member_candidate.evidence:
                ev = PathEvidence(
                    item.path,
                    item.rank,
                    item.score,
                    item.post_reducer_position,
                    member_id,
                )
                witness_list.append(ev)
                key = (-item.score, item.rank, member_id)
                prev = best_by_path.get(item.path)
                if prev is None or key < prev[0]:
                    best_by_path[item.path] = (key, ev)
        if not witness_list:
            return UnionCandidate(entrypoint_id, ())
        ordered_evidence = tuple(best_by_path[path][1] for path in sorted(best_by_path))
        return UnionCandidate(
            anime_id=entrypoint_id,
            evidence=ordered_evidence,
            witness_evidence=tuple(witness_list),
        )

    for candidate in candidates:
        entrypoint_id = relationship_index.story_line_entrypoint(candidate.anime_id)
        if entrypoint_id in nominations and entrypoint_id not in seen_entrypoints:
            seen_entrypoints.add(entrypoint_id)
            ordered_entrypoints.append(build_entrypoint_candidate(entrypoint_id))
            provenance[entrypoint_id] = tuple(sorted(nominations[entrypoint_id]))

    for entrypoint_id in sorted(nominations):
        if entrypoint_id not in seen_entrypoints:
            seen_entrypoints.add(entrypoint_id)
            ordered_entrypoints.append(build_entrypoint_candidate(entrypoint_id))
            provenance[entrypoint_id] = tuple(sorted(nominations[entrypoint_id]))

    return tuple(ordered_entrypoints), provenance


def expand_story_line_entrypoints(
    candidates: Sequence[UnionCandidate],
    *,
    relationship_index: RelationshipIndex | None = None,
) -> tuple[tuple[UnionCandidate, ...], dict[int, int]]:
    """Create one feature-scoring candidate per entrypoint and retrieved witness."""
    scoring_candidates: list[UnionCandidate] = []
    recommendation_entities: dict[int, int] = {}

    for candidate in candidates:
        entrypoint_id = candidate.anime_id
        evidence_by_witness = _evidence_by_witness(candidate)
        endpoint_evidence = evidence_by_witness.pop(entrypoint_id, ()) or candidate.evidence
        entity_id = entrypoint_id
        if relationship_index is not None:
            entity_id = relationship_index.recommendation_entity_id(entrypoint_id)

        scoring_candidates.append(
            UnionCandidate(
                anime_id=entrypoint_id,
                evidence=endpoint_evidence,
                witness_evidence=endpoint_evidence,
                witness_member_id=entrypoint_id,
            )
        )
        recommendation_entities[entrypoint_id] = entity_id

        for witness_id, witness_evidence in sorted(evidence_by_witness.items()):
            scoring_candidates.append(
                UnionCandidate(
                    anime_id=witness_id,
                    evidence=witness_evidence,
                    witness_evidence=witness_evidence,
                    witness_member_id=witness_id,
                    score_multiplier=STORYLINE_WITNESS_SCORE_MULTIPLIER,
                )
            )
            recommendation_entities[witness_id] = entity_id

    return tuple(scoring_candidates), recommendation_entities


def _evidence_by_witness(candidate: UnionCandidate) -> dict[int, tuple[PathEvidence, ...]]:
    evidence = candidate.witness_evidence or candidate.evidence
    grouped: dict[int, list[PathEvidence]] = {}
    for item in evidence:
        witness_id = item.witness_member_id or candidate.anime_id
        grouped.setdefault(witness_id, []).append(item)
    return {witness_id: tuple(items) for witness_id, items in grouped.items()}
