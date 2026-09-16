"""Curated origin-language overrides for ambiguous catalogue records."""

from features.origin_language import OriginLanguage

ORIGIN_LANGUAGE_OVERRIDES_VERSION = 'origin-language-overrides-v1'

MANUAL_ORIGIN_LANGUAGE_ASSIGNMENTS: tuple[tuple[tuple[int, ...], OriginLanguage], ...] = (
    # Wei Miao Rensheng (60591), Li Shiya (64535).
    ((60591, 64535), OriginLanguage.CHINESE),
    # Radiant (37202, 39355).
    ((37202, 39355), OriginLanguage.FRENCH),
)

MANUAL_ORIGIN_LANGUAGES: dict[int, OriginLanguage] = {
    anime_id: language for anime_ids, language in MANUAL_ORIGIN_LANGUAGE_ASSIGNMENTS for anime_id in anime_ids
}
