from fetch.contracts import TenraiAnimeEntry
from processing.eligibility import EligibilityPolicy, filter_entries
from processing.ratings import display_rating
from recommender.rating_policy import RatingPolicy


def test_rating_policy_is_asymmetric_by_maturity_level() -> None:
    policy = RatingPolicy()

    assert policy.evaluate('G', 'PG').allowed
    assert policy.evaluate('G', 'PG-13').allowed
    assert policy.evaluate('PG-13', 'G').allowed
    assert policy.evaluate('PG-13', 'PG').allowed
    assert policy.evaluate('R+', 'R').allowed
    assert not policy.evaluate('G', 'R').allowed
    assert not policy.evaluate('PG-13', 'R+').allowed
    assert display_rating('R - 17+ (violence & profanity)') == 'R'


def test_unknown_rating_fails_closed() -> None:
    decision = RatingPolicy().evaluate('G', None)

    assert not decision.allowed
    assert decision.reason == 'unknown_rating_fail_closed'


def test_filter_audit_is_deterministic_and_reports_each_rule() -> None:
    entries = [
        TenraiAnimeEntry(mal_id=20, title='Future', type='TV', year=2030),
        TenraiAnimeEntry(mal_id=5, title='Missing', type='Movie'),
    ]
    policy = EligibilityPolicy(require_primary_image=False, require_semantic_evidence=False, max_year=2027)

    accepted, audit = filter_entries(entries, policy)

    assert accepted == [entries[1]]
    assert audit.rejected_ids == (20,)
    assert audit.reasons_by_rule == (('year_after_cutoff', 1),)
