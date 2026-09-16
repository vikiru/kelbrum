from features.origin_language import OriginLanguage, infer_origin_language
from fetch.contracts import AnimeRelation, RelationEntry, TenraiAnimeEntry


def test_origin_language_uses_relation_and_script_evidence() -> None:
    entry = TenraiAnimeEntry(
        mal_id=1,
        title='静かな物語',
        relations=[
            AnimeRelation(
                relation='adaptation',
                entry=[RelationEntry(mal_id=2, name='Source', media_type='manga')],
            )
        ],
    )

    result = infer_origin_language(entry)

    assert result.language is OriginLanguage.JAPANESE
    assert result.confidence == 1.0
    assert len(result.evidence) == 2


def test_origin_language_override_is_authoritative() -> None:
    entry = TenraiAnimeEntry(mal_id=1, title='한글 제목')

    result = infer_origin_language(entry, {1: OriginLanguage.ENGLISH})

    assert result.language is OriginLanguage.ENGLISH
    assert result.confidence == 1.0
    assert result.evidence[0].source == 'manual_override'
