import pytest

from export.labels import display_label
from processing.canonicalize import clean_synopsis, duration_to_minutes
from processing.eligibility import EligibilityPolicy
from processing.identity import processing_artifact_identity
from processing.labels import normalize_label
from processing.ratings import display_rating
from processing.theme_corrections import (
    MANUAL_THEME_ADDITIONS,
    ThemeCorrection,
    ThemeCorrectionRegistry,
    theme_correction_registry_identity,
)


def test_clean_synopsis_normalizes_whitespace_and_missing_values() -> None:
    assert clean_synopsis('  A quiet\n forest   adventure. ') == 'A quiet forest adventure.'
    assert clean_synopsis('A boxing story. (Source: ANN)') == 'A boxing story.'
    assert clean_synopsis('A fantasy story. Source: Official Website') == 'A fantasy story.'
    assert clean_synopsis('A mystery story. [Written by MAL Rewrite]') == 'A mystery story.'
    assert clean_synopsis(None) is None
    assert clean_synopsis('   ') is None
    assert clean_synopsis('A resource: the story continues.') == 'A resource: the story continues.'


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


def test_processing_artifact_identity_changes_for_each_semantic_input() -> None:
    def artifact_identity(
        *,
        source_sha256: str = 'source-a',
        theme: str = 'Mecha',
        policy_identity: str = 'eligibility-v2',
    ) -> str:
        return processing_artifact_identity(
            source_sha256=source_sha256,
            policy=EligibilityPolicy(),
            theme_additions={10: (theme,)},
            tagged_anime_ids=(20,),
            policy_identity=policy_identity,
        )

    assert artifact_identity() == artifact_identity()
    assert artifact_identity(source_sha256='source-b') != artifact_identity()
    assert artifact_identity(theme='Sports') != artifact_identity()
    assert artifact_identity(policy_identity='eligibility-v3') != artifact_identity()


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


def test_theme_corrections_are_typed_and_validated_resources() -> None:
    assert isinstance(MANUAL_THEME_ADDITIONS[0], ThemeCorrection)
    assert theme_correction_registry_identity() == theme_correction_registry_identity()
    assert theme_correction_registry_identity.cache_info().hits >= 1
    with pytest.raises(ValueError, match='IDs must be positive'):
        ThemeCorrection(anime_ids=(0,), themes=('Theme',))


def test_theme_registry_identity_changes_with_corrections() -> None:
    first = ThemeCorrectionRegistry('v1', (ThemeCorrection((1,), ('Theme',)),))
    second = ThemeCorrectionRegistry('v1', (ThemeCorrection((2,), ('Theme',)),))

    assert first.identity() != second.identity()
