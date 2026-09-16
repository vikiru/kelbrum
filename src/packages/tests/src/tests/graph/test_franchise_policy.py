from graph import GraphNode, GraphRelation, RelationType, build_relationship_index


def test_franchise_membership_can_span_separate_story_families() -> None:
    nodes = tuple(GraphNode(anime_id, media_type) for anime_id, media_type in ((1, 'TV'), (2, 'TV'), (3, 'Movie')))
    relations = {
        1: (GraphRelation(2, RelationType.SPIN_OFF),),
        2: (GraphRelation(3, RelationType.SEQUEL),),
    }

    index = build_relationship_index(nodes, relations)

    assert index.family_for(1) == frozenset({1})
    assert index.family_for(2) == frozenset({2, 3})
    assert index.franchise_for(1) == frozenset({1, 2, 3})
    assert index.franchise_for(3) == frozenset({1, 2, 3})
