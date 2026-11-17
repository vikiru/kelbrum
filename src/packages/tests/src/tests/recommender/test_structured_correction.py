import pytest

from recommender.scoring import (
    ScoringProperty,
    fuse_synopsis_scores,
    make_idf_tversky,
    score_candidates,
    sigmoid_embedding_gate,
)
from recommender.union import PathEvidence, UnionCandidate


def test_production_scoring_v3_2_rewards_structured_overlap_and_is_pool_invariant() -> None:
    candidate_2 = UnionCandidate(2, (PathEvidence('embedding', 1, 0.6),))
    candidate_3 = UnionCandidate(3, (PathEvidence('embedding', 2, 0.6),))
    genres = {1: ('Action',), 2: ('Action',), 3: ('Comedy',)}
    themes = {1: ('School',), 2: ('School',), 3: ('Sports',)}

    scores = score_candidates(
        1,
        (candidate_2, candidate_3),
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
    )

    scores_by_id = {recommendation_entity_id: score for recommendation_entity_id, _, score, _ in scores}
    assert scores_by_id[2] > scores_by_id[3]
    # Candidate 3 has no structured overlap (genres/themes disjoint), only embedding evidence (1 group).
    expected_c3 = 0.41 * fuse_synopsis_scores(0.0, 0.0, sigmoid_embedding_gate(0.6))
    assert scores_by_id[3] == pytest.approx(expected_c3)

    # Test pool invariance: candidate 3 score is identical when scored alone without candidate 2 in pool
    isolated_scores = score_candidates(
        1,
        (candidate_3,),
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
    )
    assert isolated_scores[0][2] == pytest.approx(scores_by_id[3])


def test_cross_group_confidence_multipliers() -> None:
    # 1 group (semantic only): R_cross = 0 -> 1.00
    c_1_group = UnionCandidate(2, (PathEvidence('bm25', 1, 0.9),))
    # 2 groups (semantic + structured): R_cross = 1 -> 1.04
    c_2_groups = UnionCandidate(3, (PathEvidence('bm25', 1, 0.9), PathEvidence('genres', 1, 0.9)))
    # 3 groups (semantic + structured + neighbourhood): R_cross = 2 -> 1.08
    c_3_groups = UnionCandidate(
        4,
        (
            PathEvidence('bm25', 1, 0.9),
            PathEvidence('genres', 1, 0.9),
            PathEvidence('weighted-v2', 1, 0.9),
        ),
    )

    scores = score_candidates(
        1,
        (c_1_group, c_2_groups, c_3_groups),
        genres_by_id={},
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={},
        properties=(),
        synopsis_scoring_paths=('bm25', 'lsa', 'embedding'),
    )
    s_map = {item[0]: item[2] for item in scores}
    base_synopsis = 0.41 * fuse_synopsis_scores(0.9, 0.0, 0.0)
    assert s_map[2] == pytest.approx(base_synopsis * 1.00)
    assert s_map[3] == pytest.approx(base_synopsis * 1.04)
    assert s_map[4] == pytest.approx(base_synopsis * 1.08)


def test_char_tfidf_cross_group_semantics_and_intrinsic_ble_exclusion() -> None:
    """Test candidate retrieved ONLY by char-TFIDF -> Semantic group present.

    Candidate retrieved by char-TFIDF + Themes -> Semantic + Structured -> R_cross=1 -> 1.04.
    Char-TFIDF similarity itself does NOT enter IntrinsicBLE.
    """
    # Candidate 2: retrieved ONLY by char-TFIDF
    c_char_only = UnionCandidate(2, (PathEvidence('char_3_5g_tfidf', 1, 0.95),))
    # Candidate 3: retrieved by char-TFIDF + Themes
    c_char_themes = UnionCandidate(
        3,
        (
            PathEvidence('char_3_5g_tfidf', 1, 0.95),
            PathEvidence('themes', 1, 0.50),
        ),
    )

    themes_property = ScoringProperty(
        'themes',
        0.17,
        make_idf_tversky(alpha=0.7, beta=0.3),
        'idf-tversky-73-v1',
    )
    scores = score_candidates(
        1,
        (c_char_only, c_char_themes),
        genres_by_id={},
        themes_by_id={1: ('Music',), 3: ('Music',)},
        tags_by_id={},
        demographics_by_id={},
        properties=(themes_property,),
    )
    s_map = {item[0]: item[2] for item in scores}

    # Candidate 2: IntrinsicBLE = 0.0 (char-TFIDF is excluded from IntrinsicBLE).
    # Content = 0.0, so final score = 0.0 * 1.00 = 0.0
    assert s_map[2] == 0.0

    # Candidate 3: IntrinsicBLE = 0.0 (char-TFIDF excluded from IntrinsicBLE).
    # Structured themes match: score = 0.17 * 1.0 = 0.17.
    # Groups present: Semantic (via char_3_5g_tfidf) + Structured (via themes) -> 2 groups -> R_cross=1 -> 1.04.
    # Final score = 0.17 * 1.04.
    assert s_map[3] == pytest.approx(0.17 * 1.04)
