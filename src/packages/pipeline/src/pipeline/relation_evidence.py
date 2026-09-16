"""Normalize source relation evidence before graph policy is applied."""

from collections.abc import Sequence

import msgspec

from fetch.contracts import TenraiAnimeEntry
from graph import GraphRelation, RelationType


class DanglingRelation(msgspec.Struct, frozen=True):
    """Relation evidence whose target is outside the active catalogue."""

    source_id: int
    target_id: int
    relation: RelationType
    target_name: str | None = None


class RelationEvidenceAudit(msgspec.Struct, frozen=True):
    """Evidence counts and omitted targets from one relation normalization pass."""

    source_count: int
    accepted_edge_count: int
    dangling_relations: tuple[DanglingRelation, ...] = ()

    @property
    def dangling_count(self) -> int:
        return len(self.dangling_relations)


class NormalizedRelationEvidence(msgspec.Struct, frozen=True):
    """Normalized graph inputs plus diagnostics produced by the source adapter."""

    relations: dict[int, tuple[GraphRelation, ...]]
    audit: RelationEvidenceAudit


def normalize_relation_evidence(
    entries: Sequence[TenraiAnimeEntry],
    known_ids: set[int],
) -> NormalizedRelationEvidence:
    """Convert Tenrai relation groups into catalogue-scoped graph evidence."""
    normalized: dict[int, tuple[GraphRelation, ...]] = {}
    dangling: list[DanglingRelation] = []
    accepted_edge_count = 0
    for entry in entries:
        relations: list[GraphRelation] = []
        for relation_group in entry.relations:
            relation_type = _relation_type(relation_group.relation)
            for target in relation_group.entry:
                if target.type is None or target.type.casefold() != 'anime' or target.mal_id == entry.mal_id:
                    continue
                if target.mal_id not in known_ids:
                    dangling.append(DanglingRelation(entry.mal_id, target.mal_id, relation_type, target.name))
                    continue
                relation = GraphRelation(target.mal_id, relation_type)
                if relation not in relations:
                    relations.append(relation)
                    accepted_edge_count += 1
        normalized[entry.mal_id] = tuple(relations)
    return NormalizedRelationEvidence(
        normalized,
        RelationEvidenceAudit(len(entries), accepted_edge_count, tuple(dangling)),
    )


def _relation_type(value: str) -> RelationType:
    """Map source relation labels into the graph vocabulary."""
    try:
        return RelationType(value)
    except ValueError:
        return RelationType.OTHER
