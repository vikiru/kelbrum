import numpy as np
import pytest

from recommender.metrics import (
    TVERSKY_ALPHA,
    TVERSKY_BETA,
    Similarity,
    SimilarityOperands,
    similarity_score,
    tversky,
    vectorized_similarity,
)
from recommender.scoring import coverage, dice


def test_tversky_is_registered_as_a_shared_similarity_type() -> None:
    assert Similarity.TVERSKY.value == 'tversky'
    assert TVERSKY_ALPHA == 0.7
    assert TVERSKY_BETA == 0.3


def test_tversky_is_asymmetric_with_default_parameters() -> None:
    assert tversky({'genre'}, {'genre', 'extra'}) == 1.0 / 1.3
    assert tversky({'genre', 'extra'}, {'genre'}) == 1.0 / 1.7


def test_tversky_returns_zero_for_empty_sets() -> None:
    assert tversky(set(), set()) == 0.0


@pytest.mark.parametrize(
    ('metric', 'expected'),
    [
        (Similarity.JACCARD, 1.0 / 3.0),
        (Similarity.DICE, 0.5),
        (Similarity.MANHATTAN, 2.0 / 3.0),
    ],
)
def test_scalar_metrics_match_expected_scores(metric: Similarity, expected: float) -> None:
    left = np.asarray([1.0, 1.0, 0.0])
    right = np.asarray([1.0, 0.0, 1.0])
    if metric is Similarity.MANHATTAN:
        left = np.asarray([0.0, 1.0])
        right = np.asarray([1.0, 1.0])

    assert similarity_score(left, right, metric) == pytest.approx(expected)


@pytest.mark.parametrize('metric', [Similarity.JACCARD, Similarity.DICE])
def test_set_metrics_return_zero_for_empty_vectors(metric: Similarity) -> None:
    values = np.zeros(3)

    assert similarity_score(values, values, metric) == 0.0


def test_coverage_and_dice_handle_sequences_and_empty_candidates() -> None:
    source = frozenset({'a', 'b', 'c'})

    assert coverage(source, ['a', 'c', 'extra']) == pytest.approx(2.0 / 3.0)
    assert dice(source, ['a', 'c', 'extra']) == pytest.approx(2.0 / 3.0)
    assert coverage(source, ()) == 0.0
    assert dice(source, None) == 0.0


@pytest.mark.parametrize(
    ('metric', 'expected'),
    [
        (Similarity.JACCARD, np.asarray([1.0 / 3.0, 0.0])),
        (Similarity.DICE, np.asarray([0.5, 0.0])),
        (Similarity.TVERSKY, np.asarray([0.5, 0.0])),
    ],
)
def test_vectorized_set_metrics_match_scalar_definitions(metric: Similarity, expected: np.ndarray) -> None:
    operands = SimilarityOperands(
        intersections=np.asarray([1.0, 0.0]),
        left_sizes=np.asarray([2.0, 0.0]),
        right_sizes=np.asarray([2.0, 0.0]),
    )

    np.testing.assert_allclose(vectorized_similarity(metric, operands), expected)


def test_vectorized_manhattan_matches_scalar_definition() -> None:
    operands = SimilarityOperands(differences=np.asarray([[1.0, 0.0], [2.0, 2.0]]))

    np.testing.assert_allclose(
        vectorized_similarity(Similarity.MANHATTAN, operands),
        np.asarray([2.0 / 3.0, 1.0 / 3.0]),
    )
