"""Equation-level tests for weighted similarity and final ranking."""

import numpy as np
import pytest

from features.blocks import FeatureBlock, FeatureBundle
from recommender.metrics import Similarity, similarity_score
from recommender.properties import SimilarityProperty
from recommender.ranking import ScoreDescending
from recommender.weighted_v2 import WeightedV2Index, weighted_similarity


def _weighted_fixture() -> FeatureBundle:
    second_candidate = np.asarray([0.6, 0.8])
    first_block = np.asarray(
        [[1.0, 0.0], [0.8, 0.6], second_candidate],
    )
    second_block = np.asarray(
        [[1.0, 0.0], [0.4, np.sqrt(0.84)], second_candidate],
    )
    return FeatureBundle(
        np.asarray([10, 20, 30], dtype=np.int64),
        (
            FeatureBlock('first', 'dense', first_block, ('x', 'y'), ('first',)),
            FeatureBlock('second', 'dense', second_block, ('x', 'y'), ('second',)),
        ),
    )


def _weighted_properties() -> tuple[SimilarityProperty, ...]:
    return (
        SimilarityProperty('first', 0.25, contributes_to_content=True),
        SimilarityProperty('second', 0.75, contributes_to_content=True),
    )


def test_weighted_similarity_matches_explicit_weighted_average() -> None:
    bundle = _weighted_fixture()
    properties = _weighted_properties()

    score = weighted_similarity(bundle, 0, 1, properties=properties)

    assert score == pytest.approx(0.25 * 0.8 + 0.75 * 0.4)


def test_rank_returns_weighted_scores_in_descending_order() -> None:
    bundle = _weighted_fixture()
    index = WeightedV2Index(bundle, properties=_weighted_properties())

    results = index.rank(0, limit=2)

    assert [anime_id for anime_id, _ in results] == [30, 20]
    assert results[0][1] == pytest.approx(0.6)
    assert results[1][1] == pytest.approx(0.5)


def test_streaming_rank_matches_direct_rank_scores_and_order() -> None:
    index = WeightedV2Index(_weighted_fixture(), properties=_weighted_properties())

    direct = index.rank(0, limit=2)
    streaming = index.rank_many_streaming((0,), limit=2, candidate_batch_size=1)[0]

    assert tuple(anime_id for anime_id, _ in streaming) == tuple(anime_id for anime_id, _ in direct)
    assert tuple(score for _, score in streaming) == pytest.approx(tuple(score for _, score in direct))


def test_missing_feature_weight_is_renormalized() -> None:
    bundle = FeatureBundle(
        np.asarray([10, 20], dtype=np.int64),
        (
            FeatureBlock(
                'first',
                'dense',
                np.asarray([[1.0, 0.0], [0.8, 0.6]]),
                ('x', 'y'),
                ('first',),
            ),
            FeatureBlock(
                'second',
                'dense',
                np.asarray([[1.0, 0.0], [0.0, 0.0]]),
                ('x', 'y'),
                ('second',),
                row_available=np.asarray([True, False], dtype=bool),
            ),
        ),
    )
    properties = (
        SimilarityProperty('first', 0.25, contributes_to_content=True),
        SimilarityProperty('second', 0.75, contributes_to_content=True),
    )
    index = WeightedV2Index(bundle, properties=properties)

    renormalized = index.rank(0, limit=1, require_content=False, renormalize_available=True)
    unrenormalized = index.rank(0, limit=1, require_content=False, renormalize_available=False)

    assert renormalized == ((20, pytest.approx(0.8)),)
    assert unrenormalized == ((20, pytest.approx(0.2)),)


def test_score_descending_uses_anime_id_as_tie_breaker() -> None:
    candidates = (
        (30, 0, 0.8, ()),
        (10, 0, 0.8, ()),
        (20, 0, 0.6, ()),
    )

    ranked = ScoreDescending().rank(candidates)

    assert tuple(candidate[0] for candidate in ranked) == (10, 30, 20)


@pytest.mark.parametrize(
    ('metric', 'expected'),
    [
        (Similarity.COSINE, 1.0),
        (Similarity.JACCARD, 1.0 / 3.0),
        (Similarity.DICE, 0.5),
        (Similarity.MANHATTAN, 2.0 / 3.0),
    ],
)
def test_similarity_metrics_match_their_definitions(metric: Similarity, expected: float) -> None:
    left = np.asarray([1.0, 1.0, 0.0])
    right = np.asarray([1.0, 0.0, 1.0])
    if metric is Similarity.COSINE:
        left = np.asarray([1.0, 0.0])
        right = np.asarray([1.0, 0.0])
    elif metric is Similarity.MANHATTAN:
        left = np.asarray([0.0, 1.0])
        right = np.asarray([1.0, 1.0])

    assert similarity_score(left, right, metric) == pytest.approx(expected)


@pytest.mark.parametrize('metric', [Similarity.COSINE, Similarity.JACCARD, Similarity.DICE])
def test_similarity_metrics_return_zero_for_empty_inputs(metric: Similarity) -> None:
    values = np.zeros(2)

    assert similarity_score(values, values, metric) == 0.0


def test_rank_excludes_non_positive_and_non_finite_scores() -> None:
    bundle = FeatureBundle(
        np.asarray([10, 20, 30, 40, 50], dtype=np.int64),
        (
            FeatureBlock(
                'first',
                'dense',
                np.asarray([[1.0, 0.0], [np.nan, 0.0], [-1.0, 0.0], [0.0, 1.0], [1.0, 0.0]]),
                ('x', 'y'),
                ('first',),
            ),
        ),
    )
    index = WeightedV2Index(
        bundle,
        properties=(SimilarityProperty('first', 1.0, contributes_to_content=True),),
    )

    assert index.rank(0, limit=10) == ((50, 1.0),)


def test_streaming_rank_matches_direct_rank_for_multiple_sources() -> None:
    index = WeightedV2Index(_weighted_fixture(), properties=_weighted_properties())

    direct = tuple(index.rank(source, limit=2) for source in (0, 1))
    streaming = index.rank_many_streaming((0, 1), limit=2, candidate_batch_size=1)

    for expected, actual in zip(direct, streaming, strict=True):
        assert tuple(anime_id for anime_id, _ in actual) == tuple(anime_id for anime_id, _ in expected)
        assert tuple(score for _, score in actual) == pytest.approx(tuple(score for _, score in expected))


def test_rank_requires_semantic_features_when_requested() -> None:
    index = WeightedV2Index(_weighted_fixture(), properties=_weighted_properties())

    assert index.rank(0, limit=2, require_semantic=True) == ()


def test_rank_rejects_invalid_source_and_streaming_batch_size() -> None:
    index = WeightedV2Index(_weighted_fixture(), properties=_weighted_properties())

    with pytest.raises(IndexError, match='outside'):
        index.rank(-1)
    with pytest.raises(ValueError, match='positive'):
        index.rank_many_streaming((0,), candidate_batch_size=0)
