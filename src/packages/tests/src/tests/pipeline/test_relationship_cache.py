from pathlib import Path

import pytest

from fetch.contracts import AnimeRelation, RelationEntry, TenraiAnimeEntry
from graph import GraphRelation
from pipeline.relationship_cache import load_or_build_relationship_graph
from storage.json_io import write_json


def test_graph_cache_round_trip_preserves_identity_and_relations(tmp_path: Path) -> None:
    entries = (
        TenraiAnimeEntry(
            mal_id=1,
            title='Origin',
            relations=[AnimeRelation('Sequel', [RelationEntry(mal_id=2, type='anime')])],
        ),
        TenraiAnimeEntry(
            mal_id=2,
            title='Continuation',
            relations=[AnimeRelation('Prequel', [RelationEntry(mal_id=1, type='anime')])],
        ),
    )
    full_artifact = tmp_path / 'full.json'
    graph_path = tmp_path / 'graph.json'
    write_json(full_artifact, entries)

    first = load_or_build_relationship_graph(full_artifact, graph_path, (1, 2), {1: 'TV', 2: 'TV'})
    second = load_or_build_relationship_graph(full_artifact, graph_path, (1, 2), {1: 'TV', 2: 'TV'})

    assert first.index.fingerprint() == second.index.fingerprint()
    assert second.index.excluded_ids(1) == frozenset({1, 2})
    assert second.evidence_audit.source_count == 2
    assert second.evidence_audit.accepted_edge_count == 2
    assert second.evidence_audit.dangling_count == 0


def test_graph_cache_hit_does_not_decode_full_catalogue(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    entries = (TenraiAnimeEntry(mal_id=1, title='Origin'),)
    full_artifact = tmp_path / 'full.json'
    graph_path = tmp_path / 'graph.json'
    write_json(full_artifact, entries)
    load_or_build_relationship_graph(full_artifact, graph_path, (1,), {1: 'TV'})

    def fail_decode(_: object) -> dict[int, tuple[GraphRelation, ...]]:
        raise AssertionError('cache hit decoded the full catalogue')

    monkeypatch.setattr('pipeline.relationship_cache.normalize_relation_evidence', fail_decode)
    load_or_build_relationship_graph(full_artifact, graph_path, (1,), {1: 'TV'})


def test_corrupt_graph_cache_is_rebuilt(tmp_path: Path) -> None:
    full_artifact = tmp_path / 'full.json'
    graph_path = tmp_path / 'graph.json'
    write_json(full_artifact, (TenraiAnimeEntry(mal_id=1, title='Origin'),))
    graph_path.write_text('{corrupt', encoding='utf-8')

    result = load_or_build_relationship_graph(full_artifact, graph_path, (1,), {1: 'TV'})

    assert result.index.excluded_ids(1) == frozenset({1})
