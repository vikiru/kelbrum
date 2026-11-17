"""Test newly implemented empirical clash dampening guards."""

from anime_catalogue.taxonomy import Theme
from features.tags import Tag
from recommender.scoring import score_candidates
from recommender.union import PathEvidence, UnionCandidate


def test_realist_sports_vs_fantasy_battler_penalty() -> None:
    anchor_id = 263
    cand_fantasy = 527
    cand_sports = 2451

    evidence_fantasy = (PathEvidence(path='genres', score=0.60, rank=1),)
    evidence_sports = (PathEvidence(path='genres', score=0.60, rank=1),)

    candidates = [
        UnionCandidate(anime_id=cand_fantasy, evidence=evidence_fantasy),
        UnionCandidate(anime_id=cand_sports, evidence=evidence_sports),
    ]

    genres_by_id = {
        anchor_id: ('sports',),
        cand_fantasy: ('fantasy', 'adventure'),
        cand_sports: ('sports', 'drama'),
    }
    themes_by_id = {
        anchor_id: ('combat_sports',),
        cand_fantasy: ('mythology',),
        cand_sports: ('combat_sports',),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres_by_id,
        themes_by_id=themes_by_id,
        tags_by_id={},
        demographics_by_id={},
        pure_tone_contradiction_guard=True,
    )

    scores_by_id = {c.recommendation_entity_id: c.score for c in scored}
    assert scores_by_id[cand_fantasy] < scores_by_id[cand_sports]


def test_realist_crime_vs_isekai_penalty() -> None:
    anchor_id = 32998
    cand_isekai = 31240
    cand_crime = 98765

    evidence_isekai = (PathEvidence(path='themes', score=0.60, rank=1),)
    evidence_crime = (PathEvidence(path='themes', score=0.60, rank=1),)

    candidates = [
        UnionCandidate(anime_id=cand_isekai, evidence=evidence_isekai),
        UnionCandidate(anime_id=cand_crime, evidence=evidence_crime),
    ]

    genres_by_id = {
        anchor_id: ('action', 'drama'),
        cand_isekai: ('fantasy', 'drama'),
        cand_crime: ('action', 'drama'),
    }
    themes_by_id = {
        anchor_id: ('organized_crime', 'historical'),
        cand_isekai: ('isekai',),
        cand_crime: ('organized_crime',),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres_by_id,
        themes_by_id=themes_by_id,
        tags_by_id={},
        demographics_by_id={},
        pure_tone_contradiction_guard=True,
    )

    scores_by_id = {c.recommendation_entity_id: c.score for c in scored}
    assert scores_by_id[cand_isekai] < scores_by_id[cand_crime]


def test_bleak_noir_vs_slapstick_parody_penalty() -> None:
    anchor_id = 100
    cand_parody = 101
    cand_serious = 102

    evidence = (PathEvidence(path='embedding', score=0.35, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_parody, evidence=evidence),
        UnionCandidate(anime_id=cand_serious, evidence=evidence),
    ]

    genres = {
        anchor_id: ('suspense', 'drama'),
        cand_parody: ('comedy',),
        cand_serious: ('drama', 'suspense'),
    }
    themes = {
        anchor_id: ('psychological',),
        cand_parody: ('parody', 'gag_humor'),
        cand_serious: ('psychological',),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_parody] < scores[cand_serious]


def test_wholesome_cozy_vs_body_horror_penalty() -> None:
    anchor_id = 200
    cand_horror = 201
    cand_cozy = 202

    evidence = (PathEvidence(path='genres', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_horror, evidence=evidence),
        UnionCandidate(anime_id=cand_cozy, evidence=evidence),
    ]

    genres = {
        anchor_id: ('slice_of_life',),
        cand_horror: ('horror',),
        cand_cozy: ('slice_of_life',),
    }
    themes = {
        anchor_id: ('iyashikei',),
        cand_horror: ('gore',),
        cand_cozy: ('iyashikei',),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_horror] < scores[cand_cozy]


def test_bl_gl_cross_cohort_penalty() -> None:
    anchor_id = 300
    cand_bl = 301
    cand_general = 302

    evidence = (PathEvidence(path='genres', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_bl, evidence=evidence),
        UnionCandidate(anime_id=cand_general, evidence=evidence),
    ]

    genres = {
        anchor_id: ('action', 'adventure'),
        cand_bl: ('boys_love', 'drama'),
        cand_general: ('action', 'adventure'),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_bl] < scores[cand_general]


def test_innocent_youth_vs_ecchi_harem_penalty() -> None:
    anchor_id = 400
    cand_ecchi = 401
    cand_pure = 402

    evidence = (PathEvidence(path='genres', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_ecchi, evidence=evidence),
        UnionCandidate(anime_id=cand_pure, evidence=evidence),
    ]

    genres = {
        anchor_id: ('fantasy',),
        cand_ecchi: ('ecchi', 'fantasy'),
        cand_pure: ('fantasy',),
    }
    themes = {
        anchor_id: ('mahou_shoujo',),
        cand_ecchi: ('harem',),
        cand_pure: (Theme.MAHOU_SHOUJO,),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_ecchi] < scores[cand_pure]


def test_grimdark_medieval_vs_modern_school_penalty() -> None:
    anchor_id = 33
    cand_school_horror = 934
    cand_dark_fantasy = 935

    evidence_school = (PathEvidence(path='embedding', score=0.20, rank=1),)
    evidence_dark = (PathEvidence(path='embedding', score=0.20, rank=1),)

    candidates = [
        UnionCandidate(anime_id=cand_school_horror, evidence=evidence_school),
        UnionCandidate(anime_id=cand_dark_fantasy, evidence=evidence_dark),
    ]

    genres = {
        anchor_id: ('action', 'adventure', 'fantasy'),
        cand_school_horror: ('horror', 'suspense'),
        cand_dark_fantasy: ('fantasy', 'action'),
    }
    themes = {
        anchor_id: ('gore', 'military'),
        cand_school_horror: ('gore', 'psychological', 'school'),
        cand_dark_fantasy: ('gore', 'military'),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        rating_embedding_cosine={cand_school_horror: 0.20, cand_dark_fantasy: 0.20},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_school_horror] < scores[cand_dark_fantasy]


def test_psychological_sports_vs_pure_tournament_penalty() -> None:
    anchor_id = 22135
    cand_pure_sports = 22
    cand_psych_sports = 23

    evidence = (PathEvidence(path='genres', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_pure_sports, evidence=evidence),
        UnionCandidate(anime_id=cand_psych_sports, evidence=evidence),
    ]

    genres = {
        anchor_id: ('drama', 'sports'),
        cand_pure_sports: ('sports',),
        cand_psych_sports: ('drama', 'sports'),
    }
    themes = {
        anchor_id: ('psychological', 'school'),
        cand_pure_sports: ('school', 'team_sports'),
        cand_psych_sports: ('psychological',),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_pure_sports] < scores[cand_psych_sports]


def test_sparse_fantasy_vs_isekai_game_penalty() -> None:
    anchor_id = 431
    cand_isekai = 56923
    cand_fantasy = 513

    evidence = (PathEvidence(path='genres', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_isekai, evidence=evidence),
        UnionCandidate(anime_id=cand_fantasy, evidence=evidence),
    ]

    genres = {
        anchor_id: ('adventure', 'fantasy'),
        cand_isekai: ('adventure', 'fantasy'),
        cand_fantasy: ('adventure', 'fantasy'),
    }
    themes = {
        anchor_id: (),
        cand_isekai: ('isekai',),
        cand_fantasy: (),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_isekai] <= scores[cand_fantasy]


def test_setting_only_backdrop_penalty() -> None:
    anchor_id = 28851
    cand_setting_only = 390
    cand_thematic = 391

    evidence = (PathEvidence(path='genres', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_setting_only, evidence=evidence),
        UnionCandidate(anime_id=cand_thematic, evidence=evidence),
    ]

    genres = {
        anchor_id: ('drama',),
        cand_setting_only: ('drama',),
        cand_thematic: ('drama',),
    }
    themes = {
        anchor_id: (Theme.SCHOOL,),
        cand_setting_only: (Theme.SCHOOL,),
        cand_thematic: (),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={anchor_id: (Tag.DISABILITY,), cand_thematic: (Tag.DISABILITY,)},
        demographics_by_id={},
        rating_embedding_cosine={cand_setting_only: 0.30, cand_thematic: 0.30},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_setting_only] < scores[cand_thematic]


def test_sparse_anchor_disjoint_subgenre_penalty() -> None:
    anchor_id = 28851
    cand_sports = 170
    cand_drama = 28852

    evidence = (PathEvidence(path='genres', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_sports, evidence=evidence),
        UnionCandidate(anime_id=cand_drama, evidence=evidence),
    ]

    genres = {
        anchor_id: ('drama',),
        cand_sports: ('sports',),
        cand_drama: ('drama',),
    }
    themes = {
        anchor_id: ('school',),
        cand_sports: ('school', 'team_sports'),
        cand_drama: ('school',),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        rating_embedding_cosine={cand_sports: 0.35, cand_drama: 0.35},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_sports] < scores[cand_drama]


def test_psychological_investigation_vs_battle_shounen_penalty() -> None:
    anchor_id = 1535  # Death Note
    cand_battle_shounen = 392  # Yuu Yuu Hakusho
    cand_mind_game = 19  # Monster

    evidence = (PathEvidence(path='genres', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_battle_shounen, evidence=evidence),
        UnionCandidate(anime_id=cand_mind_game, evidence=evidence),
    ]

    genres = {
        anchor_id: ('suspense', 'supernatural'),
        cand_battle_shounen: ('action', 'supernatural'),
        cand_mind_game: ('suspense', 'drama'),
    }
    themes = {
        anchor_id: ('psychological', 'detective'),
        cand_battle_shounen: ('martial_arts',),
        cand_mind_game: ('psychological', 'detective'),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        rating_embedding_cosine={cand_battle_shounen: 0.40, cand_mind_game: 0.40},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_battle_shounen] < scores[cand_mind_game]


def test_serious_psychological_vs_pure_comedy_penalty() -> None:
    anchor_id = 1001
    cand_pure_comedy = 2001
    cand_drama_scifi = 2002

    evidence = (PathEvidence(path='themes', score=0.60, rank=1),)
    candidates = [
        UnionCandidate(anime_id=cand_pure_comedy, evidence=evidence),
        UnionCandidate(anime_id=cand_drama_scifi, evidence=evidence),
    ]

    genres = {
        anchor_id: ('drama', 'sci_fi', 'suspense'),
        cand_pure_comedy: ('adventure', 'comedy', 'fantasy'),
        cand_drama_scifi: ('award_winning', 'drama', 'romance', 'sci_fi'),
    }
    themes = {
        anchor_id: ('psychological', 'time_travel'),
        cand_pure_comedy: ('time_travel', 'school'),
        cand_drama_scifi: ('time_travel', 'school'),
    }

    scored = score_candidates(
        anchor_id,
        candidates,
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id={},
        demographics_by_id={},
        rating_embedding_cosine={cand_pure_comedy: 0.25, cand_drama_scifi: 0.52},
        pure_tone_contradiction_guard=True,
    )
    scores = {c.recommendation_entity_id: c.score for c in scored}
    assert scores[cand_pure_comedy] < scores[cand_drama_scifi] * 0.65
