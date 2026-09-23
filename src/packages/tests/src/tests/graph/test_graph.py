import pytest

from graph import (
    GraphNode,
    GraphRelation,
    RelationshipIndex,
    RelationshipScope,
    RelationType,
    add_manual_relationships,
    build_relationship_index,
)
from graph.registry import manual_relationships_identity


def test_builds_same_story_family_and_canonicalizes_candidates() -> None:
    index = build_relationship_index(
        (GraphNode(1, 'TV'), GraphNode(2, 'Movie'), GraphNode(3, 'ONA')),
        {
            1: (GraphRelation(2, RelationType.SEQUEL),),
            2: (GraphRelation(1, RelationType.PREQUEL), GraphRelation(3, RelationType.SEQUEL)),
            3: (GraphRelation(2, RelationType.PREQUEL),),
        },
    )

    assert index.canonical_id(2) == 1
    assert index.family_for(3) == frozenset({1, 2, 3})
    assert index.is_same_story(3, 1)
    assert not index.is_same_story(3, 4)
    assert index.excluded_ids(3) == frozenset({1, 2, 3})
    assert index.cleanup(1, (1, 2, 3)) == ()


def test_queries_franchise_entries_by_scope_and_media_type() -> None:
    index = build_relationship_index(
        (GraphNode(1, 'TV'), GraphNode(2, 'TV'), GraphNode(3, 'Movie'), GraphNode(4, 'ONA')),
        {
            1: (GraphRelation(2, RelationType.SEQUEL), GraphRelation(3, RelationType.SPIN_OFF)),
            2: (GraphRelation(1, RelationType.PREQUEL),),
            3: (GraphRelation(1, RelationType.PARENT_STORY), GraphRelation(4, RelationType.SEQUEL)),
            4: (GraphRelation(3, RelationType.PREQUEL),),
        },
    )

    assert index.entries_for(1) == (1, 2, 3, 4)
    assert index.entries_for(1, media_type='TV') == (1, 2)
    assert index.entries_for(1, media_type='movie') == (3,)
    assert index.entries_for(1, scope=RelationshipScope.STORY) == (1, 2)
    assert index.entries_for(1, scope=RelationshipScope.STORY, media_type='ONA') == ()


def test_relation_only_bridge_connects_requested_nodes() -> None:
    index = build_relationship_index(
        (GraphNode(10, 'TV'), GraphNode(12, 'ONA')),
        {
            10: (GraphRelation(11, RelationType.SEQUEL),),
            11: (GraphRelation(10, RelationType.PREQUEL), GraphRelation(12, RelationType.SEQUEL)),
            12: (GraphRelation(11, RelationType.PREQUEL),),
        },
    )

    assert index.excluded_ids(12) == frozenset({10, 12})
    assert index.canonical_id(12) == 10


def test_origin_movie_beats_non_origin_movie_without_tv_entry() -> None:
    index = build_relationship_index(
        (GraphNode(20, 'Movie'), GraphNode(1, 'Movie')),
        {
            20: (GraphRelation(1, RelationType.PREQUEL),),
            1: (GraphRelation(20, RelationType.SEQUEL),),
        },
    )

    assert index.canonical_id(20) == 1


def test_primary_media_type_beats_origin_status_for_representative_selection() -> None:
    index = build_relationship_index(
        (GraphNode(1, 'TV'), GraphNode(2, 'Movie')),
        {
            1: (GraphRelation(2, RelationType.ALTERNATIVE_VERSION),),
            2: (GraphRelation(1, RelationType.ALTERNATIVE_VERSION),),
        },
    )

    assert index.canonical_id(1) == 1
    assert index.canonical_id(2) == 1
    assert index.canonical_id(1) == 1


def test_representative_selection_is_invariant_to_node_and_relation_order() -> None:
    nodes = (GraphNode(1, 'TV'), GraphNode(2, 'Movie'), GraphNode(3, 'ONA'), GraphNode(4, 'TV'))
    relations = {
        1: (GraphRelation(2, RelationType.SEQUEL), GraphRelation(4, RelationType.SPIN_OFF)),
        2: (GraphRelation(1, RelationType.PREQUEL), GraphRelation(3, RelationType.SEQUEL)),
        3: (GraphRelation(2, RelationType.PREQUEL),),
        4: (GraphRelation(1, RelationType.SPIN_OFF),),
    }
    expected = build_relationship_index(nodes, relations)

    for node_order in (tuple(reversed(nodes)), tuple(nodes[index] for index in (2, 0, 3, 1))):
        shuffled_relations = {
            source: tuple(reversed(targets)) for source, targets in reversed(tuple(relations.items()))
        }
        actual = build_relationship_index(node_order, shuffled_relations)
        assert actual.canonical_by_id == expected.canonical_by_id
        assert actual.fingerprint() == expected.fingerprint()


def test_invalid_graph_inputs_fail_before_construction() -> None:
    with pytest.raises(ValueError, match='duplicate graph node'):
        build_relationship_index((GraphNode(1), GraphNode(1)), {})

    with pytest.raises(ValueError, match='cannot connect an ID to itself'):
        build_relationship_index((GraphNode(1),), {1: (GraphRelation(1, RelationType.SEQUEL),)})

    with pytest.raises(ValueError, match='duplicate graph relation'):
        build_relationship_index(
            (GraphNode(1), GraphNode(2)),
            {1: (GraphRelation(2, RelationType.SEQUEL), GraphRelation(2, RelationType.SEQUEL))},
        )


def test_manual_relationships_are_symmetric_and_reject_self_links() -> None:
    merged = add_manual_relationships({}, {1: (2,)})

    assert merged[1] == (GraphRelation(2, RelationType.MANUAL),)
    assert merged[2] == (GraphRelation(1, RelationType.MANUAL),)

    with pytest.raises(ValueError, match='itself'):
        add_manual_relationships({}, {1: (1,)})


def test_manual_registry_identity_changes_with_registry_content() -> None:
    assert manual_relationships_identity({1: (2,)}) != manual_relationships_identity({1: (3,)})

    with pytest.raises(ValueError, match='duplicate manual relationship'):
        manual_relationships_identity({1: (2, 2)})


def test_cleanup_removes_anchor_family_and_deduplicates_canonical_ids() -> None:
    index = build_relationship_index(
        (GraphNode(1), GraphNode(2), GraphNode(3), GraphNode(4)),
        {
            1: (GraphRelation(2, RelationType.SEQUEL),),
            2: (GraphRelation(1, RelationType.PREQUEL),),
            3: (GraphRelation(4, RelationType.SEQUEL),),
            4: (GraphRelation(3, RelationType.PREQUEL),),
        },
    )

    assert index.cleanup(1, (1, 2, 3, 4)) == (3,)


def test_relationship_index_rejects_misaligned_canonical_families() -> None:
    with pytest.raises(ValueError, match='cover the same nodes'):
        RelationshipIndex(
            family_by_id={1: frozenset({1})},
            canonical_by_id={},
        )

    with pytest.raises(ValueError, match='outside its relationship family'):
        RelationshipIndex(
            family_by_id={1: frozenset({1})},
            canonical_by_id={1: 2},
        )
