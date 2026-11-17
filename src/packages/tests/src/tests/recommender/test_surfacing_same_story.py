from recommender.contracts import RawRecommendation
from recommender.surfacing import SurfacingPolicy


def _candidate(anime_id: int, score: float = 0.9) -> RawRecommendation:
    return RawRecommendation(anime_id, anime_id, score, (), False, False)


def test_surfacing_rejects_bidirectional_same_story_collisions_and_keeps_franchise_siblings() -> None:
    candidates = tuple(_candidate(anime_id) for anime_id in (10, 11, 12, 13))
    franchise = {anime_id: frozenset({10, 11, 12, 13, 14, 15}) for anime_id in (10, 11, 12, 13)}
    exclusions = {10: frozenset({10, 11}), 11: frozenset({11}), 12: frozenset({12, 13}), 13: frozenset({13})}

    surfaced = SurfacingPolicy(minimum_score=0.0).surface(
        candidates,
        franchise_by_id=franchise,
        same_story_exclusions_by_id=exclusions,
    )

    assert tuple(item.anime_id for item in surfaced) == (10, 12)


def test_same_story_rejection_does_not_consume_franchise_capacity() -> None:
    candidates = tuple(_candidate(anime_id) for anime_id in range(1, 8))
    franchise = {anime_id: frozenset({1, 2, 3, 4, 5, 6, 7}) for anime_id in range(1, 8)}
    exclusions = {anime_id: frozenset({anime_id}) for anime_id in range(1, 8)}
    exclusions[2] = frozenset({2, 1})

    surfaced = SurfacingPolicy(minimum_score=0.0, max_per_franchise=5).surface(
        candidates,
        franchise_by_id=franchise,
        same_story_exclusions_by_id=exclusions,
    )

    assert tuple(item.anime_id for item in surfaced) == (1, 3, 4, 5, 6)


def test_surfacing_collapses_story_line_continuations_to_single_slot() -> None:
    # Candidates 201 (S1), 202 (S2), 203 (S3) belong to story line 201
    # Candidate 301 belongs to story line 301
    candidates = (
        _candidate(202, score=0.88),  # S2 scores highest
        _candidate(201, score=0.80),  # S1 canonical entrypoint
        _candidate(301, score=0.75),  # Distinct story
        _candidate(203, score=0.70),  # S3 continuation
    )
    story_line_by_id = {201: 201, 202: 201, 203: 201, 301: 301}
    franchise = {aid: frozenset({201, 202, 203, 301}) for aid in (201, 202, 203, 301)}
    exclusions = {aid: frozenset({aid}) for aid in (201, 202, 203, 301)}

    surfaced = SurfacingPolicy(minimum_score=0.0).surface(
        candidates,
        franchise_by_id=franchise,
        same_story_exclusions_by_id=exclusions,
        story_line_by_id=story_line_by_id,
    )

    # Canonical entrypoint 201 is surfaced representing storyline 201 with highest witness score 0.88, followed by 301
    assert tuple(item.anime_id for item in surfaced) == (201, 301)
    assert surfaced[0].score == 0.88
    assert surfaced[0].witness_member_id == 202


def test_fma_bidirectional_recommendation_and_distinct_adaptation_coexistence() -> None:
    # FMA 2003 (121) and Brotherhood (5114) are in the same franchise but distinct story lines
    candidates = (
        _candidate(5114, score=0.85),
        _candidate(28249, score=0.50),
    )
    story_line_by_id = {121: 121, 5114: 5114, 28249: 28249}
    franchise = {121: frozenset({121, 5114}), 5114: frozenset({121, 5114}), 28249: frozenset({28249})}
    exclusions_for_121 = {121: frozenset({121, 430}), 5114: frozenset({5114, 9135}), 28249: frozenset({28249})}

    surfaced = SurfacingPolicy(minimum_score=0.0).surface(
        candidates,
        franchise_by_id=franchise,
        same_story_exclusions_by_id=exclusions_for_121,
        story_line_by_id=story_line_by_id,
    )

    assert tuple(item.anime_id for item in surfaced) == (5114, 28249)


def test_deterministic_ten_story_five_slot_franchise_cap() -> None:
    # 10 distinct eligible story groups G1-G10 with scores from 0.95 down to 0.68
    scores = [0.95, 0.92, 0.90, 0.87, 0.85, 0.83, 0.80, 0.76, 0.72, 0.68]
    # 10 distinct eligible story groups G1-G10 plus multiple members of G1
    candidates_with_multi = (
        _candidate(1002, score=0.96),  # G1_S2 (higher score)
        _candidate(100, score=0.95),  # G1_S1 (entrypoint)
        _candidate(1003, score=0.91),  # G1_S3 (lower score)
        *(_candidate(100 + i, score=scores[i]) for i in range(1, 10)),
    )

    franchise = {aid: frozenset(range(100, 110)) | {1002, 1003} for aid in range(100, 110)}
    franchise[1002] = franchise[100]
    franchise[1003] = franchise[100]

    story_line = {100 + i: 100 + i for i in range(10)}
    story_line[1002] = 100
    story_line[1003] = 100

    exclusions = {aid: frozenset({aid}) for aid in franchise}
    exclusions[100] = frozenset({100, 1002, 1003})
    exclusions[1002] = frozenset({100, 1002, 1003})
    exclusions[1003] = frozenset({100, 1002, 1003})

    surfaced = SurfacingPolicy(minimum_score=0.0, max_per_franchise=5).surface(
        candidates_with_multi,
        franchise_by_id=franchise,
        same_story_exclusions_by_id=exclusions,
        story_line_by_id=story_line,
    )

    # G1 collapses to canonical entrypoint 100 with member 1002's peak score, followed by G2-G5
    # G6-G10 are capped out by max_per_franchise=5
    assert tuple(item.anime_id for item in surfaced) == (100, 101, 102, 103, 104)
    assert surfaced[0].score == 0.96
    assert surfaced[0].witness_member_id == 1002


def test_anchor_own_story_does_not_consume_franchise_quota() -> None:
    # Anchor is 100. Candidates are distinct stories in same franchise: 101, 102, 103, 104, 105, 106
    # With max_per_franchise=5, exactly 5 distinct stories from the franchise should surface.
    candidates = tuple(_candidate(100 + i, score=0.90 - i * 0.05) for i in range(1, 7))
    franchise = {100 + i: frozenset(range(100, 107)) for i in range(1, 7)}
    exclusions = {100 + i: frozenset({100 + i}) for i in range(1, 7)}
    story_line = {100 + i: 100 + i for i in range(1, 7)}

    surfaced = SurfacingPolicy(minimum_score=0.0, max_per_franchise=5).surface(
        candidates,
        franchise_by_id=franchise,
        same_story_exclusions_by_id=exclusions,
        story_line_by_id=story_line,
    )

    # Exactly 5 stories (101, 102, 103, 104, 105) are surfaced; anchor 100 does not consume a slot
    assert tuple(item.anime_id for item in surfaced) == (101, 102, 103, 104, 105)
