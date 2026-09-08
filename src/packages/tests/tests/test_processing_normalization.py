import pytest

from models.labels import display_label, normalize_label
from processing.canonicalize import clean_synopsis, duration_to_minutes
from processing.ratings import display_rating


def test_clean_synopsis_normalizes_whitespace_and_missing_values() -> None:
    assert clean_synopsis('  A quiet\n forest   adventure. ') == 'A quiet forest adventure.'
    assert clean_synopsis(None) is None
    assert clean_synopsis('   ') is None


@pytest.mark.parametrize(
    ('raw_label', 'normalized', 'display'),
    [
        ('Slice of Life', 'slice_of_life', 'Slice of Life'),
        ('Award Winning', 'award_winning', 'Award Winning'),
        ('sci_fi', 'sci_fi', 'Sci-Fi'),
    ],
)
def test_taxonomy_labels_have_stable_internal_and_display_forms(raw_label: str, normalized: str, display: str) -> None:
    assert normalize_label(raw_label) == normalized
    assert display_label(normalized) == display


@pytest.mark.parametrize('rating', ['G', 'PG', 'PG-13', 'R', 'R+'])
def test_rating_display_values_remain_canonical(rating: str) -> None:
    assert display_rating(rating) == rating


@pytest.mark.parametrize(
    ('raw_duration', 'expected_minutes'),
    [
        ('1 hr 26 min', 86),
        ('1 hr 1 min per ep', 61),
        ('24 mins', 24),
        ('24 min per ep', 24),
        ('2 hrs', 120),
        ('2 hr per ep', 120),
        ('10 sec', None),
        ('10 sec per ep', None),
        ('Unknown', None),
        ('Not available', None),
        (None, None),
    ],
)
def test_duration_to_minutes_handles_catalogue_duration_families(
    raw_duration: str | None, expected_minutes: int | None
) -> None:
    assert duration_to_minutes(raw_duration) == expected_minutes
