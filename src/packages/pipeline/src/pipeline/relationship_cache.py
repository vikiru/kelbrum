"""Load, validate, and persist the catalogue relationship graph."""

from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path

import msgspec

from models.tenrai import TenraiAnimeEntry
from recommender.manual_relationships import MANUAL_RELATIONSHIPS
from recommender.relationship_graph import RelationshipIndex, anime_relations, build_relationship_index
from storage.json_io import read_json, write_json

RELATIONSHIP_GRAPH_SCHEMA_VERSION = 'relationship-graph-v3'
RELATIONSHIP_POLICY_VERSION = 'strong-same-story-plus-manual-v2-origin-aware'


class RelationshipGraphArtifacts(msgspec.Struct, frozen=True):
    """Relationship data required by downstream recommendation construction."""

    index: RelationshipIndex
    relations: Mapping[int, Sequence[tuple[int, str]]]


def load_or_build_relationship_graph(
    full_artifact: Path,
    graph_path: Path,
    anime_ids: Sequence[int],
    anime_types: Mapping[int, str | None],
) -> RelationshipGraphArtifacts:
    """Reuse a valid graph cache or build and persist the current graph identity."""
    entries = read_json(full_artifact, list[TenraiAnimeEntry])
    relations = anime_relations(entries)
    ordered_ids = tuple(anime_ids)
    graph = _load_graph_cache(graph_path, ordered_ids, full_artifact)
    if graph is None:
        graph = build_relationship_index(
            ordered_ids,
            relations,
            manual_relationships=MANUAL_RELATIONSHIPS,
            anime_types=anime_types,
        )
        _write_graph_cache(graph_path, graph, ordered_ids, full_artifact)
    return RelationshipGraphArtifacts(graph, relations)


def _load_graph_cache(path: Path, anime_ids: Sequence[int], source_path: Path) -> RelationshipIndex | None:
    if not path.is_file():
        return None
    try:
        payload = read_json(path, dict[str, object])
        if payload.get('schema_version') != RELATIONSHIP_GRAPH_SCHEMA_VERSION:
            return None
        if payload.get('anime_ids') != list(anime_ids):
            return None
        if payload.get('source_sha256') != _sha256_file(source_path):
            return None
        if payload.get('build_identity') != _graph_build_identity(anime_ids):
            return None
        if payload.get('max_depth') is not None:
            return None
        canonical = payload['canonical_by_id']
        families = payload['family_by_id']
        relation_payload = payload.get('relations_by_id', {})
        if not isinstance(canonical, dict) or not isinstance(families, dict) or not isinstance(relation_payload, dict):
            return None
        relations_by_id = _decode_relations(relation_payload)
        return RelationshipIndex(
            canonical_by_id={int(key): int(value) for key, value in canonical.items()},
            family_by_id={int(key): frozenset(int(item) for item in value) for key, value in families.items()},
            relations_by_id=relations_by_id,
        )
    except (KeyError, TypeError, ValueError):
        return None


def _decode_relations(payload: dict[object, object]) -> dict[int, tuple[tuple[int, str], ...]]:
    relations_by_id: dict[int, tuple[tuple[int, str], ...]] = {}
    for key, values in payload.items():
        if not isinstance(key, str) or not isinstance(values, list):
            raise TypeError('relationship cache contains invalid relation data')
        decoded: list[tuple[int, str]] = []
        for item in values:
            if not isinstance(item, dict):
                raise TypeError('relationship cache contains an invalid relation')
            target_id = item.get('target_id')
            relation = item.get('relation')
            if not isinstance(target_id, int) or not isinstance(relation, str):
                raise TypeError('relationship cache contains an invalid relation')
            decoded.append((target_id, relation))
        relations_by_id[int(key)] = tuple(decoded)
    return relations_by_id


def _write_graph_cache(
    path: Path,
    graph: RelationshipIndex,
    anime_ids: Sequence[int],
    source_path: Path,
) -> None:
    write_json(
        path,
        {
            'schema_version': RELATIONSHIP_GRAPH_SCHEMA_VERSION,
            'anime_ids': list(anime_ids),
            'source_sha256': _sha256_file(source_path),
            'build_identity': _graph_build_identity(anime_ids),
            'max_depth': None,
            'canonical_by_id': {str(key): value for key, value in graph.canonical_by_id.items()},
            'family_by_id': {str(key): sorted(value) for key, value in graph.family_by_id.items()},
            'relations_by_id': {
                str(key): [{'target_id': target, 'relation': relation} for target, relation in values]
                for key, values in graph.relations_by_id.items()
            },
        },
    )


def _graph_build_identity(anime_ids: Sequence[int]) -> str:
    payload = {
        'schema_version': RELATIONSHIP_GRAPH_SCHEMA_VERSION,
        'anime_ids': list(anime_ids),
        'max_depth': None,
        'relation_policy': RELATIONSHIP_POLICY_VERSION,
        'manual_relationships': sorted(
            (int(source), sorted(int(target) for target in targets)) for source, targets in MANUAL_RELATIONSHIPS.items()
        ),
    }
    return sha256(msgspec.json.encode(payload)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()
