"""Representative selection and relation-derived origin policy."""

from collections.abc import Mapping

from graph.contracts import GraphNode, RelationMap, RelationType


def non_origin_ids(relations: RelationMap) -> frozenset[int]:
    """Identify entries explicitly represented as sequels, summaries, or full stories."""
    non_origin: set[int] = set()
    for source_id, targets in relations.items():
        for relation in targets:
            if relation.relation in {RelationType.PREQUEL, RelationType.FULL_STORY}:
                non_origin.add(source_id)
            elif relation.relation in {RelationType.SEQUEL, RelationType.SUMMARY, RelationType.ALTERNATIVE_VERSION}:
                non_origin.add(relation.target_id)
    return frozenset(non_origin)


def select_representative(
    family: frozenset[int],
    node_by_id: Mapping[int, GraphNode],
    non_origin: frozenset[int],
) -> int:
    """Choose origin first, then media preference, then ID for deterministic ties."""
    best_member = next(iter(family))
    best_key = _representative_sort_key(best_member, node_by_id, non_origin)
    for member_id in family:
        member_key = _representative_sort_key(member_id, node_by_id, non_origin)
        if member_key < best_key:
            best_member = member_id
            best_key = member_key
    return best_member


def _representative_sort_key(
    anime_id: int,
    node_by_id: Mapping[int, GraphNode],
    non_origin: frozenset[int],
) -> tuple[int, int, int]:
    """Rank family members by origin status, media priority, and stable ID."""
    media_type = node_by_id[anime_id].media_type if anime_id in node_by_id else None
    media_priority = {'TV': 0, 'MOVIE': 1, 'ONA': 2, 'OVA': 3, 'SPECIAL': 4}.get((media_type or '').strip().upper(), 5)
    return int(anime_id in non_origin), media_priority, anime_id
