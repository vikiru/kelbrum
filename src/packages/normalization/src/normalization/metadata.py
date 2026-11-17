"""Source-backed metadata availability states used across pipeline stages."""

from enum import StrEnum


class MetadataState(StrEnum):
    UNKNOWN = 'UNKNOWN'
    OBSERVED_ABSENT = 'OBSERVED_ABSENT'
    OBSERVED = 'OBSERVED'


class AnimeType(StrEnum):
    MOVIE = 'MOVIE'
    ONA = 'ONA'
    TV = 'TV'


class AnimeSource(StrEnum):
    FOUR_KOMA_MANGA = '4-koma manga'
    BOOK = 'Book'
    CARD_GAME = 'Card game'
    GAME = 'Game'
    LIGHT_NOVEL = 'Light novel'
    MANGA = 'Manga'
    MIXED_MEDIA = 'Mixed media'
    MUSIC = 'Music'
    NOVEL = 'Novel'
    ORIGINAL = 'Original'
    OTHER = 'Other'
    PICTURE_BOOK = 'Picture book'
    RADIO = 'Radio'
    UNKNOWN = 'Unknown'
    VISUAL_NOVEL = 'Visual novel'
    WEB_MANGA = 'Web manga'
    WEB_NOVEL = 'Web novel'


class RelationMediaType(StrEnum):
    MANGA = 'manga'
    MANHWA = 'manhwa'
    MANHUA = 'manhua'


class AiringSeason(StrEnum):
    WINTER = 'winter'
    SPRING = 'spring'
    SUMMER = 'summer'
    FALL = 'fall'
    UNKNOWN = 'unknown'


class OriginLanguage(StrEnum):
    CHINESE = 'zh'
    ENGLISH = 'en'
    FRENCH = 'fr'
    JAPANESE = 'ja'
    KOREAN = 'ko'
    UNKNOWN = 'unknown'


DEMOGRAPHIC_LABELS = {
    'kids': 'Kids',
    'shounen': 'Shounen',
    'shonen': 'Shounen',
    'seinen': 'Seinen',
    'shoujo': 'Shoujo',
    'shojo': 'Shoujo',
    'josei': 'Josei',
}


def normalize_demographic(value: str) -> str:
    """Normalize a known demographic label while preserving its canonical distinction."""
    normalized = DEMOGRAPHIC_LABELS.get(value.strip().casefold())
    if normalized is None:
        raise ValueError(f'unsupported demographic label: {value!r}')
    return normalized


def collection_state(values: object | None) -> MetadataState:
    """Classify a source collection without treating an omitted value as empty."""
    if values is None:
        return MetadataState.UNKNOWN
    return MetadataState.OBSERVED if values else MetadataState.OBSERVED_ABSENT


def scalar_state(value: str | None) -> MetadataState:
    """Classify a source scalar while preserving unknown and explicit blank values."""
    if value is None:
        return MetadataState.UNKNOWN
    return MetadataState.OBSERVED if value.strip() else MetadataState.OBSERVED_ABSENT
