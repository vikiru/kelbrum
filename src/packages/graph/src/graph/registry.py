"""Validated, graph-owned curated relationship resources loaded from CSV."""

import csv
from collections.abc import Mapping, Sequence
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import orjson

from config.manual_data import MANUAL_RELATIONSHIPS_CSV_PATH
from graph.contracts import (
    GraphRelation,
    IdentityEquivalenceAssertion,
    IdentityIntent,
    ManualEdgePolicy,
    ManualRelationshipRow,
    RelationMap,
    RelationType,
    SameStoryIntent,
    TraversalMode,
)
from graph.policies import MANUAL_RELATION, STRONG_SAME_STORY_RELATIONS

MANUAL_RELATIONSHIPS_VERSION = 'manual-relations-csv-v1'

IDENTITY_EQUIVALENCE_REGISTRY: tuple[IdentityEquivalenceAssertion, ...] = ()
SAME_STORY_EDGE_OVERRIDES: dict[tuple[int, int, RelationType], SameStoryIntent] = {}


def load_manual_relationships(
    path: Path = MANUAL_RELATIONSHIPS_CSV_PATH,
) -> tuple[ManualRelationshipRow, ...]:
    """Load curated relationship rows from the first-class CSV source."""
    if not path.is_file():
        return ()
    rows: list[ManualRelationshipRow] = []
    with path.open(newline='', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)
        required = {'source_id', 'target_id', 'same_story_intent', 'traversal_mode', 'identity_intent'}
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError(f'manual relations CSV missing required columns: {path}')
        for row in reader:
            source_id = int(row['source_id'])
            target_id = int(row['target_id'])
            if source_id <= 0 or target_id <= 0 or source_id == target_id:
                raise ValueError(f'invalid endpoints in manual relations CSV: {source_id} -> {target_id}')
            intent_str = row['same_story_intent'].strip().replace('_', '-')
            traversal_str = row['traversal_mode'].strip().replace('_', '-')
            identity_str = row['identity_intent'].strip().replace('_', '-')
            rows.append(
                ManualRelationshipRow(
                    source_id=source_id,
                    source_title=row.get('source_title', '').strip(),
                    target_id=target_id,
                    target_title=row.get('target_title', '').strip(),
                    relation_type=row.get('relation_type', 'Manual').strip(),
                    same_story_intent=SameStoryIntent(intent_str),
                    traversal_mode=TraversalMode(traversal_str),
                    identity_intent=IdentityIntent(identity_str),
                    provenance=row.get('provenance', 'manual').strip(),
                )
            )
    return tuple(rows)


def manual_relationships_csv_hash(path: Path = MANUAL_RELATIONSHIPS_CSV_PATH) -> str:
    """Return SHA256 of the manual relations CSV file, or empty string if missing."""
    if not path.is_file():
        return ''
    return sha256(path.read_bytes()).hexdigest()


def manual_relationships_to_policies(
    rows: Sequence[ManualRelationshipRow],
) -> tuple[ManualEdgePolicy, ...]:
    """Convert parsed CSV rows to graph ManualEdgePolicy instances."""
    return tuple(
        ManualEdgePolicy(
            source_id=row.source_id,
            target_id=row.target_id,
            same_story_intent=row.same_story_intent,
            rationale=row.provenance,
            provenance=row.provenance,
            identity_intent=row.identity_intent,
            traversal_mode=row.traversal_mode,
            relation_type=(
                RelationType.MANUAL if row.relation_type.casefold() == 'manual' else RelationType(row.relation_type)
            ),
        )
        for row in rows
    )


def manual_relationships_to_dict(
    rows: Sequence[ManualRelationshipRow],
) -> dict[int, tuple[int, ...]]:
    """Convert parsed CSV rows into adjacency mapping for manual raw edges."""
    adjacency: dict[int, list[int]] = {}
    for row in rows:
        adjacency.setdefault(row.source_id, []).append(row.target_id)
    return {source: tuple(sorted(targets)) for source, targets in adjacency.items()}


@lru_cache(maxsize=1)
def _default_manual_relationship_rows() -> tuple[ManualRelationshipRow, ...]:
    return load_manual_relationships()


@lru_cache(maxsize=1)
def get_manual_relationships() -> dict[int, tuple[int, ...]]:
    """Lazily load and cache the default manual relationships adjacency mapping."""
    return manual_relationships_to_dict(_default_manual_relationship_rows())


@lru_cache(maxsize=1)
def get_typed_manual_edge_policies() -> tuple[ManualEdgePolicy, ...]:
    """Lazily load and cache the default typed manual edge policies."""
    return manual_relationships_to_policies(_default_manual_relationship_rows())


def validate_manual_relationships(relationships: Mapping[int, Sequence[int]]) -> None:
    """Reject malformed, self-referential, or duplicate curated edges."""
    for source, targets in relationships.items():
        if source <= 0:
            raise ValueError(f'manual relationship source must be positive: {source}')
        seen: set[int] = set()
        for target in targets:
            if target <= 0:
                raise ValueError(f'manual relationship target must be positive: {target}')
            if source == target:
                raise ValueError(f'manual relationship cannot connect an ID to itself: {source}')
            if target in seen:
                raise ValueError(f'duplicate manual relationship: {source} → {target}')
            seen.add(target)


def manual_relationships_identity(
    relationships: Mapping[int, Sequence[int]] | None = None,
    *,
    csv_path: Path = MANUAL_RELATIONSHIPS_CSV_PATH,
) -> str:
    """Return a deterministic identity for the validated curated registry and CSV."""
    active_relationships = get_manual_relationships() if relationships is None else relationships
    validate_manual_relationships(active_relationships)
    payload = sorted((source, sorted(targets)) for source, targets in active_relationships.items())
    csv_hash = manual_relationships_csv_hash(csv_path)
    return sha256(
        orjson.dumps((MANUAL_RELATIONSHIPS_VERSION, csv_hash, payload), option=orjson.OPT_SORT_KEYS)
    ).hexdigest()


def add_manual_relationships(
    relations: Mapping[int, Sequence[GraphRelation]],
    relationships: Mapping[int, Sequence[int]],
) -> RelationMap:
    """Merge validated symmetric manual family edges into normalized relations."""
    validate_manual_relationships(relationships)
    merged: dict[int, list[GraphRelation]] = {source: list(targets) for source, targets in relations.items()}
    manual_pairs = {frozenset((source, target)) for source, targets in relationships.items() for target in targets}
    for source, targets in relationships.items():
        for target in targets:
            relation = GraphRelation(target, MANUAL_RELATION)
            reverse = GraphRelation(source, MANUAL_RELATION)
            is_manual_pair = frozenset((source, target)) in manual_pairs
            if (
                is_manual_pair or not _has_strong_relation(merged, source, target)
            ) and relation not in merged.setdefault(source, []):
                merged[source].append(relation)
            if (
                is_manual_pair or not _has_strong_relation(merged, target, source)
            ) and reverse not in merged.setdefault(target, []):
                merged[target].append(reverse)
    return {source: tuple(targets) for source, targets in merged.items()}


def _has_strong_relation(relations: Mapping[int, Sequence[GraphRelation]], left: int, right: int) -> bool:
    return any(
        relation.target_id == right and relation.relation in STRONG_SAME_STORY_RELATIONS
        for relation in relations.get(left, ())
    ) or any(
        relation.target_id == left and relation.relation in STRONG_SAME_STORY_RELATIONS
        for relation in relations.get(right, ())
    )
