from pathlib import Path

import polars as pl
import pytest

from export.labels import display_label
from fetch.contracts import Taxonomy, TenraiAnimeEntry
from normalization.metadata import MetadataState
from processing.canonicalize import canonicalize, clean_synopsis, duration_to_minutes
from processing.eligibility import EligibilityPolicy
from processing.excluded_ids import EXCLUDED_IDS
from processing.identity import processing_artifact_identity
from processing.labels import normalize_label
from processing.metadata_corrections import (
    ThemeCorrection,
    ThemeCorrectionRegistry,
    get_manual_theme_additions,
    load_manual_theme_corrections,
    theme_correction_registry_identity,
)
from processing.persistence import _canonical_from_row
from processing.ratings import display_rating
from processing.synopsis import feature_synopsis_column


@pytest.mark.parametrize(
    'synopsis',
    [
        'A story. Source: ANN, Moon Phase',
        'A story. Source: (themoviedb.org)',
        'A story. Source: (letterboxd.com)',
    ],
)
def test_clean_synopsis_removes_trailing_source_citations(synopsis: str) -> None:
    assert clean_synopsis(synopsis) == 'A story.'


def test_clean_synopsis_normalizes_whitespace_and_missing_values() -> None:
    assert clean_synopsis('  A quiet\n forest   adventure. ') == 'A quiet forest adventure.'
    assert clean_synopsis('A boxing story. (Source: ANN)') == 'A boxing story.'
    assert clean_synopsis('A fantasy story. Source: Official Website') == 'A fantasy story.'
    assert clean_synopsis('A mystery story. [Written by MAL Rewrite]') == 'A mystery story.'
    assert clean_synopsis('A story. [Written by Example]') == 'A story.'
    assert clean_synopsis('A story. (Source: ANN) About Example (U.S.)') == 'A story.'
    assert clean_synopsis(None) is None
    assert clean_synopsis('   ') is None
    assert clean_synopsis('A resource: the story continues.') == 'A resource: the story continues.'
    assert (
        clean_synopsis('A quiet tale. [Written by Example] source: the center of the planet')
        == 'A quiet tale. source: the center of the planet'
    )
    assert clean_synopsis('The relic is sent to its source: the center of the planet.') == (
        'The relic is sent to its source: the center of the planet.'
    )


def test_feature_synopsis_scalar_and_column_cleaning_agree() -> None:
    values = [
        'A story. Source: ANN, Moon Phase',
        'A story. Source: (themoviedb.org)',
        'A story. Source: (letterboxd.com)',
        'A premise. source: the center of the planet',
        None,
    ]
    frame = feature_synopsis_column(pl.DataFrame({'synopsis': values}))

    assert frame['synopsis_features'].to_list() == [
        canonicalize(TenraiAnimeEntry(mal_id=index + 1, title='Example', synopsis=value)).synopsis_features
        for index, value in enumerate(values)
    ]


def test_canonicalization_preserves_metadata_unknown_absent_and_observed_states() -> None:
    unknown = canonicalize(TenraiAnimeEntry(mal_id=10, title='Unknown'))
    absent = canonicalize(TenraiAnimeEntry(mal_id=11, title='Absent', genres=[]))
    observed = canonicalize(
        TenraiAnimeEntry(mal_id=12, title='Observed', genres=[Taxonomy(1, 'Drama')], synopsis='Story')
    )

    assert unknown.genres_state.value == 'UNKNOWN'
    assert absent.genres_state.value == 'OBSERVED_ABSENT'
    assert observed.genres_state.value == 'OBSERVED'
    assert unknown.synopsis_state.value == 'UNKNOWN'
    assert observed.synopsis_state.value == 'OBSERVED'


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
        ('10 sec', 0),
        ('10 sec per ep', 0),
        ('90 secs', 1),
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
    assert isinstance(get_manual_theme_additions()[0], ThemeCorrection)
    assert theme_correction_registry_identity() == theme_correction_registry_identity()
    assert theme_correction_registry_identity.cache_info().hits >= 1
    with pytest.raises(ValueError, match='IDs must be positive'):
        ThemeCorrection(anime_ids=(0,), themes=('Theme',))


def test_theme_registry_identity_changes_with_corrections() -> None:
    first = ThemeCorrectionRegistry('v1', (ThemeCorrection((1,), ('Theme',)),))
    second = ThemeCorrectionRegistry('v1', (ThemeCorrection((2,), ('Theme',)),))

    assert first.identity() != second.identity()


def test_theme_correction_allows_removal_only_and_excludes_excluded_ids() -> None:
    removal_only = ThemeCorrection(anime_ids=(1,), themes=(), remove_themes=('School',))
    assert removal_only.remove_themes == ('School',)

    corrected_ids = {anime_id for correction in get_manual_theme_additions() for anime_id in correction.anime_ids}
    assert corrected_ids.isdisjoint(EXCLUDED_IDS)


def test_load_manual_theme_corrections_validates_headers_and_normalizes_labels(tmp_path: Path) -> None:
    bad_csv = tmp_path / 'bad.csv'
    bad_csv.write_text('source id,manual_genres\n1,Action\n', encoding='utf-8')
    with pytest.raises(ValueError, match='must contain source id, manual_genres, and manual_themes'):
        load_manual_theme_corrections(bad_csv)

    valid_csv = tmp_path / 'valid.csv'
    valid_csv.write_text('source id,manual_genres,manual_themes\n10,Sci-Fi,Time Travel\n', encoding='utf-8')
    corrections = load_manual_theme_corrections(valid_csv)
    assert any(c.genres == ('sci_fi',) and 10 in c.anime_ids for c in corrections)
    assert any(c.themes == ('time_travel',) and 10 in c.anime_ids for c in corrections)


def test_canonical_from_row_populates_tags_state() -> None:
    record = _canonical_from_row(
        {
            'mal_id': 1,
            'title': 'Test',
            'genres': [],
            'themes': [],
            'demographics': [],
            'tags_state': MetadataState.OBSERVED.value,
        }
    )
    assert record.tags_state is MetadataState.OBSERVED
