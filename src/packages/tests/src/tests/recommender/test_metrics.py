from recommender.metrics import TVERSKY_ALPHA, TVERSKY_BETA, Similarity, tversky


def test_tversky_is_registered_as_a_shared_similarity_type() -> None:
    assert Similarity.TVERSKY.value == 'tversky'
    assert TVERSKY_ALPHA == 0.7
    assert TVERSKY_BETA == 0.3


def test_tversky_is_asymmetric_with_default_parameters() -> None:
    assert tversky({'genre'}, {'genre', 'extra'}) == 1.0 / 1.3
    assert tversky({'genre', 'extra'}, {'genre'}) == 1.0 / 1.7


def test_tversky_returns_zero_for_empty_sets() -> None:
    assert tversky(set(), set()) == 0.0
