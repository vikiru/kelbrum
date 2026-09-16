"""Deterministic relationship-family construction over normalized graph inputs."""

from collections.abc import Mapping, Sequence

from graph.contracts import GraphNode, GraphRelation, RelationMap, RelationType
from graph.families import bounded_family, connected_families
from graph.index import RelationshipIndex
from graph.policies import FRANCHISE_RELATIONS, MANUAL_RELATION, STRONG_SAME_STORY_RELATIONS
from graph.registry import add_manual_relationships
from graph.representatives import non_origin_ids, select_representative


def build_relationship_index(
    nodes: Sequence[GraphNode],
    relations: Mapping[int, Sequence[GraphRelation]],
    *,
    max_depth: int | None = None,
    manual_relationships: Mapping[int, Sequence[int]] | None = None,
) -> RelationshipIndex:
    """Build deterministic same-story families from normalized nodes and edges."""
    if max_depth is not None and max_depth < 0:
        raise ValueError('max_depth must be non-negative')
    node_by_id = _validate_nodes(nodes)
    normalized = _validate_relations(relations)
    merged = add_manual_relationships(normalized, manual_relationships or {})
    adjacency = _strong_adjacency(merged)
    node_ids = tuple(sorted(node_by_id))
    origin_policy = non_origin_ids(merged)

    if max_depth is None:
        families, canonical = _build_component_index(node_ids, adjacency, node_by_id, origin_policy)
    else:
        families = {}
        canonical = {}
        for anime_id in node_ids:
            family = bounded_family(anime_id, adjacency, max_depth)
            families[anime_id] = family
            canonical[anime_id] = select_representative(family, node_by_id, origin_policy)

    franchise_families = connected_families(node_ids, _all_adjacency(merged))
    media_types = {anime_id: node.media_type for anime_id, node in node_by_id.items()}
    return RelationshipIndex(
        families,
        canonical,
        merged,
        franchise_by_id=franchise_families,
        media_type_by_id=media_types,
    )


def _validate_nodes(nodes: Sequence[GraphNode]) -> dict[int, GraphNode]:
    """Index graph nodes while rejecting invalid or duplicate catalogue IDs."""
    node_by_id: dict[int, GraphNode] = {}
    for node in nodes:
        if node.anime_id <= 0:
            raise ValueError(f'graph node ID must be positive: {node.anime_id}')
        if node.anime_id in node_by_id:
            raise ValueError(f'duplicate graph node ID: {node.anime_id}')
        node_by_id[node.anime_id] = node
    return node_by_id


def _validate_relations(relations: Mapping[int, Sequence[GraphRelation]]) -> RelationMap:
    """Normalize and validate every directed relation at the graph boundary."""
    normalized: dict[int, tuple[GraphRelation, ...]] = {}
    for source, targets in relations.items():
        if source <= 0:
            raise ValueError(f'graph relation source must be positive: {source}')
        seen: set[GraphRelation] = set()
        ordered: list[GraphRelation] = []
        for relation in targets:
            try:
                normalized_relation = GraphRelation(relation.target_id, RelationType(relation.relation))
            except ValueError as error:
                raise ValueError(f'unsupported graph relation: {source} → {relation.target_id}') from error
            if normalized_relation.target_id <= 0:
                raise ValueError(f'graph relation target must be positive: {normalized_relation.target_id}')
            if normalized_relation.target_id == source:
                raise ValueError(f'graph relation cannot connect an ID to itself: {source}')
            if normalized_relation in seen:
                raise ValueError(
                    f'duplicate graph relation: {source} → '
                    f'{normalized_relation.target_id} [{normalized_relation.relation}]'
                )
            seen.add(normalized_relation)
            ordered.append(normalized_relation)
        normalized[source] = tuple(ordered)
    return normalized


def _build_component_index(
    node_ids: Sequence[int],
    adjacency: Mapping[int, frozenset[int]],
    node_by_id: Mapping[int, GraphNode],
    non_origin_ids: frozenset[int],
) -> tuple[dict[int, frozenset[int]], dict[int, int]]:
    """Build one canonical representative for every connected same-story family."""
    families = connected_families(node_ids, adjacency)
    canonical: dict[int, int] = {}
    for anime_id, family in families.items():
        canonical[anime_id] = select_representative(family, node_by_id, non_origin_ids)
    return families, canonical


def _strong_adjacency(relations: RelationMap) -> dict[int, frozenset[int]]:
    """Select relation edges that participate in same-story canonicalization."""
    spin_off_pairs = {
        frozenset((source, relation.target_id))
        for source, targets in relations.items()
        for relation in targets
        if relation.relation == 'Spin-Off'
    }
    adjacency: dict[int, set[int]] = {}
    for source, targets in relations.items():
        strong_targets = adjacency.setdefault(source, set())
        for relation in targets:
            is_parent_spin_off = (
                relation.relation == 'Parent Story' and frozenset((source, relation.target_id)) in spin_off_pairs
            )
            if (
                relation.relation in STRONG_SAME_STORY_RELATIONS and not is_parent_spin_off
            ) or relation.relation == MANUAL_RELATION:
                strong_targets.add(relation.target_id)
    return {source: frozenset(targets) for source, targets in adjacency.items()}


def _all_adjacency(relations: RelationMap) -> dict[int, frozenset[int]]:
    """Build undirected connectivity for complete franchise membership."""
    adjacency: dict[int, set[int]] = {}
    for source, targets in relations.items():
        source_targets = adjacency.setdefault(source, set())
        for relation in targets:
            if relation.relation not in FRANCHISE_RELATIONS:
                continue
            source_targets.add(relation.target_id)
            adjacency.setdefault(relation.target_id, set()).add(source)
    return {source: frozenset(targets) for source, targets in adjacency.items()}
