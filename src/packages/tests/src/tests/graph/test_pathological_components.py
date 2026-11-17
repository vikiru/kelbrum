from collections.abc import Mapping

from graph import GraphNode, GraphRelation, RelationType, build_relationship_index


def _index(
    ids: tuple[int, ...],
    relations: dict[int, tuple[GraphRelation, ...]],
    manual: Mapping[int, tuple[int, ...]] | None = None,
):
    return build_relationship_index(
        tuple(GraphNode(anime_id) for anime_id in ids),
        relations,
        manual_relationships=manual,
    )


def test_maou_dante_crossover_parent_story_does_not_join_devilman_and_mazinger() -> None:
    index = _index(
        (2252, 2253, 3898),
        {
            3898: (
                GraphRelation(2252, RelationType.PARENT_STORY),
                GraphRelation(2253, RelationType.PARENT_STORY),
            )
        },
    )

    assert index.same_story_exclusions(2252) == frozenset({2252})
    assert index.same_story_exclusions(2253) == frozenset({2253})
    assert index.franchise_members(2252) == frozenset({2252, 3898, 2253})


def test_perman_ninja_hattori_crossover_films_do_not_join_continuation_lines() -> None:
    index = _index(
        (4936, 6303, 29233, 29235),
        {
            29233: (
                GraphRelation(4936, RelationType.PARENT_STORY),
                GraphRelation(6303, RelationType.PARENT_STORY),
            ),
            29235: (
                GraphRelation(4936, RelationType.PARENT_STORY),
                GraphRelation(6303, RelationType.PARENT_STORY),
            ),
        },
    )

    assert index.same_story_exclusions(4936) == frozenset({4936})
    assert index.same_story_exclusions(6303) == frozenset({6303})


def test_relation_only_taka_no_tsume_glass_no_kamen_node_35612_cannot_relay() -> None:
    index = _index(
        (13431, 17707),
        {
            35612: (
                GraphRelation(13431, RelationType.PARENT_STORY),
                GraphRelation(17707, RelationType.PARENT_STORY),
            )
        },
    )

    assert index.same_story_exclusions(13431) == frozenset({13431})
    assert index.same_story_exclusion_path(13431, 17707) is None


def test_relation_only_crayon_shin_chan_node_966_cannot_be_a_manual_hub() -> None:
    index = _index((2450, 3744, 35139), {}, {966: (2450, 3744, 35139)})

    assert all(index.same_story_exclusions(anime_id) == frozenset({anime_id}) for anime_id in (2450, 3744, 35139))
    assert index.recommendation_entity_id(2450) == 2450


def test_anpanman_parent_story_movies_remain_franchise_context_only() -> None:
    index = _index(
        (1960, 10056, 10057),
        {
            10056: (GraphRelation(1960, RelationType.PARENT_STORY),),
            10057: (GraphRelation(1960, RelationType.PARENT_STORY),),
        },
    )

    assert index.same_story_exclusions(1960) == frozenset({1960})
    assert index.same_story_exclusions(10056) == frozenset({10056})
    assert index.franchise_members(10056) == frozenset({1960, 10056, 10057})
