from pipeline.curation import CurationSnapshot, audit_curation, load_curation_snapshot


def test_curation_snapshot_materializes_all_registry_identities() -> None:
    snapshot = load_curation_snapshot()

    assert snapshot.theme_additions
    assert snapshot.tagged_anime_ids
    assert snapshot.theme_identity
    assert snapshot.tag_identity
    assert snapshot.relation_identity
    assert snapshot.identity


def test_curation_snapshot_identity_changes_when_materialized_facts_change() -> None:
    snapshot = load_curation_snapshot()
    changed = CurationSnapshot(
        theme_additions={**snapshot.theme_additions, 999_999: ('Test theme',)},
        tagged_anime_ids=snapshot.tagged_anime_ids,
        theme_identity=snapshot.theme_identity,
        tag_identity=snapshot.tag_identity,
        relation_identity=snapshot.relation_identity,
    )

    assert changed.identity != snapshot.identity


def test_curation_audit_reports_ids_outside_active_catalogue() -> None:
    snapshot = CurationSnapshot(
        theme_additions={10: ('Test theme',)},
        tagged_anime_ids=frozenset({11}),
        theme_identity='theme',
        tag_identity='tag',
        relation_identity='relation',
    )

    audit = audit_curation(snapshot, {1})

    assert audit.missing_theme_ids == (10,)
    assert audit.missing_tag_ids == (11,)
    assert audit.missing_relation_ids
    assert audit.missing_count == 2 + len(audit.missing_relation_ids)
