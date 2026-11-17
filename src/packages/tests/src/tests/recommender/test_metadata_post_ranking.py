"""Tests for production metadata post-ranking integration."""

from recommender.post_ranking import (
    AnimePostRankingMetadata,
    compute_audience_adjustment,
    compute_format_commitment_adjustment,
    compute_metadata_multiplier,
    compute_quality_adjustment,
)


def test_post_ranking_piecewise_functions() -> None:
    # Group 1: Audience
    a_demo = AnimePostRankingMetadata(1, 'TV', 'Shounen', 'PG-13', 2010, 8.0, 500.0)
    c_kids = AnimePostRankingMetadata(2, 'TV', 'Kids', 'G', 2010, 8.0, 500.0)
    g1 = compute_audience_adjustment(a_demo, c_kids)
    assert g1 < 0.0

    # Group 2: Unified Format & Volume Commitment
    a_tv = AnimePostRankingMetadata(1, 'TV', 'Shounen', 'PG-13', 2020, 8.0, 500.0, episodes=12, storyline_episodes=12)
    c_mov = AnimePostRankingMetadata(2, 'MOVIE', 'Shounen', 'PG-13', 2020, 8.0, 500.0, episodes=1, storyline_episodes=1)
    g_commit_movie = compute_format_commitment_adjustment(a_tv, c_mov)
    assert g_commit_movie < 0.0

    a_epic = AnimePostRankingMetadata(
        1, 'TV', 'Shounen', 'PG-13', 2010, 8.0, 5000.0, episodes=200, storyline_episodes=200
    )
    g_peer = compute_format_commitment_adjustment(a_epic, a_epic)
    assert g_peer > 0.0

    c_short_ona = AnimePostRankingMetadata(
        3, 'ONA', 'Shounen', 'PG-13', 2010, 8.0, 60.0, episodes=1, storyline_episodes=1
    )
    g_short = compute_format_commitment_adjustment(a_epic, c_short_ona)
    assert g_short < 0.0

    # Group 3: Quality Prior
    c_high = AnimePostRankingMetadata(2, 'TV', 'Shounen', 'PG-13', 2020, 8.6, 500.0)
    g_qual = compute_quality_adjustment(a_tv, c_high)
    assert g_qual == 0.018

    c_low = AnimePostRankingMetadata(4, 'TV', 'Shounen', 'PG-13', 2020, 6.0, 500.0)
    g_qual_low = compute_quality_adjustment(a_tv, c_low, dense_cosine=0.50)
    assert g_qual_low == -0.080

    # Multiplier bounds [0.65, 1.15]
    mult = compute_metadata_multiplier(a_demo, c_kids)
    assert 0.65 <= mult <= 1.15
