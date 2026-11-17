from recommender.contracts import RawRecommendation
from recommender.surfacing import collapse_to_franchise_containers


def test_collapse_to_franchise_containers_groups_multi_season_into_canonical() -> None:
    # Anchor is an action mecha anime
    # Candidate 1: Gundam SEED Destiny (Sequel member, high similarity score)
    # Candidate 2: Gundam SEED (Canonical entrypoint, lower similarity score)
    # Candidate 3: Gundam Wing (Independent canonical storyline in same franchise)
    # Candidate 4: Code Geass (Independent mecha anime in different franchise)
    items = (
        RawRecommendation(
            anime_id=102,  # Gundam SEED Destiny
            witness_member_id=102,
            score=0.88,
            retrieval_paths=('embedding', 'tags'),
            semantic_available=True,
            categorical_available=True,
        ),
        RawRecommendation(
            anime_id=101,  # Gundam SEED
            witness_member_id=101,
            score=0.72,
            retrieval_paths=('themes',),
            semantic_available=False,
            categorical_available=True,
        ),
        RawRecommendation(
            anime_id=105,  # Gundam Wing
            witness_member_id=105,
            score=0.81,
            retrieval_paths=('embedding', 'weighted-v2'),
            semantic_available=True,
            categorical_available=True,
        ),
        RawRecommendation(
            anime_id=201,  # Code Geass
            witness_member_id=201,
            score=0.85,
            retrieval_paths=('embedding', 'themes', 'tags'),
            semantic_available=True,
            categorical_available=True,
        ),
    )

    story_line_by_id = {
        102: 101,  # 102 maps to canonical entrypoint 101
        101: 101,
        105: 105,
        201: 201,
    }

    gundam_franchise = frozenset({101, 102, 105})
    geass_franchise = frozenset({201})
    franchise_by_id = {
        101: gundam_franchise,
        102: gundam_franchise,
        105: gundam_franchise,
        201: geass_franchise,
    }

    slots = collapse_to_franchise_containers(
        items,
        franchise_by_id=franchise_by_id,
        story_line_by_id=story_line_by_id,
        maximum_storylines_per_franchise=2,
    )

    # 1. We expect exactly 2 franchise slots (Gundam and Code Geass)
    assert len(slots) == 2

    # 2. Top slot is Gundam (score 0.88 inherited from witness 102)
    top_slot = slots[0]
    assert top_slot.primary_anime_id == 101
    assert top_slot.maximum_similarity_score == 0.88
    assert len(top_slot.storyline_entries) == 2

    # Verify that canonical entrypoint 101 inherited member 102's evidence & max score
    entry_seed = top_slot.storyline_entries[0]
    assert entry_seed.canonical_anime_id == 101
    assert entry_seed.best_witness_anime_id == 102
    assert entry_seed.similarity_score == 0.88
    assert 'tags' in entry_seed.retrieval_paths
    assert 'themes' in entry_seed.retrieval_paths
    assert entry_seed.semantic_available is True

    # Verify second storyline in Gundam slot is Wing (105) with similarity 0.81
    entry_wing = top_slot.storyline_entries[1]
    assert entry_wing.canonical_anime_id == 105
    assert entry_wing.similarity_score == 0.81

    # 3. Second slot is Code Geass
    second_slot = slots[1]
    assert second_slot.primary_anime_id == 201
    assert second_slot.maximum_similarity_score == 0.85
    assert len(second_slot.storyline_entries) == 1
