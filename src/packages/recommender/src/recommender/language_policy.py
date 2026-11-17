"""Origin language compatibility policy for cross-linguistic recommendation gating and weighting."""

from functools import lru_cache
from typing import Final

import msgspec

from normalization.metadata import OriginLanguage

_LABEL_TO_ORIGIN_LANGUAGE: Final[dict[str, OriginLanguage]] = {
    'ja': OriginLanguage.JAPANESE,
    'japanese': OriginLanguage.JAPANESE,
    'zh': OriginLanguage.CHINESE,
    'chinese': OriginLanguage.CHINESE,
    'ko': OriginLanguage.KOREAN,
    'korean': OriginLanguage.KOREAN,
    'fr': OriginLanguage.FRENCH,
    'french': OriginLanguage.FRENCH,
    'en': OriginLanguage.ENGLISH,
    'english': OriginLanguage.ENGLISH,
}


@lru_cache(maxsize=64)
def normalize_origin_language(value: str | OriginLanguage | None) -> OriginLanguage:
    """Normalize language labels and ISO-639-1 codes to canonical OriginLanguage."""
    if value is None:
        return OriginLanguage.UNKNOWN
    if isinstance(value, OriginLanguage):
        return value
    clean = str(value).strip().casefold()
    if not clean or clean in {'unknown', 'none'}:
        return OriginLanguage.UNKNOWN
    return _LABEL_TO_ORIGIN_LANGUAGE.get(clean, OriginLanguage.UNKNOWN)


class LanguageCompatibilityPolicy(msgspec.Struct, frozen=True):
    same_language_boost: float = 1.02
    cross_language_dampen: float = 0.40
    cross_language_dense_override_threshold: float = 0.68

    def multiplier(
        self,
        source_lang: str | OriginLanguage | None,
        candidate_lang: str | OriginLanguage | None,
        dense_similarity: float = 0.0,
    ) -> float:
        s_lang = normalize_origin_language(source_lang)
        c_lang = normalize_origin_language(candidate_lang)

        if s_lang == OriginLanguage.UNKNOWN or c_lang == OriginLanguage.UNKNOWN:
            return 1.0

        if s_lang == c_lang:
            return self.same_language_boost

        if dense_similarity >= self.cross_language_dense_override_threshold:
            return 1.0

        return self.cross_language_dampen


DEFAULT_LANGUAGE_COMPATIBILITY_POLICY: Final[LanguageCompatibilityPolicy] = LanguageCompatibilityPolicy()

__all__ = [
    'DEFAULT_LANGUAGE_COMPATIBILITY_POLICY',
    'LanguageCompatibilityPolicy',
    'OriginLanguage',
    'normalize_origin_language',
]
