from recommender.scoring import score_candidates
from recommender.union import PathEvidence, UnionCandidate


def test_normalized_structured_correction_is_opt_in_and_deterministic() -> None:
    candidates = (
        UnionCandidate(2, (PathEvidence('genres', 1, 1.0),)),
        UnionCandidate(3, (PathEvidence('genres', 2, 0.9),)),
    )
    values = {
        1: frozenset({'Action', 'Fantasy'}),
        2: frozenset({'Action', 'Fantasy'}),
        3: frozenset({'Comedy'}),
    }

    baseline = score_candidates(
        1,
        candidates,
        genres_by_id=values,
        themes_by_id={1: frozenset(), 2: frozenset(), 3: frozenset()},
        tags_by_id={},
        demographics_by_id={},
    )
    corrected = score_candidates(
        1,
        candidates,
        genres_by_id=values,
        themes_by_id={1: frozenset(), 2: frozenset(), 3: frozenset()},
        tags_by_id={},
        demographics_by_id={},
        normalized_structured_correction=True,
    )

    assert tuple(item[0] for item in baseline) == (2, 3)
    assert tuple(item[0] for item in corrected) == (2, 3)
    assert corrected[0][2] > baseline[0][2]
