import pytest

from processing.ratings import RatingPolicy, display_rating, normalize_rating


def test_general_audience_anchors_share_one_compatibility_ceiling() -> None:
    policy = RatingPolicy()

    for parent in ('G', 'PG', 'PG-13'):
        for candidate in ('G', 'PG', 'PG-13'):
            assert policy.evaluate(parent, candidate).allowed
        assert not policy.evaluate(parent, 'R').allowed
        assert not policy.evaluate(parent, 'R+').allowed


def test_mature_anchors_can_recommend_all_cleaned_rating_classes() -> None:
    policy = RatingPolicy()

    for parent in ('R', 'R+'):
        for candidate in ('G', 'PG', 'PG-13', 'R', 'R+'):
            assert policy.evaluate(parent, candidate).allowed


@pytest.mark.parametrize(
    ('raw_rating', 'normalized', 'display'),
    [
        ('G - All Ages', 'G', 'G'),
        ('PG - Children', 'PG', 'PG'),
        ('PG-13 - Teens 13 or older', 'PG_13', 'PG-13'),
        ('R - 17+ (violence & profanity)', 'R', 'R'),
        ('R+ - Mild Nudity', 'R_PLUS', 'R+'),
        ('None', 'UNKNOWN', 'Unknown'),
    ],
)
def test_catalogue_rating_strings_normalize_to_stable_classes(raw_rating: str, normalized: str, display: str) -> None:
    assert normalize_rating(raw_rating).value == normalized
    assert display_rating(raw_rating) == display


def test_unknown_rating_fails_closed() -> None:
    decision = RatingPolicy().evaluate('G', None)

    assert not decision.allowed
    assert decision.reason == 'unknown_rating_fail_closed'
