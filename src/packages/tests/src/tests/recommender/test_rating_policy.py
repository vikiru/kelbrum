import pytest

from normalization.metadata import MetadataState
from normalization.ratings import rating_metadata_state
from processing.ratings import display_rating, normalize_rating
from recommender.rating_policy import RatingClass, RatingPolicy


def test_rating_class_preserves_each_normalized_rating_value() -> None:
    assert tuple(item.value for item in RatingClass) == ('UNKNOWN', 'G', 'PG', 'PG_13', 'R', 'R_PLUS', 'R_X')


def test_general_audience_anchors_share_one_compatibility_ceiling() -> None:
    policy = RatingPolicy()

    # G and PG (Children / All Ages): Never allowed to recommend R or R+
    for parent in ('G', 'PG'):
        for candidate in ('G', 'PG', 'PG-13'):
            assert policy.evaluate(parent, candidate).allowed
        assert not policy.evaluate(parent, 'R').allowed
        assert not policy.evaluate(parent, 'R+').allowed

    # PG-13 (Teens): Adult demographic sources (Seinen, Josei) also admit R+ candidates.
    for candidate in ('G', 'PG', 'PG-13', 'R'):
        assert policy.evaluate('PG-13', candidate).allowed
    assert not policy.evaluate('PG-13', 'R+').allowed
    assert policy.evaluate('PG-13', 'R+', parent_demographics=['Seinen']).allowed
    assert policy.evaluate('PG-13', 'R+', parent_demographics=['Josei']).allowed


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
        ('PG-13', 'PG_13', 'PG-13'),
        ('R+', 'R_PLUS', 'R+'),
        ('PG_13', 'PG_13', 'PG-13'),
        ('R_PLUS', 'R_PLUS', 'R+'),
        ('R_X', 'R_X', 'Rx'),
        ('Rx', 'R_X', 'Rx'),
        ('None', 'UNKNOWN', 'Unknown'),
    ],
)
def test_catalogue_rating_strings_normalize_to_stable_classes(raw_rating: str, normalized: str, display: str) -> None:
    assert normalize_rating(raw_rating).value == normalized
    assert display_rating(raw_rating) == display


@pytest.mark.parametrize('raw_rating', ['Rubbish', 'Random', 'GARBAGE', 'General', 'PG nonsense', 'RXjunk'])
def test_unknown_rating_near_matches_remain_unknown(raw_rating: str) -> None:
    assert normalize_rating(raw_rating).value == 'UNKNOWN'
    assert rating_metadata_state(raw_rating) is MetadataState.UNKNOWN


@pytest.mark.parametrize(
    ('parent', 'candidate', 'allowed'),
    [
        ('UNKNOWN', 'G', True),
        ('UNKNOWN', 'PG', True),
        ('UNKNOWN', 'PG-13', True),
        ('UNKNOWN', 'R', True),
        ('UNKNOWN', 'R+', False),
        ('UNKNOWN', 'Rx', False),
        ('UNKNOWN', None, True),
        ('G', None, False),
        ('PG', 'UNKNOWN', False),
        ('PG-13', 'UNKNOWN', True),
        ('R', 'UNKNOWN', True),
        ('R+', 'UNKNOWN', True),
        ('Rx', 'UNKNOWN', True),
        ('R', 'Rx', True),
        ('R+', 'Rx', True),
    ],
)
def test_unknown_rating_uses_asymmetric_maturity_compatibility(
    parent: str | None,
    candidate: str | None,
    allowed: bool,
) -> None:
    assert RatingPolicy.baseline_a().evaluate(parent, candidate).allowed is allowed


def test_unknown_rating_decisions_explain_the_exclusion_rule() -> None:
    policy = RatingPolicy()

    assert policy.evaluate('UNKNOWN', 'PG-13').reason == 'retained'
    assert policy.evaluate('UNKNOWN', 'R+').reason == 'explicit_content_excluded'
    assert policy.evaluate('PG', 'UNKNOWN').reason == 'unknown_candidate_requires_teen_or_mature_anchor'
    assert policy.evaluate('UNKNOWN', 'Rx').reason == 'explicit_content_excluded'


def test_policy_d_cond_hard_exclusion_ceilings() -> None:
    policy = RatingPolicy.policy_d_cond()

    # Universal Rx exclusion
    assert not policy.evaluate('R', 'Rx').allowed
    assert not policy.evaluate('PG-13', 'Rx').allowed
    assert not policy.evaluate('G', 'Rx').allowed
    assert policy.multiplier('R', 'Rx') == 0.0

    # Children anchor ceilings
    assert not policy.evaluate('G', 'R').allowed
    assert not policy.evaluate('PG', 'R+').allowed
    assert policy.multiplier('G', 'R') == 0.0

    # PG-13 anchor ceilings
    assert not policy.evaluate('PG-13', 'R+').allowed
    assert policy.multiplier('PG-13', 'R+') == 0.0
    assert policy.evaluate('PG-13', 'R+', parent_demographics=['Seinen']).allowed
    assert policy.multiplier('PG-13', 'R+', parent_demographics=['seinen']) == 1.0


def test_policy_d_cond_base_cohort_multipliers() -> None:
    policy = RatingPolicy.policy_d_cond()

    # PG-13 -> General G/PG non-Kids: 0.95x
    assert policy.multiplier('PG-13', 'G', candidate_demographics=['Shounen']) == 0.95
    assert policy.multiplier('PG-13', 'PG') == 0.95

    # Mature -> General G/PG non-Kids: 0.60x
    assert policy.multiplier('R', 'G') == 0.60
    assert policy.multiplier('R+', 'PG') == 0.60

    # G/PG -> PG-13: 0.90x
    assert policy.multiplier('G', 'PG-13') == 0.90
    assert policy.multiplier('PG', 'PG-13') == 0.90

    # Peer cohorts: 1.00x
    assert policy.multiplier('PG-13', 'PG-13') == 1.00
    assert policy.multiplier('PG-13', 'R') == 1.00
    assert policy.multiplier('R', 'R') == 1.00
    assert policy.multiplier('R', 'PG-13') == 1.00
    assert policy.multiplier('G', 'G') == 1.00


def test_policy_d_cond_conditional_narrative_kids_multipliers() -> None:
    policy = RatingPolicy.policy_d_cond()

    # PG-13 -> G/PG Kids Strong (shared theme): 0.76x (0.95 * 0.80)
    assert (
        policy.multiplier(
            'PG-13',
            'G',
            candidate_demographics=['Kids'],
            shared_themes=['Super Power'],
        )
        == 0.76
    )

    # PG-13 -> G/PG Kids Strong (dense cosine >= 0.45): 0.76x
    assert (
        policy.multiplier(
            'PG-13',
            'PG',
            candidate_demographics=['Kids'],
            dense_cosine=0.48,
        )
        == 0.76
    )

    # PG-13 -> G/PG Kids Weak (no shared tags/themes, low dense cosine): 0.57x (0.95 * 0.60)
    assert (
        policy.multiplier(
            'PG-13',
            'G',
            candidate_demographics=['Kids'],
            dense_cosine=0.25,
        )
        == 0.57
    )

    # Mature -> G/PG Kids Strong: 0.48x (0.60 * 0.80)
    assert (
        policy.multiplier(
            'R',
            'G',
            candidate_demographics=['Kids'],
            shared_themes=['Demons'],
        )
        == 0.48
    )

    # Mature -> G/PG Kids Weak: 0.36x (0.60 * 0.60)
    assert (
        policy.multiplier(
            'R',
            'G',
            candidate_demographics=['Kids'],
        )
        == 0.36
    )

    # PG-13 -> PG-13 Kids strong match: 0.90x (1.00 * 0.90)
    assert (
        policy.multiplier(
            'PG-13',
            'PG-13',
            candidate_demographics=['Kids'],
            shared_themes=['Adventure'],
        )
        == 0.90
    )

    # PG-13 -> PG-13 Kids Weak: 0.60x (1.00 * 0.60)
    assert (
        policy.multiplier(
            'PG-13',
            'PG-13',
            candidate_demographics=['Kids'],
        )
        == 0.60
    )


def test_policy_d_cond_unannotated_demographic_fallback() -> None:
    policy = RatingPolicy.policy_d_cond()

    # Empty demographic list -> neutral fallback, base rating multiplier only
    assert policy.multiplier('PG-13', 'G', candidate_demographics=[]) == 0.95
    assert policy.multiplier('R', 'G', candidate_demographics=None) == 0.60
    assert policy.multiplier('PG-13', 'PG-13', candidate_demographics=[]) == 1.00


def test_baseline_a_fallback_preserves_unpenalized_scores() -> None:
    baseline = RatingPolicy.baseline_a()

    assert baseline.name == 'rating-compatibility-v6'
    assert baseline.identity == 'rating-compatibility-v6:baseline_a'


def test_rating_policy_identity_includes_effective_mode() -> None:
    baseline = RatingPolicy(mode='baseline_a', name='shared')
    conditional = RatingPolicy(mode='policy_d_cond', name='shared')

    assert baseline.identity != conditional.identity
    assert baseline.multiplier('PG-13', 'G', candidate_demographics=['Kids']) == 1.00
    assert baseline.multiplier('R', 'G', candidate_demographics=['Kids']) == 1.00
    assert baseline.multiplier('G', 'PG-13') == 1.00
