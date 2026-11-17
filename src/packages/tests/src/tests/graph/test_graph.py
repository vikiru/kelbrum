import pytest

from graph import (
    GraphNode,
    GraphRelation,
    IdentityEquivalenceAssertion,
    IdentityIntent,
    ManualEdgePolicy,
    ManualRelationshipRow,
    RelationType,
    SameStoryIntent,
    build_relationship_index,
)
from graph.contracts import TraversalMode
from graph.registry import manual_relationships_to_dict, manual_relationships_to_policies


def _graph(
    anime_ids: tuple[int, ...],
    edges: tuple[tuple[int, int, RelationType], ...],
    *,
    manual: tuple[ManualEdgePolicy, ...] = (),
    overrides: dict[tuple[int, int, RelationType], SameStoryIntent] | None = None,
    identities: tuple[IdentityEquivalenceAssertion, ...] = (),
):
    relations: dict[int, list[GraphRelation]] = {}
    for source, target, relation in edges:
        relations.setdefault(source, []).append(GraphRelation(target, relation))
    return build_relationship_index(
        tuple(GraphNode(anime_id) for anime_id in anime_ids),
        relations,
        manual_edge_policies=manual,
        edge_overrides=overrides,
        identity_equivalences=identities,
    )


def test_sequel_chain_excludes_transitively_and_middle_anchor_excludes_both_directions() -> None:
    index = _graph(
        (1, 2, 3),
        ((1, 2, RelationType.SEQUEL), (2, 3, RelationType.SEQUEL)),
    )

    assert index.same_story_exclusions(1) == frozenset({1, 2, 3})
    assert index.same_story_exclusions(2) == frozenset({1, 2, 3})
    assert index.same_story_exclusion_path(1, 3) is not None
    assert index.recommendation_entity_id(2) == 2


def test_specific_sequel_edge_can_be_overridden_without_weakening_default_policy() -> None:
    index = _graph(
        (1, 2, 3),
        ((1, 2, RelationType.SEQUEL), (2, 3, RelationType.SEQUEL)),
        overrides={(2, 3, RelationType.SEQUEL): SameStoryIntent.NEEDS_REVIEW},
    )

    assert index.same_story_exclusions(1) == frozenset({1, 2})
    assert index.same_story_exclusions(3) == frozenset({3})


def test_prequel_link_excludes_continuation_in_both_directions() -> None:
    index = _graph((1, 2), ((1, 2, RelationType.PREQUEL),))

    assert index.same_story_exclusions(1) == frozenset({1, 2})
    assert index.same_story_exclusions(2) == frozenset({1, 2})


def test_relation_only_connector_cannot_transmit_exclusions() -> None:
    index = _graph(
        (10, 12),
        (
            (10, 11, RelationType.SEQUEL),
            (11, 12, RelationType.SEQUEL),
        ),
    )

    assert index.same_story_exclusions(10) == frozenset({10})
    assert index.same_story_exclusions(12) == frozenset({12})
    assert index.franchise_members(10) == frozenset({10})


@pytest.mark.parametrize(
    ('source', 'target'),
    [(9253, 30484), (477, 3297)],
)
def test_reviewed_real_manual_continuations_are_typed(source: int, target: int) -> None:
    policy = ManualEdgePolicy(
        source,
        target,
        SameStoryIntent.CONTINUATION,
        'Reviewed direct continuing-story season/entry.',
        'regression-fixture',
    )
    index = build_relationship_index(
        (GraphNode(source), GraphNode(target)),
        {},
        manual_relationships={source: (target,)},
        manual_edge_policies=(policy,),
    )

    assert index.same_story_exclusions(source) == frozenset({source, target})


def test_reviewed_manual_continuation_chains_promote_only_their_storylines() -> None:
    relationship_rows = tuple(
        ManualRelationshipRow(
            source_id=source_id,
            source_title='',
            target_id=target_id,
            target_title='',
            relation_type='Manual',
            same_story_intent=SameStoryIntent.CONTINUATION,
            traversal_mode=TraversalMode.TRANSITIVE,
            identity_intent=IdentityIntent.DISTINCT,
            provenance='regression-fixture',
        )
        for source_id, target_id in ((9253, 11577), (11577, 30484), (477, 962), (962, 3297))
    )
    manual_edge_policies = manual_relationships_to_policies(relationship_rows)
    index = build_relationship_index(
        tuple(GraphNode(anime_id) for anime_id in (9253, 11577, 30484, 477, 962, 3297, 9999)),
        {},
        manual_relationships=manual_relationships_to_dict(relationship_rows),
        manual_edge_policies=manual_edge_policies,
    )

    assert index.same_story_exclusions(9253) == frozenset({9253, 11577, 30484})
    assert index.same_story_exclusions(477) == frozenset({477, 962, 3297})
    assert index.same_story_exclusions(9999) == frozenset({9999})


def test_franchise_only_relationship_keeps_candidate_eligible() -> None:
    index = build_relationship_index(
        (GraphNode(1), GraphNode(2)),
        {},
        manual_relationships={1: (2,)},
        manual_edge_policies=(
            ManualEdgePolicy(
                1,
                2,
                SameStoryIntent.FRANCHISE_ONLY,
                'Shared franchise context without story continuity.',
                'regression-fixture',
                traversal_mode=TraversalMode.NONE,
            ),
        ),
    )

    assert 2 not in index.same_story_exclusions(1)
    assert index.franchise_members(1) == frozenset({1, 2})
    assert index.recommendation_entity_id(1) != index.recommendation_entity_id(2)


def test_relation_only_bridge_connects_requested_nodes() -> None:
    index = build_relationship_index(
        (GraphNode(10, 'TV'), GraphNode(12, 'ONA')),
        {
            10: (GraphRelation(11, RelationType.SEQUEL),),
            11: (GraphRelation(10, RelationType.PREQUEL), GraphRelation(12, RelationType.SEQUEL)),
            12: (GraphRelation(11, RelationType.PREQUEL),),
        },
    )

    assert index.excluded_ids(12) == frozenset({12})
    assert index.canonical_id(12) == 12


def test_untyped_manual_edge_does_not_exclude() -> None:
    index = build_relationship_index(
        (GraphNode(1), GraphNode(2)),
        {},
        manual_relationships={1: (2,)},
    )

    assert index.same_story_exclusions(1) == frozenset({1})
    assertion = next(edge for edge in index.edge_assertions if edge.relation_type is RelationType.MANUAL)
    assert assertion.same_story_intent is SameStoryIntent.NEEDS_REVIEW


def test_typed_manual_pairwise_and_franchise_intents_are_non_transitive() -> None:
    policies = (
        ManualEdgePolicy(1, 2, SameStoryIntent.PAIRWISE_EXCLUSION, 'Direct pair only.', 'review'),
        ManualEdgePolicy(2, 3, SameStoryIntent.CONTINUATION, 'Continuing story.', 'review'),
        ManualEdgePolicy(4, 5, SameStoryIntent.FRANCHISE_ONLY, 'Franchise context.', 'review'),
    )
    index = build_relationship_index(
        tuple(GraphNode(anime_id) for anime_id in range(1, 6)),
        {},
        manual_relationships={1: (2,), 2: (3,), 4: (5,)},
        manual_edge_policies=policies,
    )

    assert index.same_story_exclusions(1) == frozenset({1, 2})
    assert index.same_story_exclusions(4) == frozenset({4})
    assert index.franchise_members(4) == frozenset({4, 5})


@pytest.mark.parametrize('relation', [RelationType.SUMMARY, RelationType.FULL_STORY])
def test_pairwise_recap_excludes_endpoint_without_relaying(relation: RelationType) -> None:
    index = _graph(
        (1, 2, 3),
        ((1, 2, relation), (2, 3, RelationType.SEQUEL)),
        overrides={(1, 2, relation): SameStoryIntent.PAIRWISE_EXCLUSION},
    )

    assert index.same_story_exclusions(1) == frozenset({1, 2})
    assert index.same_story_exclusions(2) == frozenset({1, 2, 3})
    assert index.same_story_exclusion_path(1, 2)
    assert index.same_story_exclusion_path(1, 3) is None


def test_alternative_adaptation_and_parent_story_do_not_change_identity_or_exclusion() -> None:
    index = _graph(
        (1, 2, 3),
        (
            (1, 2, RelationType.ALTERNATIVE_VERSION),
            (2, 3, RelationType.PARENT_STORY),
        ),
    )

    assert index.recommendation_entity_id(1) == 1
    assert index.recommendation_entity_id(2) == 2
    assert index.same_story_exclusions(1) == frozenset({1})
    assert index.franchise_members(1) == frozenset({1, 2, 3})


def test_franchise_connectivity_cannot_change_identity_or_same_story() -> None:
    disconnected = _graph((1, 2, 3), ((1, 2, RelationType.SEQUEL),))
    connected = _graph(
        (1, 2, 3),
        ((1, 2, RelationType.SEQUEL), (2, 3, RelationType.SPIN_OFF)),
    )

    assert disconnected.recommendation_entity_by_id == connected.recommendation_entity_by_id
    assert disconnected.exclusions_by_id == connected.exclusions_by_id


def test_explicit_identity_equivalence_does_not_create_story_exclusion() -> None:
    index = _graph(
        (1, 2),
        (),
        identities=(IdentityEquivalenceAssertion(1, 2, 'Same catalogue edition', 'reviewed-registry'),),
    )

    assert index.recommendation_entity_id(1) == index.recommendation_entity_id(2)
    assert index.recommendation_entity_members(1) == frozenset({1, 2})
    assert index.same_story_exclusions(1) == frozenset({1})


def test_typed_identity_equivalent_manual_assertion_is_supported() -> None:
    policy = ManualEdgePolicy(
        1,
        2,
        SameStoryIntent.FRANCHISE_ONLY,
        'Same interchangeable catalogue edition.',
        'reviewed-registry',
        IdentityIntent.IDENTITY_EQUIVALENT,
    )
    index = build_relationship_index(
        (GraphNode(1), GraphNode(2)),
        {},
        manual_relationships={1: (2,)},
        manual_edge_policies=(policy,),
    )

    assert index.recommendation_entity_id(1) == index.recommendation_entity_id(2)
    assert index.same_story_exclusions(1) == frozenset({1})


def test_manual_policy_requires_rationale_and_provenance() -> None:
    with pytest.raises(ValueError, match='rationale and provenance'):
        ManualEdgePolicy(1, 2, SameStoryIntent.CONTINUATION, '', '')


def test_relation_only_path_is_not_returned_as_exclusion_witness() -> None:
    index = _graph(
        (35612, 13431, 17707),
        (
            (35612, 13431, RelationType.PARENT_STORY),
            (35612, 17707, RelationType.PARENT_STORY),
        ),
    )

    assert index.same_story_exclusion_path(13431, 17707) is None


def test_manual_identity_policy_rejects_story_exclusion_intent() -> None:
    with pytest.raises(ValueError, match='must not imply same-story'):
        ManualEdgePolicy(
            1,
            2,
            SameStoryIntent.CONTINUATION,
            'Contradictory intent.',
            'reviewed-registry',
            IdentityIntent.IDENTITY_EQUIVALENT,
        )
