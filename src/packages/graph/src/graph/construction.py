"""Deterministic construction for identity, exclusion, and context graph policies."""

from collections import deque
from collections.abc import Mapping, Sequence
from hashlib import sha256

import orjson

from graph.contracts import (
    EdgeAssertion,
    GraphNode,
    GraphRelation,
    IdentityEquivalenceAssertion,
    IdentityIntent,
    ManualEdgePolicy,
    RelationMap,
    RelationType,
    SameStoryIntent,
    TraversalMode,
)
from graph.index import RelationshipIndex
from graph.policies import FRANCHISE_RELATIONS, MANUAL_RELATION
from graph.registry import IDENTITY_EQUIVALENCE_REGISTRY, add_manual_relationships

RELATIONSHIP_POLICY_VERSION = 'same-story-identity-v1'
IDENTITY_POLICY_VERSION = 'recommendation-identity-v1'
SAME_STORY_POLICY_VERSION = 'same-story-v1'
FRANCHISE_POLICY_VERSION = 'franchise-context-v3-character-excluded-other-included'


def build_relationship_index(
    nodes: Sequence[GraphNode],
    relations: Mapping[int, Sequence[GraphRelation]],
    *,
    max_depth: int | None = None,
    manual_relationships: Mapping[int, Sequence[int]] | None = None,
    manual_edge_policies: Sequence[ManualEdgePolicy] = (),
    edge_overrides: Mapping[tuple[int, int, RelationType], SameStoryIntent] | None = None,
    identity_equivalences: Sequence[IdentityEquivalenceAssertion] = IDENTITY_EQUIVALENCE_REGISTRY,
    raw_relationship_version: str | None = None,
) -> RelationshipIndex:
    """Build three independent graph products from raw relationships and typed policy."""
    if max_depth is not None:
        raise ValueError('same-story traversal is transitive; bounded max_depth is unsupported')
    node_by_id = _validate_nodes(nodes)
    normalized = _validate_relations(relations)
    merged = add_manual_relationships(normalized, manual_relationships or {})
    catalogue_ids = frozenset(node_by_id)
    typed_manual = _validate_manual_policies(manual_edge_policies, merged)
    overrides = edge_overrides or {}
    assertions = _build_assertions(merged, typed_manual, overrides)
    reviewed_identity_edges = [
        IdentityEquivalenceAssertion(policy.source_id, policy.target_id, policy.rationale, policy.provenance)
        for policy in manual_edge_policies
        if policy.identity_intent is IdentityIntent.IDENTITY_EQUIVALENT
    ]
    identity_by_id, members_by_id = _build_identity_index(
        catalogue_ids, (*identity_equivalences, *reviewed_identity_edges)
    )
    exclusions, paths = _build_exclusion_index(catalogue_ids, assertions)
    story_line_entrypoints, story_line_members = _build_story_line_index(
        catalogue_ids, assertions, manual_edge_policies, node_by_id
    )
    franchise = _build_franchise_index(catalogue_ids, merged, manual_edge_policies)
    raw_version = raw_relationship_version or _relationship_data_hash(merged)
    return RelationshipIndex(
        recommendation_entity_by_id=identity_by_id,
        recommendation_members_by_id=members_by_id,
        exclusions_by_id=exclusions,
        exclusion_paths_by_pair=paths,
        story_line_entrypoint_by_id=story_line_entrypoints,
        story_line_members_by_id=story_line_members,
        relations_by_id=merged,
        edge_assertions=assertions,
        identity_assertions=tuple(identity_equivalences) + tuple(reviewed_identity_edges),
        franchise_by_id=franchise,
        media_type_by_id={anime_id: node.media_type for anime_id, node in node_by_id.items()},
        raw_relationship_version=raw_version,
        identity_policy_version=IDENTITY_POLICY_VERSION,
        same_story_policy_version=SAME_STORY_POLICY_VERSION,
        franchise_policy_version=FRANCHISE_POLICY_VERSION,
    )


def _validate_nodes(nodes: Sequence[GraphNode]) -> dict[int, GraphNode]:
    node_by_id: dict[int, GraphNode] = {}
    for node in nodes:
        if node.anime_id <= 0 or node.anime_id in node_by_id:
            raise ValueError(f'invalid or duplicate graph node ID: {node.anime_id}')
        node_by_id[node.anime_id] = node
    return node_by_id


def _validate_relations(relations: Mapping[int, Sequence[GraphRelation]]) -> RelationMap:
    normalized: dict[int, tuple[GraphRelation, ...]] = {}
    for source, targets in relations.items():
        if source <= 0:
            raise ValueError(f'graph relation source must be positive: {source}')
        seen: set[GraphRelation] = set()
        ordered: list[GraphRelation] = []
        for relation in targets:
            try:
                edge = GraphRelation(relation.target_id, RelationType(relation.relation))
            except ValueError as error:
                raise ValueError(f'unsupported graph relation: {source} → {relation.target_id}') from error
            if edge.target_id <= 0 or edge.target_id == source:
                if edge.target_id == source:
                    raise ValueError(f'graph relation cannot connect an ID to itself: {source}')
                raise ValueError(f'invalid graph relation target: {source} → {edge.target_id}')
            if edge in seen:
                raise ValueError(f'duplicate graph relation: {source} → {edge.target_id} [{edge.relation}]')
            seen.add(edge)
            ordered.append(edge)
        normalized[source] = tuple(ordered)
    return normalized


def _validate_manual_policies(
    policies: Sequence[ManualEdgePolicy], relations: RelationMap
) -> dict[frozenset[int], ManualEdgePolicy]:
    typed: dict[frozenset[int], ManualEdgePolicy] = {}
    for policy in policies:
        key = frozenset((policy.source_id, policy.target_id))
        if key in typed:
            raise ValueError(f'duplicate typed manual edge: {sorted(key)}')
        if not _has_manual_edge(relations, policy.source_id, policy.target_id):
            raise ValueError(f'typed manual policy has no raw manual edge: {sorted(key)}')
        typed[key] = policy
    return typed


def _has_manual_edge(relations: RelationMap, source_id: int, target_id: int) -> bool:
    return any(
        relation.target_id == target_id and relation.relation is MANUAL_RELATION
        for relation in relations.get(source_id, ())
    ) or any(
        relation.target_id == source_id and relation.relation is MANUAL_RELATION
        for relation in relations.get(target_id, ())
    )


def _build_assertions(
    relations: RelationMap,
    manual_policies: Mapping[frozenset[int], ManualEdgePolicy],
    overrides: Mapping[tuple[int, int, RelationType], SameStoryIntent],
) -> tuple[EdgeAssertion, ...]:
    assertions: list[EdgeAssertion] = []
    for source_id, edges in sorted(relations.items()):
        for relation in sorted(edges, key=lambda edge: (edge.target_id, edge.relation.value)):
            pair = frozenset((source_id, relation.target_id))
            policy = manual_policies.get(pair)
            intent = overrides.get((source_id, relation.target_id, relation.relation))
            if policy is not None:
                intent = policy.same_story_intent
            if intent is None:
                intent = _default_intent(relation.relation)
            traversal = (
                policy.traversal_mode if policy and policy.traversal_mode is not None else _traversal_mode(intent)
            )
            rationale = policy.rationale if policy else _default_rationale(relation.relation, intent)
            provenance = (
                policy.provenance
                if policy
                else (
                    'manual-registry-untyped' if relation.relation is MANUAL_RELATION else 'catalogue-relationship-feed'
                )
            )
            assertions.append(
                EdgeAssertion(
                    source_id,
                    relation.target_id,
                    relation.relation,
                    provenance,
                    f'{source_id}:{relation.relation.value}:{relation.target_id}',
                    policy.identity_intent if policy else IdentityIntent.DISTINCT,
                    intent,
                    traversal,
                    rationale,
                    RELATIONSHIP_POLICY_VERSION,
                )
            )
    return tuple(assertions)


def _default_intent(relation: RelationType) -> SameStoryIntent:
    if relation in {RelationType.SEQUEL, RelationType.PREQUEL}:
        return SameStoryIntent.CONTINUATION
    if relation in {RelationType.SUMMARY, RelationType.FULL_STORY}:
        return SameStoryIntent.SAME_STORY_LINK
    if relation in {RelationType.PARENT_STORY, RelationType.SIDE_STORY, RelationType.SPIN_OFF}:
        return SameStoryIntent.FRANCHISE_ONLY
    if relation is RelationType.MANUAL:
        return SameStoryIntent.NEEDS_REVIEW
    return SameStoryIntent.NEEDS_REVIEW


def _traversal_mode(intent: SameStoryIntent) -> TraversalMode:
    if intent is SameStoryIntent.CONTINUATION:
        return TraversalMode.TRANSITIVE
    if intent in {SameStoryIntent.SAME_STORY_LINK, SameStoryIntent.PAIRWISE_EXCLUSION}:
        return TraversalMode.ENDPOINT_ONLY
    return TraversalMode.NONE


def _default_rationale(relation: RelationType, intent: SameStoryIntent) -> str:
    if intent is SameStoryIntent.CONTINUATION:
        return f'{relation.value} defaults to continuing-story traversal.'
    if intent is SameStoryIntent.FRANCHISE_ONLY:
        return f'{relation.value} provides context without same-story exclusion.'
    if relation is RelationType.MANUAL:
        return 'Untyped manual relationship requires review and does not exclude.'
    return f'{relation.value} requires an explicit reviewed same-story override.'


def _build_identity_index(
    catalogue_ids: frozenset[int], equivalences: Sequence[IdentityEquivalenceAssertion]
) -> tuple[dict[int, int], dict[int, frozenset[int]]]:
    parent = {anime_id: anime_id for anime_id in catalogue_ids}

    def find(anime_id: int) -> int:
        while parent[anime_id] != anime_id:
            parent[anime_id] = parent[parent[anime_id]]
            anime_id = parent[anime_id]
        return anime_id

    for assertion in equivalences:
        left, right = assertion.source_id, assertion.target_id
        if left not in parent or right not in parent:
            continue
        root_left, root_right = find(left), find(right)
        parent[max(root_left, root_right)] = min(root_left, root_right)
    groups: dict[int, set[int]] = {}
    for anime_id in sorted(catalogue_ids):
        groups.setdefault(find(anime_id), set()).add(anime_id)
    identity: dict[int, int] = {}
    members: dict[int, frozenset[int]] = {}
    for group in groups.values():
        entity_id = min(group)
        frozen_group = frozenset(group)
        for anime_id in group:
            identity[anime_id] = entity_id
            members[anime_id] = frozen_group
    return identity, members


def _build_exclusion_index(
    catalogue_ids: frozenset[int], assertions: Sequence[EdgeAssertion]
) -> tuple[dict[int, frozenset[int]], dict[tuple[int, int], tuple[EdgeAssertion, ...]]]:
    transitive: dict[int, list[tuple[int, EdgeAssertion]]] = {anime_id: [] for anime_id in catalogue_ids}
    pairwise: dict[int, list[tuple[int, EdgeAssertion]]] = {anime_id: [] for anime_id in catalogue_ids}
    for assertion in assertions:
        if assertion.source_id not in catalogue_ids or assertion.target_id not in catalogue_ids:
            continue
        if assertion.traversal_mode is TraversalMode.TRANSITIVE:
            transitive[assertion.source_id].append((assertion.target_id, assertion))
            transitive[assertion.target_id].append((assertion.source_id, assertion))
        elif assertion.traversal_mode is TraversalMode.ENDPOINT_ONLY:
            pairwise[assertion.source_id].append((assertion.target_id, assertion))
            pairwise[assertion.target_id].append((assertion.source_id, assertion))
    exclusions: dict[int, frozenset[int]] = {}
    paths: dict[tuple[int, int], tuple[EdgeAssertion, ...]] = {}
    for anchor_id in sorted(catalogue_ids):
        found: dict[int, tuple[EdgeAssertion, ...]] = {anchor_id: ()}
        queue = deque((anchor_id,))
        while queue:
            current_id = queue.popleft()
            current_path = found[current_id]
            for target_id, edge in sorted(
                transitive[current_id], key=lambda item: (item[0], item[1].relation_type.value)
            ):
                if target_id not in found:
                    found[target_id] = (*current_path, edge)
                    queue.append(target_id)
        for target_id, edge in sorted(pairwise[anchor_id], key=lambda item: (item[0], item[1].relation_type.value)):
            found.setdefault(target_id, (edge,))
        exclusions[anchor_id] = frozenset(found)
        paths.update({(anchor_id, target_id): path for target_id, path in found.items() if target_id != anchor_id})
    return exclusions, paths


def _build_franchise_index(
    catalogue_ids: frozenset[int],
    relations: RelationMap,
    manual_policies: Sequence[ManualEdgePolicy],
) -> dict[int, frozenset[int]]:
    adjacency: dict[int, set[int]] = {anime_id: set() for anime_id in catalogue_ids}
    for source_id, edges in relations.items():
        if source_id not in catalogue_ids:
            continue
        for edge in edges:
            if edge.relation is RelationType.MANUAL:
                continue
            if edge.relation not in FRANCHISE_RELATIONS or edge.target_id not in catalogue_ids:
                continue
            adjacency[source_id].add(edge.target_id)
            adjacency[edge.target_id].add(source_id)
    for policy in manual_policies:
        if (
            policy.relation_type not in FRANCHISE_RELATIONS
            or policy.source_id not in catalogue_ids
            or policy.target_id not in catalogue_ids
        ):
            continue
        adjacency[policy.source_id].add(policy.target_id)
        adjacency[policy.target_id].add(policy.source_id)
    result: dict[int, frozenset[int]] = {}
    for anime_id in sorted(catalogue_ids):
        if anime_id in result:
            continue
        visited = {anime_id}
        queue = deque((anime_id,))
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        component = frozenset(visited)
        for member in component:
            result[member] = component
    return result


def _build_story_line_index(
    catalogue_ids: frozenset[int],
    assertions: Sequence[EdgeAssertion],
    manual_edge_policies: Sequence[ManualEdgePolicy] = (),
    node_by_id: Mapping[int, GraphNode] | None = None,
) -> tuple[dict[int, int], dict[int, frozenset[int]]]:
    """Compute directed story line entrypoints and their member sets."""
    # Directed continuation: A -> B where B is the continuation of A
    # Sequel: source -> target
    # Prequel: target -> source
    # Manual with SameStoryIntent.CONTINUATION: source -> target (direction defined in CSV)
    manual_dir_cont = {
        (p.source_id, p.target_id) for p in manual_edge_policies if p.same_story_intent is SameStoryIntent.CONTINUATION
    }
    manual_undir_cont = {
        frozenset((p.source_id, p.target_id))
        for p in manual_edge_policies
        if p.same_story_intent is SameStoryIntent.CONTINUATION
    }

    continuation_edges: set[tuple[int, int]] = set()
    for assertion in assertions:
        if (
            assertion.source_id not in catalogue_ids
            or assertion.target_id not in catalogue_ids
            or assertion.same_story_intent is not SameStoryIntent.CONTINUATION
        ):
            continue
        pair = (assertion.source_id, assertion.target_id)
        if frozenset(pair) in manual_undir_cont:
            if pair in manual_dir_cont:
                continuation_edges.add(pair)
            continue
        if assertion.relation_type is RelationType.PREQUEL:
            continuation_edges.add((assertion.target_id, assertion.source_id))
        else:
            continuation_edges.add((assertion.source_id, assertion.target_id))

    reverse_adjacency: dict[int, set[int]] = {}
    for u, v in continuation_edges:
        reverse_adjacency.setdefault(v, set()).add(u)

    roots_cache: dict[int, frozenset[int]] = {}

    def get_ancestor_roots(node: int) -> frozenset[int]:
        cached = roots_cache.get(node)
        if cached is not None:
            return cached
        if not reverse_adjacency.get(node):
            res = frozenset((node,))
            roots_cache[node] = res
            return res
        anc: set[int] = set()
        queue = deque((node,))
        visited = {node}
        while queue:
            curr = queue.popleft()
            for parent in reverse_adjacency.get(curr, ()):
                if parent not in visited:
                    visited.add(parent)
                    anc.add(parent)
                    queue.append(parent)
        res = frozenset(a for a in anc if not reverse_adjacency.get(a))
        roots_cache[node] = res
        return res

    # Media type preference order: TV (0) > ONA (1) > Movie (2) > other (3)
    type_priority = {'tv': 0, 'ona': 1, 'movie': 2}

    def root_sort_key(node_id: int) -> tuple[int, int]:
        m_type = (node_by_id[node_id].media_type or '').casefold() if node_by_id and node_id in node_by_id else ''
        prio = type_priority.get(m_type, 3)
        return prio, node_id

    entrypoint_by_id: dict[int, int] = {}
    members_by_entrypoint: dict[int, set[int]] = {}
    for anime_id in sorted(catalogue_ids):
        roots = get_ancestor_roots(anime_id)
        if len(roots) == 1:
            ep = next(iter(roots))
        elif len(roots) > 1:
            ep = min(roots, key=root_sort_key)
        else:
            ep = anime_id
        entrypoint_by_id[anime_id] = ep
        members_by_entrypoint.setdefault(ep, set()).add(anime_id)

    members_by_id: dict[int, frozenset[int]] = {ep: frozenset(members) for ep, members in members_by_entrypoint.items()}
    return entrypoint_by_id, members_by_id


def _relationship_data_hash(relations: RelationMap) -> str:
    payload = sorted(
        (source_id, edge.target_id, edge.relation.value) for source_id, edges in relations.items() for edge in edges
    )
    return sha256(orjson.dumps(payload)).hexdigest()
