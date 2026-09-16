from fetch.contracts import AnimeRelation, RelationEntry, TenraiAnimeEntry
from graph import GraphRelation, RelationType
from pipeline.relation_evidence import normalize_relation_evidence


def test_normalization_scopes_edges_and_reports_dangling_targets() -> None:
    entries = (
        TenraiAnimeEntry(
            mal_id=1,
            title='Origin',
            relations=[
                AnimeRelation(
                    'Sequel',
                    [
                        RelationEntry(mal_id=2, type='anime', name='Known'),
                        RelationEntry(mal_id=3, type='anime', name='Missing'),
                        RelationEntry(mal_id=1, type='anime', name='Self'),
                        RelationEntry(mal_id=4, type='manga', name='Manga'),
                    ],
                ),
                AnimeRelation('Unknown label', [RelationEntry(mal_id=2, type='anime')]),
            ],
        ),
        TenraiAnimeEntry(mal_id=2, title='Known'),
    )

    evidence = normalize_relation_evidence(entries, {1, 2})

    assert evidence.relations == {
        1: (
            GraphRelation(2, RelationType.SEQUEL),
            GraphRelation(2, RelationType.OTHER),
        ),
        2: (),
    }
    assert evidence.audit.source_count == 2
    assert evidence.audit.accepted_edge_count == 2
    assert evidence.audit.dangling_relations[0].target_id == 3
    assert evidence.audit.dangling_count == 1


def test_duplicate_source_edges_are_deduplicated() -> None:
    entry = TenraiAnimeEntry(
        mal_id=1,
        title='Origin',
        relations=[
            AnimeRelation('Sequel', [RelationEntry(mal_id=2, type='anime')]),
            AnimeRelation('Sequel', [RelationEntry(mal_id=2, type='anime')]),
        ],
    )

    evidence = normalize_relation_evidence((entry,), {1, 2})

    assert evidence.relations[1] == (GraphRelation(2, RelationType.SEQUEL),)
    assert evidence.audit.accepted_edge_count == 1
