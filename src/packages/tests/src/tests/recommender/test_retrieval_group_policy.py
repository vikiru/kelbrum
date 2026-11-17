from collections.abc import Sequence

from graph import GraphNode, GraphRelation, RelationType, build_relationship_index
from recommender.paths import CategoricalPathIndex
from recommender.plan import RecommenderPlan
from recommender.retrieval import PathScores, RetrievalEngine
from recommender.union import (
    DEFAULT_RETRIEVAL_PATHS,
    RetrievalGroupBudget,
    reduce_path_results,
)


def test_production_reducer_reports_selection_separately_from_path_evidence() -> None:
    reduction = reduce_path_results(
        (
            ('weighted-v2', ((11, 0.9),)),
            ('tags', ((22, 0.8), (11, 0.1))),
        ),
        budgets=RetrievalGroupBudget(semantic=1, structured=1, neighbourhood=1, affinity=1),
    )

    assert reduction.path_results == (
        ('weighted-v2', ((11, 0.9),)),
        ('tags', ((22, 0.8), (11, 0.1))),
    )
    assert [(selection.group, selection.candidate_ids) for selection in reduction.selected_by_group] == [
        ('neighbourhood', (11,)),
        ('structured', (22,)),
    ]


def test_default_plan_includes_core_retrieval_paths() -> None:
    plan = RecommenderPlan()

    assert plan.retrieval_paths == DEFAULT_RETRIEVAL_PATHS
    assert DEFAULT_RETRIEVAL_PATHS == (
        'embedding',
        'weighted-v2',
        'bm25',
        'themes',
        'genres',
        'tags',
        'lsa',
    )
    assert 'tags' in DEFAULT_RETRIEVAL_PATHS
    assert 'bm25' in DEFAULT_RETRIEVAL_PATHS
    assert plan.retrieval_group_budget == RetrievalGroupBudget()
    assert plan.gated_synopsis_transfer is True
    assert plan.evidence_qualified_multiplier is True
    assert any(property_spec.name == 'tags' for property_spec in plan.scoring_properties)
    assert any(property_spec.name == 'demographics' for property_spec in plan.scoring_properties)
    assert plan.scoring_paths == ('bm25', 'lsa', 'embedding')


def test_retrieval_engine_bypasses_group_reduction_when_budget_is_none() -> None:
    class MockRanker:
        def rank_many(
            self,
            source_indices: Sequence[int],
            *,
            limit: int,
            excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
        ) -> tuple[PathScores, ...]:
            _ = excluded_ids_by_source
            return tuple(tuple((i, 1.0 / (i + 1)) for i in range(1, limit + 1)) for _ in source_indices)

        def rank_many_streaming(
            self,
            path: str,
            source_indices: Sequence[int],
            *,
            limit: int,
            candidate_batch_size: int = 512,
            excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
        ) -> tuple[PathScores, ...]:
            _ = (path, candidate_batch_size, excluded_ids_by_source)
            return tuple(tuple((i, 1.0 / (i + 1)) for i in range(1, limit + 1)) for _ in source_indices)

    mock = MockRanker()
    engine = RetrievalEngine(
        mock,
        None,
        {'genres': mock, 'themes': mock, 'tags': mock},
        {},
        retrieval_limit=300,
        group_budget=None,
        path_limits={'tags': 100},
        enabled_paths=('genres', 'themes', 'tags'),
    )

    batch = engine.retrieve((0,))
    # All candidates from each path preserved without group reduction
    results_by_path = dict(batch.results[0])
    assert len(results_by_path['genres']) == 300
    assert len(results_by_path['themes']) == 300
    assert len(results_by_path['tags']) == 100
    # Original results match output results
    assert batch.original_results[0] == batch.results[0]
    # No group quota selections recorded
    assert batch.selected_by_group == ((),)
    # Reduced candidate count in diagnostics counts unique IDs across unpruned paths
    assert batch.diagnostics.reduced_candidate_count == 300


def test_excluded_continuation_does_not_consume_retrieval_top_k_slot() -> None:
    class _NoSynopsisRanker:
        anime_ids = (1, 2, 3)

        def rank_many_streaming(
            self,
            path: str,
            source_indices: Sequence[int],
            *,
            limit: int,
            candidate_batch_size: int,
            excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
        ) -> tuple[tuple[tuple[int, float], ...], ...]:
            _ = (path, source_indices, limit, candidate_batch_size, excluded_ids_by_source)
            raise AssertionError('no synopsis path should run')

    anime_ids = (1, 2, 3)
    graph = build_relationship_index(
        tuple(GraphNode(anime_id) for anime_id in anime_ids),
        {1: (GraphRelation(2, RelationType.SEQUEL),)},
    )
    genres = CategoricalPathIndex(anime_ids, (('shared',), ('shared',), ('shared',)))
    engine = RetrievalEngine(
        _NoSynopsisRanker(),
        None,
        {'genres': genres},
        {},
        retrieval_limit=1,
        enabled_paths=('genres',),
        relationship_index=graph,
    )

    batch = engine.retrieve((0,))

    assert batch.results[0][0][1] == ((3, 1.0),)
