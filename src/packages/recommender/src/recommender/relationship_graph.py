"""Precomputed RelationshipGraph identity cleanup for catalogue-scale use."""

from collections import deque
from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path

import msgspec

from models.tenrai import TenraiAnimeEntry
from recommender.identity_policy import STRONG_SAME_STORY_RELATIONS
from storage.json_io import read_json

MANUAL_RELATION = 'Artificial/Manual'
RelationMap = dict[int, tuple[tuple[int, str], ...]]


class RelationshipIndex(msgspec.Struct, frozen=True):
    """Immutable family membership and canonical entrypoint lookup."""

    family_by_id: Mapping[int, frozenset[int]]
    canonical_by_id: Mapping[int, int]
    relations_by_id: Mapping[int, tuple[tuple[int, str], ...]] = msgspec.field(default_factory=dict)

    def get_relationships(self, anime_id: int) -> tuple[tuple[int, str], ...]:
        """Return all retained anime relations for an ID."""
        return self.relations_by_id.get(anime_id, ())

    def to_string(self, anime_id: int | None = None) -> str:
        """Render one node or the complete graph in a compact readable form."""
        ids = (anime_id,) if anime_id is not None else tuple(sorted(self.canonical_by_id))
        lines: list[str] = []
        for current_id in ids:
            relations = (
                ', '.join(f'{target} [{relation}]' for target, relation in self.get_relationships(current_id)) or 'none'
            )
            family = ', '.join(str(member) for member in sorted(self.excluded_ids(current_id)))
            lines.append(
                f'{current_id} → canonical {self.canonical_by_id.get(current_id, current_id)}; '
                f'family {{{family}}}; relations: {relations}'
            )
        return '\n'.join(lines)

    def excluded_ids(self, anchor_id: int) -> frozenset[int]:
        """Return the complete same-story family for an anchor."""
        return self.family_by_id.get(anchor_id, frozenset({anchor_id}))

    def canonical_id(self, anime_id: int) -> int:
        """Return the canonical origin entry for an anime family member."""
        return self.canonical_by_id.get(anime_id, anime_id)

    def cleanup(self, anchor_id: int, candidate_ids: Sequence[int]) -> tuple[int, ...]:
        """Remove the anchor family and keep one deterministic ID per candidate family."""
        excluded = self.excluded_ids(anchor_id)
        retained: list[int] = []
        seen_canonicals: set[int] = set()
        for candidate_id in candidate_ids:
            if candidate_id in excluded:
                continue
            canonical_id = self.canonical_id(candidate_id)
            if canonical_id in seen_canonicals:
                continue
            seen_canonicals.add(canonical_id)
            retained.append(canonical_id)
        return tuple(retained)

    def fingerprint(self) -> str:
        """Return a stable identity for graph families and retained edges."""
        payload = {
            'canonical_by_id': sorted((int(key), int(value)) for key, value in self.canonical_by_id.items()),
            'family_by_id': sorted(
                (int(key), sorted(int(value) for value in family)) for key, family in self.family_by_id.items()
            ),
            'relations_by_id': sorted(
                (int(key), sorted((int(target), relation) for target, relation in values))
                for key, values in self.relations_by_id.items()
            ),
        }
        return sha256(msgspec.json.encode(payload)).hexdigest()


def build_relationship_index(
    anime_ids: Sequence[int],
    relations: Mapping[int, Sequence[tuple[int, str]]],
    *,
    max_depth: int | None = None,
    manual_relationships: Mapping[int, Sequence[int]] | None = None,
    anime_types: Mapping[int, str | None] | None = None,
) -> RelationshipIndex:
    """Precompute bounded same-story families once for all catalogue IDs."""
    if max_depth is not None and max_depth < 0:
        raise ValueError('max_depth must be non-negative')
    strong_adjacency = _strong_adjacency(_with_manual_relationships(relations, manual_relationships))
    if max_depth is None:
        return _build_component_index(anime_ids, strong_adjacency, relations, anime_types)
    families: dict[int, frozenset[int]] = {}
    canonical_by_id: dict[int, int] = {}
    non_origin_ids = _non_origin_ids(relations)

    def _canonical_key(member_id: int) -> tuple[int, int, int]:
        return _canonical_sort_key(member_id, anime_types, non_origin_ids)

    for anime_id in sorted(set(anime_ids)):
        family = _family(anime_id, strong_adjacency, max_depth)
        families[anime_id] = family
        canonical_by_id[anime_id] = min(family, key=_canonical_key)
    return RelationshipIndex(families, canonical_by_id, _with_manual_relationships(relations, manual_relationships))


def anime_relations(entries: Sequence[TenraiAnimeEntry]) -> dict[int, tuple[tuple[int, str], ...]]:
    """Project retained Tenrai relations to anime targets for graph traversal."""
    return {
        entry.mal_id: tuple(
            (target.mal_id, relation.relation)
            for relation in entry.relations
            for target in relation.entry
            if target.type and target.type.lower() == 'anime'
        )
        for entry in entries
    }


def add_manual_relationships(
    relations: Mapping[int, Sequence[tuple[int, str]]],
    relationships: Mapping[int, Sequence[int]],
) -> RelationMap:
    """Add symmetric manual family edges from source IDs to related IDs."""
    return _with_manual_relationships(relations, relationships)


def load_relationship_index(
    full_artifact: Path,
    anime_ids: Sequence[int],
    *,
    max_depth: int | None = None,
) -> RelationshipIndex:
    """Load a complete full-detail artifact before graph cleanup."""
    if not full_artifact.is_file():
        raise FileNotFoundError(f'full-detail artifact does not exist: {full_artifact}')
    entries = read_json(full_artifact, list[TenraiAnimeEntry])
    requested = frozenset(anime_ids)
    covered = frozenset(entry.mal_id for entry in entries)
    missing = requested - covered
    if missing:
        raise ValueError(f'full-detail artifact is incomplete; missing IDs: {sorted(missing)}')
    return build_relationship_index(tuple(requested), anime_relations(entries), max_depth=max_depth)


def _with_manual_relationships(
    relations: Mapping[int, Sequence[tuple[int, str]]],
    relationships: Mapping[int, Sequence[int]] | None,
) -> RelationMap:
    merged: dict[int, list[tuple[int, str]]] = {source: list(targets) for source, targets in relations.items()}
    for source, targets in (relationships or {}).items():
        for target in targets:
            if source == target:
                raise ValueError(f'manual relationship cannot connect an ID to itself: {source}')
            if _has_strong_relation(merged, source, target):
                continue
            merged.setdefault(source, []).append((target, MANUAL_RELATION))
            merged.setdefault(target, []).append((source, MANUAL_RELATION))
    return {source: tuple(dict.fromkeys(targets)) for source, targets in merged.items()}


def _has_strong_relation(
    relations: Mapping[int, Sequence[tuple[int, str]]],
    left: int,
    right: int,
) -> bool:
    return any(
        target == right and relation in STRONG_SAME_STORY_RELATIONS for target, relation in relations.get(left, ())
    ) or any(
        target == left and relation in STRONG_SAME_STORY_RELATIONS for target, relation in relations.get(right, ())
    )


def _family(
    anime_id: int,
    adjacency: Mapping[int, frozenset[int]],
    max_depth: int,
) -> frozenset[int]:
    seen = {anime_id}
    queue = deque([(anime_id, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for target in adjacency.get(current, frozenset()):
            if target in seen:
                continue
            seen.add(target)
            queue.append((target, depth + 1))
    return frozenset(seen)


def _build_component_index(
    anime_ids: Sequence[int],
    adjacency: Mapping[int, frozenset[int]],
    relations: Mapping[int, Sequence[tuple[int, str]]],
    anime_types: Mapping[int, str | None] | None,
) -> RelationshipIndex:
    """Build exact requested-ID families through relation-only bridge nodes."""
    ids = set(anime_ids)
    undirected: dict[int, set[int]] = {anime_id: set() for anime_id in ids}
    for source, targets in adjacency.items():
        undirected.setdefault(source, set())
        for target in targets:
            undirected.setdefault(target, set())
            undirected[source].add(target)
            undirected[target].add(source)
    families: dict[int, frozenset[int]] = {}
    canonical_by_id: dict[int, int] = {}
    non_origin_ids = _non_origin_ids(relations)
    unvisited = set(ids)
    while unvisited:
        root = unvisited.pop()
        component: set[int] = set()
        queue = [root]
        while queue:
            current = queue.pop()
            if current in component:
                continue
            component.add(current)
            queue.extend(target for target in undirected[current] if target not in component)
        unvisited.difference_update(component)
        family = frozenset(component.intersection(ids))
        if not family:
            continue

        def _canonical_key(anime_id: int) -> tuple[int, int, int]:
            return _canonical_sort_key(anime_id, anime_types, non_origin_ids)

        canonical = min(family, key=_canonical_key)
        for anime_id in family:
            families[anime_id] = family
            canonical_by_id[anime_id] = canonical
    return RelationshipIndex(
        families,
        canonical_by_id,
        {source: tuple(targets) for source, targets in relations.items()},
    )


def _canonical_sort_key(
    anime_id: int,
    anime_types: Mapping[int, str | None] | None,
    non_origin_ids: frozenset[int],
) -> tuple[int, int, int]:
    """Prefer relation-proven origins, then primary TV entries, deterministically."""
    anime_type = (anime_types or {}).get(anime_id)
    priority = {'TV': 0, 'Movie': 1, 'ONA': 2, 'OVA': 3, 'Special': 4}.get(anime_type or '', 5)
    return priority, int(anime_id in non_origin_ids), anime_id


def _non_origin_ids(relations: Mapping[int, Sequence[tuple[int, str]]]) -> frozenset[int]:
    """Identify entries explicitly represented as sequels, summaries, or full stories."""
    non_origin: set[int] = set()
    for source_id, targets in relations.items():
        for target_id, relation in targets:
            if relation in {'Prequel', 'Full Story'}:
                non_origin.add(source_id)
            elif relation in {'Sequel', 'Summary', 'Alternative Version'}:
                non_origin.add(target_id)
    return frozenset(non_origin)


def _strong_adjacency(
    relations: Mapping[int, Sequence[tuple[int, str]]],
) -> dict[int, frozenset[int]]:
    spin_off_pairs = {
        frozenset((source, target))
        for source, targets in relations.items()
        for target, relation in targets
        if relation == 'Spin-Off'
    }
    adjacency: dict[int, set[int]] = {}
    for source, targets in relations.items():
        strong_targets = adjacency.setdefault(source, set())
        strong_targets.update(
            target
            for target, relation in targets
            if (
                relation in STRONG_SAME_STORY_RELATIONS
                and not (relation == 'Parent Story' and frozenset((source, target)) in spin_off_pairs)
            )
            or relation == MANUAL_RELATION
        )
    return {source: frozenset(targets) for source, targets in adjacency.items()}
