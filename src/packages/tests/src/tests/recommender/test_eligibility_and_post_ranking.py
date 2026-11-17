from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import polars as pl
from scipy.sparse import csr_matrix

from features.blocks import FeatureBlock, FeatureBundle
from graph import IdentityIntent, ManualRelationshipRow, SameStoryIntent, TraversalMode
from normalization.ratings import RatingClass
from recommender.inputs import RecommenderInputs
from recommender.pipeline import Recommender, ScoredCandidate
from recommender.plan import RecommenderPlan
from recommender.post_ranking import (
    RATING_HYPOTHESIS,
    WEIGHT_AUDIENCE,
    WEIGHT_FORMAT_COMMITMENT,
    WEIGHT_QUALITY,
    AnimePostRankingMetadata,
    build_mainline_runtime_index,
    compute_audience_adjustment,
    compute_metadata_multiplier,
    compute_quality_adjustment,
    estimate_catalogue_duration_minutes,
    estimate_catalogue_episodes,
)
from recommender.retrieval import PathScores, RetrievalEngine

if TYPE_CHECKING:
    from collections.abc import Sequence


class MockSynopsisRanker:
    def __init__(self, anime_ids: Sequence[int]) -> None:
        self.anime_ids = tuple(anime_ids)

    def rank_many_streaming(
        self,
        path: str,
        source_indices: Sequence[int],
        *,
        limit: int,
        candidate_batch_size: int = 512,
        excluded_ids_by_source: Sequence[frozenset[int]] | None = None,
    ) -> tuple[PathScores, ...]:
        del path, candidate_batch_size
        results: list[PathScores] = []
        for i, s_idx in enumerate(source_indices):
            excluded = excluded_ids_by_source[i] if excluded_ids_by_source is not None else frozenset()
            candidates = [
                (idx, 1.0 - (idx * 0.01))
                for idx, aid in enumerate(self.anime_ids)
                if aid not in excluded and idx != s_idx
            ][:limit]
            results.append(tuple(candidates))
        return tuple(results)


def test_weight_quality_enabled() -> None:
    assert WEIGHT_QUALITY == 0.5
    assert WEIGHT_AUDIENCE == 1.0
    assert WEIGHT_FORMAT_COMMITMENT == 1.0

    anchor = AnimePostRankingMetadata(1, 'TV', 'Shounen', 'PG-13', 2020, 7.0, 100.0, demographics=('Shounen',))
    candidate_low = AnimePostRankingMetadata(2, 'TV', 'Shounen', 'PG-13', 2020, 6.0, 500.0, demographics=('Shounen',))
    candidate_high = AnimePostRankingMetadata(3, 'TV', 'Shounen', 'PG-13', 2020, 8.8, 500.0, demographics=('Shounen',))

    assert compute_quality_adjustment(anchor, candidate_low) < 0.0
    assert compute_quality_adjustment(anchor, candidate_high) > 0.0

    mult_low = compute_metadata_multiplier(anchor, candidate_low)
    mult_high = compute_metadata_multiplier(anchor, candidate_high)
    assert mult_low < 1.0
    assert mult_high > 1.0


def test_pg13_to_g_soft_rating_penalty_removed() -> None:
    assert RATING_HYPOTHESIS[(RatingClass.PG_13, RatingClass.G)] == 0.0
    assert RATING_HYPOTHESIS[(RatingClass.PG_13, RatingClass.PG)] == 0.0

    anchor_pg13 = AnimePostRankingMetadata(
        anime_id=4181,
        anime_type='TV',
        demographic='Missing',
        rating='PG-13',
        year=2008,
        score=7.0,
        mainline_runtime_minutes=600.0,
        demographics=(),
    )
    cand_g = AnimePostRankingMetadata(
        anime_id=102,
        anime_type='TV',
        demographic='Missing',
        rating='G',
        year=1991,
        score=7.0,
        mainline_runtime_minutes=600.0,
        demographics=(),
    )
    assert compute_audience_adjustment(anchor_pg13, cand_g) == 0.0
    # Both TV, same score (7.0, neutral), matched commitment (neutral 1.0)
    assert compute_metadata_multiplier(anchor_pg13, cand_g) == 1.0


def test_multi_demographic_compatibility() -> None:
    anchor_multi = AnimePostRankingMetadata(
        anime_id=1,
        anime_type='TV',
        demographic='Multiple',
        rating='PG',
        year=2010,
        score=7.5,
        mainline_runtime_minutes=1000.0,
        demographics=('Kids', 'Shounen'),
    )

    cand_shounen = AnimePostRankingMetadata(
        anime_id=2,
        anime_type='TV',
        demographic='Shounen',
        rating='PG',
        year=2010,
        score=7.5,
        mainline_runtime_minutes=1000.0,
        demographics=('Shounen',),
    )
    assert compute_audience_adjustment(anchor_multi, cand_shounen) == 0.005

    cand_josei = AnimePostRankingMetadata(
        anime_id=3,
        anime_type='TV',
        demographic='Josei',
        rating='PG',
        year=2010,
        score=7.5,
        mainline_runtime_minutes=1000.0,
        demographics=('Josei',),
    )
    assert compute_audience_adjustment(anchor_multi, cand_josei) == -0.001

    cand_missing = AnimePostRankingMetadata(
        anime_id=4,
        anime_type='TV',
        demographic='Missing',
        rating='PG',
        year=2010,
        score=7.5,
        mainline_runtime_minutes=1000.0,
        demographics=(),
    )
    assert compute_audience_adjustment(anchor_multi, cand_missing) == 0.002


def test_unclamped_demotions_below_minimum_score() -> None:
    source_meta = AnimePostRankingMetadata(1, 'TV', 'Shounen', 'PG-13', 2020, 8.0, 500.0, demographics=('Shounen',))
    cand_meta = AnimePostRankingMetadata(2, 'Movie', 'Kids', 'G', 1980, 7.0, 500.0, demographics=('Kids',))
    multiplier = compute_metadata_multiplier(source_meta, cand_meta)
    assert multiplier < 1.0

    base_candidate = ScoredCandidate(
        recommendation_entity_id=2,
        witness_member_id=2,
        score=0.201,
        retrieval_paths=('synopsis',),
    )

    class DummyPipeline:
        _catalogue_state = type(
            'CatState',
            (),
            {'post_ranking_metadata_by_id': {1: source_meta, 2: cand_meta}},
        )()

    dummy: Any = DummyPipeline()
    adjusted = Recommender._apply_metadata_post_ranking(
        dummy,
        1,
        (base_candidate,),
    )
    expected_score = 0.201 * multiplier
    assert adjusted[0].score == expected_score
    assert adjusted[0].score < 0.20


def test_retrieval_rating_prefilter_recovers_candidates() -> None:
    anime_ids = [101, 102, 103, 104, 105, 106]
    synopsis = MockSynopsisRanker(anime_ids)
    engine = RetrievalEngine(
        synopsis=synopsis,
        weighted=None,
        categorical={},
        affinity={},
        retrieval_limit=3,
        enabled_paths=('embedding',),
    )

    ineligible_for_g = frozenset({102, 103})

    batch_unfiltered = engine.retrieve((0,))
    retrieved_unfiltered_ids = [anime_ids[c[0]] for c in batch_unfiltered.results[0][0][1]]
    assert retrieved_unfiltered_ids == [102, 103, 104]

    batch_filtered = engine.retrieve((0,), ineligible_ids_by_source=(ineligible_for_g,))
    retrieved_filtered_ids = [anime_ids[c[0]] for c in batch_filtered.results[0][0][1]]
    assert retrieved_filtered_ids == [104, 105, 106]
    assert 102 not in retrieved_filtered_ids
    assert 103 not in retrieved_filtered_ids


def test_mature_anchors_unaffected_by_retrieval_prefilter() -> None:
    anime_ids = [201, 202, 203, 204]
    synopsis = MockSynopsisRanker(anime_ids)
    engine = RetrievalEngine(
        synopsis=synopsis,
        weighted=None,
        categorical={},
        affinity={},
        retrieval_limit=4,
        enabled_paths=('embedding',),
    )

    ineligible_empty = frozenset()

    batch_standard = engine.retrieve((0,))
    batch_mature = engine.retrieve((0,), ineligible_ids_by_source=(ineligible_empty,))

    res_standard = batch_standard.results[0][0][1]
    res_mature = batch_mature.results[0][0][1]
    assert res_standard == res_mature


def test_audience_adjustment_normalizes_rating_and_demographic_variants() -> None:
    canonical = compute_audience_adjustment(
        AnimePostRankingMetadata(1, 'TV', 'Shounen', 'PG-13', 2020, 7.5, 300.0, demographics=('Shounen',)),
        AnimePostRankingMetadata(2, 'TV', 'Shounen', 'PG-13', 2020, 7.5, 300.0, demographics=('Shounen',)),
    )
    variant = compute_audience_adjustment(
        AnimePostRankingMetadata(1, 'TV', 'shonen', 'PG_13', 2020, 7.5, 300.0, demographics=('shonen',)),
        AnimePostRankingMetadata(2, 'TV', 'SHOUNEN', 'PG-13 - Teens 13 or older', 2020, 7.5, 300.0),
    )
    assert variant == canonical == 0.5 * 0.006 + 0.5 * 0.004


def test_estimate_catalogue_episodes_and_duration_normalize_anime_type() -> None:
    assert estimate_catalogue_episodes(None, 'Movie') == 1
    assert estimate_catalogue_episodes(None, ' tv ') == 12
    assert estimate_catalogue_episodes(None, None) == 12
    assert estimate_catalogue_duration_minutes(None, 'Movie') == 90
    assert estimate_catalogue_duration_minutes(None, 'ona') == 15
    assert estimate_catalogue_duration_minutes(None, None) == 24


def test_build_mainline_runtime_index_groups_continuation_components() -> None:
    frame = pl.DataFrame(
        {
            'mal_id': [1, 2, 3],
            'episodes': [12, 12, 1],
            'anime_type': ['TV', 'TV', 'Movie'],
            'duration_minutes': [24, 24, 90],
        }
    )
    relations = pl.DataFrame(
        {
            'source_id': [1, 1],
            'target_id': [2, 3],
            'relation_type': ['Sequel', 'Spin-Off'],
            'same_story_intent': ['continuation', 'unrelated'],
        }
    )
    runtimes, episodes = build_mainline_runtime_index(frame, relations)
    assert runtimes == {1: 576.0, 2: 576.0, 3: 90.0}
    assert episodes == {1: 24, 2: 24, 3: 1}


def test_recommender_uses_manual_relationships_from_inputs_for_post_ranking() -> None:
    frame = pl.DataFrame(
        {
            'mal_id': [1, 2, 3],
            'title': ['One', 'Two', 'Three'],
            'genres': [['Drama'], ['Drama'], ['Drama']],
            'themes': [[], [], []],
            'demographics': [[], [], []],
            'rating_class': ['G', 'G', 'G'],
            'synopsis_features': ['', '', ''],
            'studio_ids': [[], [], []],
            'episodes': [12, 12, 1],
            'anime_type': ['TV', 'TV', 'Movie'],
            'duration_minutes': [24, 24, 90],
        }
    )
    bundle = FeatureBundle(
        np.asarray([1, 2, 3], dtype=np.int64),
        (
            FeatureBlock(
                'genres',
                'multi-hot',
                csr_matrix([[1.0], [1.0], [1.0]]),
                ('Drama',),
                ('genres',),
            ),
        ),
    )
    manual_rows = (
        ManualRelationshipRow(
            source_id=1,
            source_title='One',
            target_id=2,
            target_title='Two',
            relation_type='Sequel',
            same_story_intent=SameStoryIntent.CONTINUATION,
            traversal_mode=TraversalMode.TRANSITIVE,
            identity_intent=IdentityIntent.DISTINCT,
            provenance='test',
        ),
        ManualRelationshipRow(
            source_id=1,
            source_title='One',
            target_id=3,
            target_title='Three',
            relation_type='Spin-Off',
            same_story_intent=SameStoryIntent.FRANCHISE_ONLY,
            traversal_mode=TraversalMode.NONE,
            identity_intent=IdentityIntent.DISTINCT,
            provenance='test',
        ),
    )
    recommender = Recommender(
        RecommenderInputs(frame, bundle, manual_relationships=manual_rows),
        RecommenderPlan(retrieval_paths=('genres',), scoring_paths=()),
    )

    meta = recommender._catalogue_state.post_ranking_metadata_by_id
    assert meta[1].mainline_runtime_minutes == 576.0
    assert meta[1].storyline_episodes == 24
    assert meta[2].mainline_runtime_minutes == 576.0
    assert meta[2].storyline_episodes == 24
    assert meta[3].mainline_runtime_minutes == 90.0
    assert meta[3].storyline_episodes == 1
