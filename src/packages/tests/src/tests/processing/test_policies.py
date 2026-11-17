from anime_catalogue.taxonomy import Theme
from fetch.contracts import TenraiAnimeEntry
from processing.build import build_canonical
from processing.eligibility import (
    EligibilityPolicy,
    ExclusionReason,
    filter_entries,
    filter_non_recommendable_content,
)
from processing.excluded_ids import EXCLUDED_IDS
from processing.ratings import display_rating
from recommender.rating_policy import RatingPolicy


def test_ona_cleanup_respects_manual_tags_and_applies_theme_corrections_before_eligibility() -> None:
    entries = [
        TenraiAnimeEntry(mal_id=1, title='Tagged ONA', type='ONA', duration='30 min'),
        TenraiAnimeEntry(mal_id=2, title='Corrected ONA', type='ONA', duration='30 min'),
        TenraiAnimeEntry(mal_id=3, title='Short ONA', type='ONA', duration='10 min'),
        TenraiAnimeEntry(mal_id=4, title='Promotional Trailer ONA', type='ONA', duration='30 min'),
    ]

    result = build_canonical(
        entries,
        EligibilityPolicy(
            require_primary_image=False,
            require_semantic_evidence=True,
            excluded_genre_ids=frozenset(),
        ),
        tagged_anime_ids={1, 3, 4},
        theme_additions={2: (Theme.ISEKAI,)},
    )

    assert {record.mal_id for record in result.records} == {1, 2}
    assert set(dict(result.audit.reasons_by_id)) >= {3, 4}


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


def test_unknown_rating_policy_uses_conservative_maturity_ceiling() -> None:
    policy = RatingPolicy()

    assert not policy.evaluate('G', None).allowed
    assert policy.evaluate('R', None).allowed
    assert policy.evaluate('UNKNOWN', None).allowed
    assert not policy.evaluate('UNKNOWN', 'Rx').allowed


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


def test_filter_non_recommendable_content_rejects_curated_exclusions() -> None:
    sample_id = next(iter(EXCLUDED_IDS))
    entries = [
        TenraiAnimeEntry(mal_id=sample_id, title='Excluded Sample', type='TV'),
        TenraiAnimeEntry(mal_id=9999999, title='Valid Narrative', type='TV'),
    ]

    accepted, rejected = filter_non_recommendable_content(entries)

    assert len(accepted) == 1
    assert accepted[0].mal_id == 9999999
    assert rejected[sample_id] == ExclusionReason.CURATED_EXCLUSION
