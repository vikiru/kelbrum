from recommender.frozen_pipeline import raw_score_frozen_union
from recommender.relationship_graph import build_relationship_index
from recommender.union import PathEvidence, UnionCandidate


def test_same_story_family_is_removed_and_candidates_are_canonicalized() -> None:
    index = build_relationship_index(
        (1, 2, 3, 4),
        {
            1: ((2, 'Sequel'),),
            2: ((1, 'Prequel'),),
            3: ((4, 'Sequel'),),
            4: ((3, 'Prequel'),),
        },
    )

    assert index.cleanup(1, (1, 2, 3, 4)) == (3,)


def test_manual_relationships_are_symmetric_and_fingerprinted() -> None:
    index = build_relationship_index((1, 2), {}, manual_relationships={1: (2,)})

    assert index.excluded_ids(1) == frozenset({1, 2})
    assert index.excluded_ids(2) == frozenset({1, 2})
    assert index.fingerprint()


def test_frozen_union_keeps_highest_alias_score_and_merges_paths() -> None:
    index = build_relationship_index(
        (1, 2, 3, 4),
        {
            2: ((3, 'Sequel'), (4, 'Sequel')),
            3: ((2, 'Prequel'),),
            4: ((2, 'Prequel'),),
        },
        anime_types={2: 'TV', 3: 'TV', 4: 'TV'},
    )
    candidates = (
        UnionCandidate(3, (PathEvidence('embedding', 1, 0.2),)),
        UnionCandidate(
            4,
            (
                PathEvidence('embedding', 1, 0.8),
                PathEvidence('genres', 1, 0.8),
            ),
        ),
    )

    result = raw_score_frozen_union(
        1,
        candidates,
        genres_by_id={},
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={},
        relationship_index=index,
    )

    assert result == ((2, 4, 0.336, ('embedding', 'genres')),)


def test_tv_origin_beats_movie_and_ona_entries_when_relationships_identify_origin() -> None:
    index = build_relationship_index(
        (10, 11, 12),
        {
            10: ((11, 'Sequel'), (12, 'Sequel')),
            11: ((10, 'Prequel'),),
            12: ((10, 'Prequel'),),
        },
        anime_types={10: 'TV', 11: 'Movie', 12: 'ONA'},
    )

    assert index.canonical_id(11) == 10
    assert index.canonical_id(12) == 10


def test_movie_family_without_tv_origin_uses_deterministic_first_entry() -> None:
    index = build_relationship_index(
        (20, 21, 22),
        {20: ((21, 'Sequel'),), 21: ((20, 'Prequel'),), 22: ((21, 'Sequel'),)},
        anime_types={20: 'Movie', 21: 'Movie', 22: 'Movie'},
    )

    assert index.canonical_id(20) == 20
    assert index.canonical_id(21) == 20
    assert index.canonical_id(22) == 20


def test_original_and_remake_are_collapsed_by_alternative_version_relation() -> None:
    index = build_relationship_index(
        (30, 31),
        {30: ((31, 'Alternative Version'),)},
        anime_types={30: 'TV', 31: 'TV'},
    )

    assert index.canonical_id(30) == 30
    assert index.canonical_id(31) == 30
    assert index.cleanup(30, (31,)) == ()


def test_spin_off_remains_a_separate_recommendation_family() -> None:
    index = build_relationship_index(
        (40, 41),
        {40: ((41, 'Spin-Off'),)},
        anime_types={40: 'TV', 41: 'TV'},
    )

    assert index.canonical_id(40) != index.canonical_id(41)
    assert index.excluded_ids(40) == frozenset({40})


def test_distinct_franchise_relations_remain_recommendable() -> None:
    relation_types = (
        'Alternative Setting',
        'Character',
        'Other',
        'Parent Story',
        'Side Story',
        'Spin-Off',
    )
    relations = {100: tuple(enumerate(relation_types, 101))}
    anime_ids = tuple(range(100, 107))
    anime_types = dict.fromkeys(anime_ids, 'TV')

    index = build_relationship_index(anime_ids, relations, anime_types=anime_types)

    for candidate_id in range(101, 107):
        assert index.canonical_id(candidate_id) == candidate_id
        assert index.cleanup(100, (candidate_id,)) == (candidate_id,)


def test_same_story_relations_still_collapse_inside_a_franchise() -> None:
    index = build_relationship_index(
        (200, 201, 202),
        {
            200: ((201, 'Sequel'), (202, 'Alternative Version')),
            201: ((200, 'Prequel'),),
            202: ((200, 'Alternative Version'),),
        },
        anime_types={200: 'TV', 201: 'TV', 202: 'TV'},
    )

    assert index.canonical_id(201) == 200
    assert index.canonical_id(202) == 200
    assert index.cleanup(200, (201, 202)) == ()
