import json
from pathlib import Path

import pytest

from fetch.contracts import AnimeRelation, RelationEntry, TenraiAnimeEntry
from graph import GraphNode, GraphRelation, ManualEdgePolicy, SameStoryIntent, TraversalMode, build_relationship_index
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
    assert second.index.same_story_exclusions(1) == frozenset({1, 2})
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


def test_graph_cache_is_rebuilt_when_media_type_changes(tmp_path: Path) -> None:
    full_artifact = tmp_path / 'full.json'
    graph_path = tmp_path / 'graph.json'
    write_json(
        full_artifact,
        (
            TenraiAnimeEntry(mal_id=1, title='Origin'),
            TenraiAnimeEntry(mal_id=2, title='Continuation'),
        ),
    )

    tv_graph = load_or_build_relationship_graph(full_artifact, graph_path, (1, 2), {1: 'TV', 2: 'MOVIE'})
    movie_graph = load_or_build_relationship_graph(full_artifact, graph_path, (1, 2), {1: 'MOVIE', 2: 'TV'})

    assert tv_graph.index.fingerprint() != movie_graph.index.fingerprint()
    assert movie_graph.index.media_type_by_id == {1: 'MOVIE', 2: 'TV'}


def test_explicit_manual_traversal_none_is_preserved() -> None:
    graph = build_relationship_index(
        (GraphNode(1), GraphNode(2), GraphNode(3)),
        {},
        manual_relationships={1: (2,), 2: (3,)},
        manual_edge_policies=(
            ManualEdgePolicy(
                1, 2, SameStoryIntent.CONTINUATION, 'direct only', 'test', traversal_mode=TraversalMode.NONE
            ),
            ManualEdgePolicy(
                2, 3, SameStoryIntent.CONTINUATION, 'direct only', 'test', traversal_mode=TraversalMode.NONE
            ),
        ),
    )

    assert graph.same_story_exclusions(1) == frozenset({1})


def test_corrupt_graph_cache_is_rebuilt(tmp_path: Path) -> None:
    full_artifact = tmp_path / 'full.json'
    graph_path = tmp_path / 'graph.json'
    write_json(full_artifact, (TenraiAnimeEntry(mal_id=1, title='Origin'),))
    graph_path.write_text('{corrupt', encoding='utf-8')

    result = load_or_build_relationship_graph(full_artifact, graph_path, (1,), {1: 'TV'})

    assert result.index.same_story_exclusions(1) == frozenset({1})


def test_stale_graph_cache_is_rejected_on_incompatible_schema_or_graph_or_ids(tmp_path: Path) -> None:
    full_artifact = tmp_path / 'full.json'
    graph_path = tmp_path / 'graph.json'
    write_json(full_artifact, (TenraiAnimeEntry(mal_id=1, title='Origin'),))
    load_or_build_relationship_graph(full_artifact, graph_path, (1,), {1: 'TV'})

    # 1. Incompatible schema version
    with graph_path.open() as f:
        cache_data = json.load(f)
    cache_data['schema_version'] = 'relationship-graph-v0-outdated'
    with graph_path.open('w') as f:
        json.dump(cache_data, f)
    res_schema = load_or_build_relationship_graph(full_artifact, graph_path, (1,), {1: 'TV'})
    assert res_schema.index.same_story_policy_version == 'same-story-v1'

    # 2. Changed anime_ids (catalogue drift)
    res_drift = load_or_build_relationship_graph(full_artifact, graph_path, (1, 2), {1: 'TV', 2: 'TV'})
    assert res_drift.index.same_story_exclusions(1) == frozenset({1})
