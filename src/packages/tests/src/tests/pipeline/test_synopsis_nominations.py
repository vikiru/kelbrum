from fetch.contracts import TenraiAnimeEntry
from pipeline.synopsis_nominations import SynopsisNominationRule, nominate_synopsis_tags


def test_synopsis_nominations_return_reviewable_evidence() -> None:
    entries = (
        TenraiAnimeEntry(
            mal_id=1,
            title='Loop Story',
            synopsis='A student awakens to the same day and searches for a way to break the time loop.',
        ),
        TenraiAnimeEntry(mal_id=2, title='No Synopsis'),
    )

    nominations = nominate_synopsis_tags(
        entries,
        (SynopsisNominationRule('time_loop', ('time loop', 'same day')),),
    )

    assert len(nominations) == 1
    assert nominations[0].anime_id == 1
    assert nominations[0].tag_id == 'time_loop'
    assert nominations[0].matched_terms == ('time loop', 'same day')
    assert 'time loop' in nominations[0].evidence.casefold()


def test_synopsis_nominations_are_deterministic_and_skip_existing_empty_text() -> None:
    entries = (TenraiAnimeEntry(mal_id=2, title='No Synopsis', synopsis='  '),)
    rule = SynopsisNominationRule('revenge', ('revenge',))

    assert nominate_synopsis_tags(entries, (rule,)) == ()
