"""Load, validate, and persist the catalogue relationship graph."""

from collections.abc import Mapping, Sequence
from pathlib import Path

import msgspec

from config import LogEvent, bind_logger, derive_payload_identity, derive_stage_identity, emit_event
from fetch.contracts import TenraiAnimeEntry
from graph import (
    MANUAL_RELATIONSHIPS,
    GraphNode,
    GraphRelation,
    RelationshipIndex,
    RelationType,
    build_relationship_index,
)
from pipeline.relation_evidence import DanglingRelation, RelationEvidenceAudit, normalize_relation_evidence
from storage.errors import StorageError
from storage.hashing import sha256_file
from storage.json_io import read_json, write_json

RELATIONSHIP_GRAPH_SCHEMA_VERSION = 'relationship-graph-v6'
RELATIONSHIP_POLICY_DESCRIPTOR = {
    'same_story': 'canonical-strong-component',
    'franchise': 'all-relation-types',
    'manual_relations': 'explicit-graph-relations',
    'max_depth': None,
}
log = bind_logger(package='pipeline', stage='relationship-graph')


class RelationshipGraphArtifacts(msgspec.Struct, frozen=True):
    """Relationship index produced for downstream recommendation construction."""

    index: RelationshipIndex
    evidence_audit: RelationEvidenceAudit = msgspec.field(default_factory=lambda: RelationEvidenceAudit(0, 0))


def load_or_build_relationship_graph(
    full_artifact: Path,
    graph_path: Path,
    anime_ids: Sequence[int],
    anime_types: Mapping[int, str | None],
    run_id: str = '-',
) -> RelationshipGraphArtifacts:
    """Reuse a valid graph cache or build and persist the current graph identity."""
    ordered_ids = tuple(anime_ids)
    cached = _load_graph_cache(graph_path, ordered_ids, full_artifact)
    if cached is None:
        entries = read_json(full_artifact, list[TenraiAnimeEntry])
        evidence = normalize_relation_evidence(entries, set(ordered_ids))
        relations = evidence.relations
        emit_event(
            log,
            LogEvent(
                event_name='cache.decision',
                package='pipeline',
                stage='relationship-graph',
                run_id=run_id,
                cache_decision='rebuilt',
                cache_reason='missing-or-invalid',
                row_count=len(ordered_ids),
            ),
        )
        log.info('Building the relationship graph for {} records.', len(ordered_ids))
        nodes = tuple(GraphNode(anime_id, anime_types.get(anime_id)) for anime_id in ordered_ids)
        graph = build_relationship_index(
            nodes,
            relations,
            manual_relationships=MANUAL_RELATIONSHIPS,
        )
        _write_graph_cache(graph_path, graph, ordered_ids, full_artifact, evidence.audit)
        evidence_audit = evidence.audit
    else:
        graph, evidence_audit = cached
        emit_event(
            log,
            LogEvent(
                event_name='cache.decision',
                package='pipeline',
                stage='relationship-graph',
                run_id=run_id,
                cache_decision='reused',
                cache_reason='identity-and-alignment-match',
                row_count=len(ordered_ids),
            ),
        )
        log.info('Reusing the cached relationship graph for {} records.', len(ordered_ids))
    return RelationshipGraphArtifacts(graph, evidence_audit)


def _load_graph_cache(
    path: Path, anime_ids: Sequence[int], source_path: Path
) -> tuple[RelationshipIndex, RelationEvidenceAudit] | None:
    """Load a graph cache only when its source, schema, and catalogue IDs still match."""
    if not path.is_file():
        return None
    try:
        payload = read_json(path, dict[str, object])
        source_sha256 = sha256_file(source_path)
        identity_matches = (
            payload.get('schema_version') == RELATIONSHIP_GRAPH_SCHEMA_VERSION,
            payload.get('anime_ids') == list(anime_ids),
            payload.get('source_sha256') == source_sha256,
            payload.get('build_identity') == _graph_build_identity(anime_ids, source_sha256),
            payload.get('max_depth') is None,
        )
        if not all(identity_matches):
            return None
        canonical = payload['canonical_by_id']
        families = payload['family_by_id']
        franchise = payload['franchise_by_id']
        media_types = payload['media_type_by_id']
        relation_payload = payload.get('relations_by_id', {})
        if (
            not isinstance(canonical, dict)
            or not isinstance(families, dict)
            or not isinstance(franchise, dict)
            or not isinstance(media_types, dict)
            or not isinstance(relation_payload, dict)
        ):
            return None
        relations_by_id = _decode_relations(relation_payload)
        graph = RelationshipIndex(
            canonical_by_id={int(key): int(value) for key, value in canonical.items()},
            family_by_id={int(key): frozenset(int(item) for item in value) for key, value in families.items()},
            relations_by_id=relations_by_id,
            franchise_by_id={int(key): frozenset(int(item) for item in value) for key, value in franchise.items()},
            media_type_by_id={int(key): value for key, value in media_types.items()},
        )
        return graph, _decode_evidence_audit(payload.get('evidence_audit', {}))
    except (KeyError, StorageError, TypeError, ValueError):
        return None


def _decode_relations(payload: dict[object, object]) -> dict[int, tuple[GraphRelation, ...]]:
    """Decode persisted relation records into validated graph contracts."""
    relations_by_id: dict[int, tuple[GraphRelation, ...]] = {}
    for key, values in payload.items():
        if not isinstance(key, str) or not isinstance(values, list):
            raise TypeError('relationship cache contains invalid relation data')
        decoded: list[GraphRelation] = []
        for item in values:
            if not isinstance(item, dict):
                raise TypeError('relationship cache contains an invalid relation')
            target_id = item.get('target_id')
            relation = item.get('relation')
            if not isinstance(target_id, int) or not isinstance(relation, str):
                raise TypeError('relationship cache contains an invalid relation')
            try:
                relation_type = RelationType(relation)
            except ValueError as error:
                raise TypeError('relationship cache contains an unsupported relation') from error
            decoded.append(GraphRelation(target_id, relation_type))
        relations_by_id[int(key)] = tuple(decoded)
    return relations_by_id


def _decode_evidence_audit(payload: object) -> RelationEvidenceAudit:
    """Decode persisted source-evidence diagnostics."""
    if not isinstance(payload, dict):
        raise TypeError('relationship cache contains invalid evidence diagnostics')
    source_count = payload.get('source_count')
    accepted_edge_count = payload.get('accepted_edge_count')
    dangling_payload = payload.get('dangling_relations', [])
    if (
        not isinstance(source_count, int)
        or not isinstance(accepted_edge_count, int)
        or not isinstance(dangling_payload, list)
    ):
        raise TypeError('relationship cache contains invalid evidence diagnostics')
    dangling: list[DanglingRelation] = []
    for item in dangling_payload:
        if not isinstance(item, dict):
            raise TypeError('relationship cache contains invalid dangling relation')
        source_id = item.get('source_id')
        target_id = item.get('target_id')
        relation = item.get('relation')
        target_name = item.get('target_name')
        if not isinstance(source_id, int) or not isinstance(target_id, int) or not isinstance(relation, str):
            raise TypeError('relationship cache contains invalid dangling relation')
        try:
            relation_type = RelationType(relation)
        except ValueError as error:
            raise TypeError('relationship cache contains unsupported dangling relation') from error
        if target_name is not None and not isinstance(target_name, str):
            raise TypeError('relationship cache contains invalid dangling relation name')
        dangling.append(DanglingRelation(source_id, target_id, relation_type, target_name))
    return RelationEvidenceAudit(source_count, accepted_edge_count, tuple(dangling))


def _write_graph_cache(
    path: Path,
    graph: RelationshipIndex,
    anime_ids: Sequence[int],
    source_path: Path,
    evidence_audit: RelationEvidenceAudit,
) -> None:
    """Persist the graph and all identity inputs needed for a future cache hit."""
    source_sha256 = sha256_file(source_path)
    write_json(
        path,
        {
            'schema_version': RELATIONSHIP_GRAPH_SCHEMA_VERSION,
            'anime_ids': list(anime_ids),
            'source_sha256': source_sha256,
            'build_identity': _graph_build_identity(anime_ids, source_sha256),
            'max_depth': None,
            'canonical_by_id': {str(key): value for key, value in graph.canonical_by_id.items()},
            'family_by_id': {str(key): sorted(value) for key, value in graph.family_by_id.items()},
            'franchise_by_id': {str(key): sorted(value) for key, value in graph.franchise_by_id.items()},
            'media_type_by_id': {str(key): value for key, value in graph.media_type_by_id.items()},
            'relations_by_id': {
                str(key): [{'target_id': item.target_id, 'relation': item.relation.value} for item in values]
                for key, values in graph.relations_by_id.items()
            },
            'evidence_audit': {
                'source_count': evidence_audit.source_count,
                'accepted_edge_count': evidence_audit.accepted_edge_count,
                'dangling_relations': [
                    {
                        'source_id': item.source_id,
                        'target_id': item.target_id,
                        'relation': item.relation.value,
                        'target_name': item.target_name,
                    }
                    for item in evidence_audit.dangling_relations
                ],
            },
        },
    )


def _graph_build_identity(anime_ids: Sequence[int], source_identity: str) -> str:
    """Build the deterministic identity for one relationship-graph artifact."""
    return derive_stage_identity(
        'relationship-graph',
        contract_identity=RELATIONSHIP_GRAPH_SCHEMA_VERSION,
        source_identity=source_identity,
        ordered_ids=tuple(anime_ids),
        policy_identity=derive_payload_identity(RELATIONSHIP_POLICY_DESCRIPTOR),
        registry_identity=derive_payload_identity(
            sorted((source, sorted(targets)) for source, targets in MANUAL_RELATIONSHIPS.items())
        ),
        producer_identity='pipeline.relationship_cache',
    )
