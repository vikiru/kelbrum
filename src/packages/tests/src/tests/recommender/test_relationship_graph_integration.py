from collections.abc import Sequence

import numpy as np
import polars as pl
import pytest
from scipy.sparse import csr_matrix

import graph
from features.blocks import FeatureBlock, FeatureBundle
from graph import GraphNode, GraphRelation, RelationType
from recommender.frozen_pipeline import Recommender
from recommender.inputs import RecommenderInputs
from recommender.plan import RecommenderPlan
from recommender.qualification import canonical_candidate_ids, qualify_candidates
from recommender.ranking import ScoredCandidate
from recommender.retrieval import RetrievalEngine
from recommender.scoring import ScoringProperty, coverage, score_candidates
from recommender.surfacing import SurfacingPolicy
from recommender.union import NoUnion, PathEvidence, RetrievalMode, UnionCandidate, build_union, reduce_path_results


class ReverseIdRanking:
    name = 'reverse-id'
    identity = 'reverse-id-v1'

    def rank(self, candidates: Sequence[ScoredCandidate]) -> tuple[ScoredCandidate, ...]:
        return tuple(sorted(candidates, key=_candidate_id, reverse=True))


def _candidate_id(item: ScoredCandidate) -> int:
    return item[0]


class _SinglePathRanker:
    def __init__(self, result: tuple[tuple[int, float], ...]) -> None:
        self.result = result

    def rank_many(self, source_indices: Sequence[int], *, limit: int) -> tuple[tuple[tuple[int, float], ...], ...]:
        _ = limit
        return tuple(self.result for _ in source_indices)


class _UnusedPathRanker:
    def rank_many(self, source_indices: Sequence[int], *, limit: int) -> tuple[tuple[tuple[int, float], ...], ...]:
        _ = (source_indices, limit)
        raise AssertionError('inactive retrieval path was executed')


class _UnusedStreamingRanker:
    def rank_many_streaming(
        self, path: str, source_indices: Sequence[int], *, limit: int, candidate_batch_size: int
    ) -> tuple[tuple[tuple[int, float], ...], ...]:
        _ = (path, source_indices, limit, candidate_batch_size)
        raise AssertionError('inactive synopsis path was executed')


def test_retrieval_executes_only_explicitly_enabled_paths() -> None:
    engine = RetrievalEngine(
        _UnusedStreamingRanker(),
        None,
        {'genres': _SinglePathRanker(((2, 0.8),)), 'themes': _UnusedPathRanker()},
        {'studio': _UnusedPathRanker()},
        retrieval_limit=10,
        mode=RetrievalMode.UNION,
        enabled_paths=('genres',),
    )

    batch = engine.retrieve((0,))

    assert batch.results == ((('genres', ((2, 0.8),)),),)
    with pytest.raises(ValueError, match='unique'):
        RetrievalEngine(
            _UnusedStreamingRanker(),
            None,
            {},
            {},
            retrieval_limit=10,
            mode=RetrievalMode.UNION,
            enabled_paths=('genres', 'genres'),
        )


def test_retrieval_identity_includes_retrieval_limit() -> None:
    first = RetrievalEngine(
        _UnusedStreamingRanker(),
        None,
        {},
        {},
        retrieval_limit=100,
        retrieval_batch_size=512,
        mode=RetrievalMode.UNION,
        enabled_paths=('genres',),
    )
    second = RetrievalEngine(
        _UnusedStreamingRanker(),
        None,
        {},
        {},
        retrieval_limit=200,
        retrieval_batch_size=512,
        mode=RetrievalMode.UNION,
        enabled_paths=('genres',),
    )
    assert first.identity != second.identity


def test_disabled_embedding_path_does_not_prepare_an_embedding_index(monkeypatch: pytest.MonkeyPatch) -> None:
    frame = pl.DataFrame(
        {
            'mal_id': [1, 2],
            'title': ['One', 'Two'],
            'genres': [['Drama'], ['Drama']],
            'themes': [[], []],
            'demographics': [[], []],
            'rating_class': ['G', 'G'],
            'synopsis_features': ['', ''],
            'studio_ids': [[], []],
        }
    )
    bundle = FeatureBundle(
        np.asarray([1, 2], dtype=np.int64),
        (
            FeatureBlock(
                'genres',
                'multi-hot',
                csr_matrix([[1.0], [1.0]]),
                ('Drama',),
                ('genres',),
            ),
        ),
    )

    def fail_if_called(_self: object, _values: object) -> None:
        raise AssertionError('disabled embedding path was prepared')

    monkeypatch.setattr('recommender.paths.SynopsisPathIndex.fit_embedding_matrix', fail_if_called)
    Recommender(
        RecommenderInputs(
            frame,
            bundle,
            synopsis_embedding_matrix=np.ones((2, 4), dtype=np.float32),
        ),
        RecommenderPlan(retrieval_paths=('genres',)),
    )


def test_no_union_preserves_independent_path_nominations() -> None:
    candidates = NoUnion().merge((('genres', ((2, 0.8),)), ('themes', ((2, 0.7),))))

    assert candidates == (
        UnionCandidate(2, (PathEvidence('genres', 1, 0.8),)),
        UnionCandidate(2, (PathEvidence('themes', 1, 0.7),)),
    )


def test_union_deduplicates_candidates_within_one_path_using_maximum_score() -> None:
    candidates = build_union((('genres', ((2, 0.4), (2, 0.8), (3, 0.2))),))

    assert candidates[0].anime_id == 2
    assert candidates[0].evidence == (PathEvidence('genres', 2, 0.8),)
    with pytest.raises(ValueError, match='finite'):
        build_union((('genres', ((3, float('nan')),)),))


def test_union_exposes_path_and_family_provenance() -> None:
    candidate = build_union(
        (
            ('embedding', ((2, 0.8),)),
            ('genres', ((2, 0.7),)),
            ('studio', ((2, 0.6),)),
        )
    )[0]

    assert candidate.path_count == 3
    assert candidate.family_count == 3
    assert candidate.evidence_families == ('affinity', 'semantic', 'structured')


def test_union_does_not_treat_paths_within_one_family_as_independent_families() -> None:
    candidate = build_union(
        (
            ('bm25', ((2, 0.8),)),
            ('lsa', ((2, 0.7),)),
            ('embedding', ((2, 0.6),)),
        )
    )[0]

    assert candidate.path_count == 3
    assert candidate.family_count == 1
    assert candidate.evidence_families == ('semantic',)


def test_union_rejects_unknown_paths_in_both_reduction_modes() -> None:
    for mode in (RetrievalMode.UNION, RetrievalMode.FAMILY_REDUCED):
        with pytest.raises(ValueError, match='unknown retrieval path'):
            reduce_path_results((('unknown', ((2, 0.5),)),), mode=mode)


def test_scoring_accepts_an_alternate_ranking_policy() -> None:
    result = score_candidates(
        1,
        (
            UnionCandidate(2, (PathEvidence('genres', 1, 0.8),)),
            UnionCandidate(3, (PathEvidence('genres', 1, 0.7),)),
        ),
        genres_by_id={1: ('Drama',), 2: ('Drama',), 3: ('Drama',)},
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={},
        ranking_policy=ReverseIdRanking(),
    )

    assert tuple(item[0] for item in result) == (3, 2)


def test_scoring_properties_can_replace_metrics_without_touching_other_properties() -> None:
    result = score_candidates(
        1,
        (UnionCandidate(2, (PathEvidence('themes', 1, 0.0),)),),
        genres_by_id={1: ('Drama',), 2: ('Action',)},
        themes_by_id={1: ('School', 'Music'), 2: ('School',)},
        tags_by_id={},
        demographics_by_id={},
        properties=(ScoringProperty('themes', 1.0, coverage),),
    )

    assert result == ((2, 2, 0.5, ('themes',)),)


def test_scoring_accepts_a_new_property_without_scoring_code_changes() -> None:
    result = score_candidates(
        1,
        (UnionCandidate(2, (PathEvidence('languages', 1, 0.0),)),),
        genres_by_id={},
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={},
        properties=(ScoringProperty('languages', 1.0, coverage),),
        property_values={'languages': {1: ('Japanese',), 2: ('Japanese', 'English')}},
    )

    assert result == ((2, 2, 1.0, ('languages',)),)


def test_recommender_produces_stable_in_memory_rankings() -> None:
    frame = pl.DataFrame(
        {
            'mal_id': [1, 2, 3],
            'title': ['Source', 'Matching', 'Different'],
            'genres': [['Drama'], ['Drama'], ['Action']],
            'themes': [[], [], []],
            'demographics': [[], [], []],
            'rating_class': ['G', 'G', 'G'],
            'synopsis_features': ['', '', ''],
            'studio_ids': [[], [], []],
        }
    )
    bundle = FeatureBundle(np.asarray([1, 2, 3], dtype=np.int64), ())
    recommender = Recommender(
        RecommenderInputs(
            frame,
            bundle,
            surfacing_policy=SurfacingPolicy(minimum_score=0.0),
        ),
        RecommenderPlan(retrieval_paths=('genres',)),
    )

    first = recommender.recommend_ids_many((1,), limit=10)
    second = recommender.recommend_ids_many((1,), limit=10)

    assert first == second == {1: (2,)}


def build_graph_fixture(
    anime_ids: tuple[int, ...],
    relations: dict[int, tuple[tuple[int, str], ...]],
    *,
    manual_relationships: dict[int, tuple[int, ...]] | None = None,
    anime_types: dict[int, str] | None = None,
):
    nodes = tuple(GraphNode(anime_id, (anime_types or {}).get(anime_id)) for anime_id in anime_ids)
    graph_relations = {
        source: tuple(GraphRelation(target, RelationType(relation)) for target, relation in targets)
        for source, targets in relations.items()
    }
    return graph.build_relationship_index(nodes, graph_relations, manual_relationships=manual_relationships)


def test_same_story_family_is_removed_and_candidates_are_canonicalized() -> None:
    index = build_graph_fixture(
        (1, 2, 3, 4),
        {
            1: ((2, 'Sequel'),),
            2: ((1, 'Prequel'),),
            3: ((4, 'Sequel'),),
            4: ((3, 'Prequel'),),
        },
    )

    assert index.cleanup(1, (1, 2, 3, 4)) == (3,)


def test_manual_relationships_are_symmetric_and_fingerprinted() -> None:
    index = build_graph_fixture((1, 2), {}, manual_relationships={1: (2,)})

    assert index.excluded_ids(1) == frozenset({1, 2})
    assert index.excluded_ids(2) == frozenset({1, 2})
    assert index.fingerprint()


def test_frozen_union_keeps_highest_alias_score_and_merges_paths() -> None:
    index = build_graph_fixture(
        (1, 2, 3, 4),
        {
            2: ((3, 'Sequel'), (4, 'Sequel')),
            3: ((2, 'Prequel'),),
            4: ((2, 'Prequel'),),
        },
        anime_types={2: 'TV', 3: 'TV', 4: 'TV'},
    )
    candidates = (
        UnionCandidate(3, (PathEvidence('embedding', 1, 0.2),)),
        UnionCandidate(
            4,
            (
                PathEvidence('embedding', 1, 0.8),
                PathEvidence('genres', 1, 0.8),
            ),
        ),
    )

    qualified = qualify_candidates(1, candidates, relationship_index=index)
    result = score_candidates(
        1,
        qualified,
        genres_by_id={},
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={},
        canonical_ids=canonical_candidate_ids(qualified, index),
    )

    assert result == ((2, 4, 0.336, ('embedding', 'genres')),)


def test_tv_origin_beats_movie_and_ona_entries_when_relationships_identify_origin() -> None:
    index = build_graph_fixture(
        (10, 11, 12),
        {
            10: ((11, 'Sequel'), (12, 'Sequel')),
            11: ((10, 'Prequel'),),
            12: ((10, 'Prequel'),),
        },
        anime_types={10: 'TV', 11: 'Movie', 12: 'ONA'},
    )

    assert index.canonical_id(11) == 10
    assert index.canonical_id(12) == 10


def test_movie_family_without_tv_origin_uses_deterministic_first_entry() -> None:
    index = build_graph_fixture(
        (20, 21, 22),
        {20: ((21, 'Sequel'),), 21: ((20, 'Prequel'),), 22: ((21, 'Sequel'),)},
        anime_types={20: 'Movie', 21: 'Movie', 22: 'Movie'},
    )

    assert index.canonical_id(20) == 20
    assert index.canonical_id(21) == 20
    assert index.canonical_id(22) == 20


def test_relation_only_bridge_connects_requested_entries_to_their_origin() -> None:
    index = build_graph_fixture(
        (41219, 50207, 57067),
        {
            41219: ((50207, 'Sequel'),),
            50207: ((41219, 'Prequel'), (55993, 'Sequel')),
            55993: ((50207, 'Prequel'), (57067, 'Sequel')),
            57067: ((55993, 'Prequel'),),
        },
        anime_types={41219: 'TV', 50207: 'ONA', 57067: 'ONA'},
    )

    assert index.canonical_id(57067) == 41219
    assert index.excluded_ids(57067) == frozenset({41219, 50207, 57067})


def test_original_and_remake_are_collapsed_by_alternative_version_relation() -> None:
    index = build_graph_fixture(
        (30, 31),
        {30: ((31, 'Alternative Version'),)},
        anime_types={30: 'TV', 31: 'TV'},
    )

    assert index.canonical_id(30) == 30
    assert index.canonical_id(31) == 30
    assert index.cleanup(30, (31,)) == ()


def test_spin_off_remains_a_separate_recommendation_family() -> None:
    index = build_graph_fixture(
        (40, 41),
        {40: ((41, 'Spin-Off'),)},
        anime_types={40: 'TV', 41: 'TV'},
    )

    assert index.canonical_id(40) != index.canonical_id(41)
    assert index.excluded_ids(40) == frozenset({40})


def test_unrelated_parent_story_and_spin_off_relations_remain_distinct() -> None:
    relation_types = (
        'Alternative Setting',
        'Character',
        'Other',
        'Parent Story',
        'Side Story',
        'Spin-Off',
    )
    relations = {100: tuple(enumerate(relation_types, 101))}
    anime_ids = tuple(range(100, 107))
    anime_types = dict.fromkeys(anime_ids, 'TV')

    index = build_graph_fixture(anime_ids, relations, anime_types=anime_types)

    for candidate_id in range(101, 104):
        assert index.canonical_id(candidate_id) == candidate_id
        assert index.cleanup(100, (candidate_id,)) == (candidate_id,)

    assert index.canonical_id(104) == 100
    assert index.cleanup(100, (104,)) == ()
    assert index.canonical_id(105) == 105
    assert index.cleanup(100, (105,)) == (105,)
    assert index.canonical_id(106) == 106
    assert index.cleanup(100, (106,)) == (106,)


def test_same_story_relations_still_collapse_inside_a_franchise() -> None:
    index = build_graph_fixture(
        (200, 201, 202),
        {
            200: ((201, 'Sequel'), (202, 'Alternative Version')),
            201: ((200, 'Prequel'),),
            202: ((200, 'Alternative Version'),),
        },
        anime_types={200: 'TV', 201: 'TV', 202: 'TV'},
    )

    assert index.canonical_id(201) == 200
    assert index.canonical_id(202) == 200
    assert index.cleanup(200, (201, 202)) == ()
