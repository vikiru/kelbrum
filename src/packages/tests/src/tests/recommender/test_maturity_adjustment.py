from recommender.maturity_adjustment import weak_maturity_penalty
from recommender.rating_policy import RatingClass


def test_penalizes_weak_lower_rated_pg13_match() -> None:
    assert weak_maturity_penalty(RatingClass.PG_13, RatingClass.G, (), ('time_travel',), 0.1) == 0.02


def test_preserves_strong_lower_rated_match() -> None:
    assert weak_maturity_penalty(RatingClass.PG_13, RatingClass.G, ('drama', 'sci_fi'), ('time_travel',), 0.1) == 0.0


def test_preserves_lower_rated_match_with_strong_semantic_evidence() -> None:
    assert weak_maturity_penalty(RatingClass.PG_13, RatingClass.PG, (), (), 0.8) == 0.0


def test_does_not_penalize_mature_sources() -> None:
    assert weak_maturity_penalty(RatingClass.R, RatingClass.G, (), (), 0.0) == 0.0
