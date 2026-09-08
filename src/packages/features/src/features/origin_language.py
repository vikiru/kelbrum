"""Deterministic origin-language evidence derived from catalogue metadata."""

import re
from collections.abc import Mapping
from enum import StrEnum

import msgspec

from models.tenrai import TenraiAnimeEntry


class OriginLanguage(StrEnum):
    CHINESE = 'zh'
    ENGLISH = 'en'
    FRENCH = 'fr'
    JAPANESE = 'ja'
    KOREAN = 'ko'


class OriginEvidence(msgspec.Struct, frozen=True):
    language: OriginLanguage
    source: str
    value: str
    weight: float


class OriginLanguageFeature(msgspec.Struct, frozen=True):
    language: OriginLanguage | None
    confidence: float
    evidence: tuple[OriginEvidence, ...]


# Hangul targets Korean; Hiragana and Katakana target Japanese.
_HANGUL = re.compile(r'[\uac00-\ud7af]')
_HIRAGANA = re.compile(r'[\u3040-\u309f]')
_KATAKANA = re.compile(r'[\u30a0-\u30ff]')


def infer_origin_language(
    entry: TenraiAnimeEntry,
    overrides: Mapping[int, OriginLanguage] | None = None,
) -> OriginLanguageFeature:
    """Infer origin language from explicit adaptation and textual signals."""
    override = (overrides or {}).get(entry.mal_id)
    if override is not None:
        override_evidence = OriginEvidence(override, 'manual_override', str(entry.mal_id), 1.5)
        return OriginLanguageFeature(override, 1.0, (override_evidence,))
    evidence: list[OriginEvidence] = []
    for relation in entry.relations:
        for target in relation.entry:
            name = target.name or ''
            media_type = (target.media_type or '').casefold()
            if media_type == 'manhwa':
                evidence.append(OriginEvidence(OriginLanguage.KOREAN, 'relation', name, 1.0))
            elif media_type == 'manhua':
                evidence.append(OriginEvidence(OriginLanguage.CHINESE, 'relation', name, 1.0))
            elif media_type == 'manga' or (not media_type and target.type and target.type.casefold() == 'manga'):
                evidence.append(OriginEvidence(OriginLanguage.JAPANESE, 'relation', name, 1.0))

    if _HANGUL.search(entry.title):
        evidence.append(OriginEvidence(OriginLanguage.KOREAN, 'title_script', entry.title, 0.5))
    elif _HIRAGANA.search(entry.title) or _KATAKANA.search(entry.title):
        evidence.append(OriginEvidence(OriginLanguage.JAPANESE, 'title_script', entry.title, 0.5))

    totals: dict[OriginLanguage, float] = {}
    for item in evidence:
        totals[item.language] = totals.get(item.language, 0.0) + item.weight
    if not totals:
        return OriginLanguageFeature(None, 0.0, ())
    language = max(totals, key=totals.__getitem__)
    total = totals[language]
    confidence = min(total / 1.5, 1.0)
    return OriginLanguageFeature(language, confidence, tuple(evidence))
