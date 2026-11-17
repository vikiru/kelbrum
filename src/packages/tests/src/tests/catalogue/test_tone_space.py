"""Tests for continuous tonal coordinate and smooth distance penalties."""

import pytest

from anime_catalogue.tags import Tag
from anime_catalogue.taxonomy import Genre, Theme
from anime_catalogue.tone_space import (
    FATAL_TONAL_DISTANCE_THRESHOLD,
    compute_tonal_coordinate,
    compute_tonal_scoring_multiplier,
    is_fatal_tonal_contradiction,
)


def test_pure_dark_anchor_computes_deep_negative_coordinate() -> None:
    # Texhnolyze / Higurashi archetype
    tokens = {Genre.HORROR, Theme.GORE, Tag.BLEAK, Tag.BODY_HORROR}
    coord = compute_tonal_coordinate(tokens)
    assert coord <= -0.80


def test_pure_gag_comedy_computes_high_positive_coordinate() -> None:
    # Nichijou / Pop Team Epic archetype
    tokens = {Genre.COMEDY, Theme.GAG_HUMOR, Tag.ABSURDIST}
    coord = compute_tonal_coordinate(tokens)
    assert coord >= +0.70


def test_multi_tonal_title_self_balances() -> None:
    # Steins;Gate archetype: Suspense + Drama + Comedy banter
    tokens = {Genre.SUSPENSE, Genre.DRAMA, Theme.PSYCHOLOGICAL, Genre.COMEDY}
    coord = compute_tonal_coordinate(tokens)
    # Balanced negative-leaning drama/suspense
    assert -0.60 <= coord <= -0.20


def test_fatal_tonal_distance_detection() -> None:
    dark_coord = -0.85
    gag_coord = +0.80
    assert abs(dark_coord - gag_coord) > FATAL_TONAL_DISTANCE_THRESHOLD
    assert is_fatal_tonal_contradiction(dark_coord, gag_coord) is True

    # Steins;Gate (-0.35) vs standard Drama (-0.35)
    assert is_fatal_tonal_contradiction(-0.35, -0.35) is False
    # Steins;Gate (-0.35) vs light comedy (+0.50) -> delta = 0.85 < 1.35
    assert is_fatal_tonal_contradiction(-0.35, +0.50) is False


def test_smooth_scoring_multiplier_decays_exponentially() -> None:
    # Identical tone
    assert compute_tonal_scoring_multiplier(-0.4, -0.4) == pytest.approx(1.0)

    # Moderate distance
    mult_mod = compute_tonal_scoring_multiplier(-0.4, 0.0)
    assert 0.70 <= mult_mod <= 0.80

    # Large distance
    mult_large = compute_tonal_scoring_multiplier(-0.8, +0.4)
    assert mult_large < 0.10


def test_cross_enum_tokens_do_not_collide_in_tone_lookup() -> None:
    assert compute_tonal_coordinate((Genre.SLICE_OF_LIFE,)) > 0.0
    assert compute_tonal_coordinate((Theme.SLICE_OF_LIFE,)) == 0.0
