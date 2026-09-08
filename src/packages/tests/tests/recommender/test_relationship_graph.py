from recommender.relationship_graph import build_relationship_index


def test_cleanup_removes_anchor_family_and_deduplicates_canonical_ids() -> None:
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
    assert bool(index.fingerprint())
