from recommender.contracts import RawRecommendation
from recommender.maturity_adjustment import weak_maturity_penalty
from recommender.rating_policy import RatingClass
from recommender.surfacing import SurfacingPolicy


def test_penalizes_weak_lower_rated_pg13_match() -> None:
    assert weak_maturity_penalty(RatingClass.PG_13, RatingClass.G, (), ('time_travel',), 0.1) == 0.02


def test_preserves_strong_lower_rated_match() -> None:
    assert weak_maturity_penalty(RatingClass.PG_13, RatingClass.G, ('drama', 'sci_fi'), ('time_travel',), 0.1) == 0.0


def test_preserves_lower_rated_match_with_strong_semantic_evidence() -> None:
    assert weak_maturity_penalty(RatingClass.PG_13, RatingClass.PG, (), (), 0.8) == 0.0


def test_does_not_penalize_mature_sources() -> None:
    assert weak_maturity_penalty(RatingClass.R, RatingClass.G, (), (), 0.0) == 0.0


def test_surfacing_policy_floor_boundary_regression() -> None:
    """Verify that surfacing score floor is strictly evaluated on final matured scores."""
    policy = SurfacingPolicy(minimum_score=0.20, maximum_results=10)

    items = [
        RawRecommendation(
            anime_id=1,
            score=0.2000,
            witness_member_id=1,
            retrieval_paths=(),
            semantic_available=True,
            categorical_available=True,
        ),
        RawRecommendation(
            anime_id=2,
            score=0.1999,
            witness_member_id=2,
            retrieval_paths=(),
            semantic_available=True,
            categorical_available=True,
        ),
        RawRecommendation(
            anime_id=3,
            score=0.2001,
            witness_member_id=3,
            retrieval_paths=(),
            semantic_available=True,
            categorical_available=True,
        ),
    ]

    surfaced = policy.surface(items)
    surfaced_ids = [item.anime_id for item in surfaced]

    assert 1 in surfaced_ids, 'Item exactly on floor (0.2000) must be retained'
    assert 3 in surfaced_ids, 'Item above floor (0.2001) must be retained'
    assert 2 not in surfaced_ids, 'Item below floor (0.1999) must be discarded'
