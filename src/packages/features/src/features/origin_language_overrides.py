"""Curated origin-language overrides for ambiguous catalogue records."""

import csv
import logging
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

from config.manual_data import MANUAL_ORIGIN_LANGUAGE_CSV_PATH
from normalization.metadata import OriginLanguage

logger = logging.getLogger(__name__)

ORIGIN_LANGUAGE_OVERRIDES_VERSION = 'origin-language-overrides-v1'

_LANGUAGE_NAMES = {
    'chinese': OriginLanguage.CHINESE,
    'english': OriginLanguage.ENGLISH,
    'french': OriginLanguage.FRENCH,
    'japanese': OriginLanguage.JAPANESE,
    'korean': OriginLanguage.KOREAN,
}


def manual_origin_language_csv_hash(path: Path = MANUAL_ORIGIN_LANGUAGE_CSV_PATH) -> str:
    """Return a content fingerprint for the optional origin-language CSV."""
    return sha256(path.read_bytes()).hexdigest() if path.is_file() else ''


MANUAL_ORIGIN_LANGUAGE_ASSIGNMENTS: tuple[tuple[tuple[int, ...], OriginLanguage], ...] = (
    # Wei Miao Rensheng (60591), Li Shiya (64535).
    ((60591, 64535), OriginLanguage.CHINESE),
    # Radiant (37202, 39355).
    ((37202, 39355), OriginLanguage.FRENCH),
)

_BUILTIN_MANUAL_ORIGIN_LANGUAGES: dict[int, OriginLanguage] = {
    anime_id: language for anime_ids, language in MANUAL_ORIGIN_LANGUAGE_ASSIGNMENTS for anime_id in anime_ids
}


def load_manual_origin_languages(path: Path = MANUAL_ORIGIN_LANGUAGE_CSV_PATH) -> dict[int, OriginLanguage]:
    """Load optional CSV overrides; empty language cells do not override inferred values."""
    languages = dict(_BUILTIN_MANUAL_ORIGIN_LANGUAGES)
    if not path.is_file():
        logger.warning(
            'Manual csv files were not found (%s). Continuing without them, '
            'this may greatly affect recommendation quality',
            path,
        )
        return languages
    logger.info('Loading manual csv file: %s', path)
    with path.open(newline='', encoding='utf-8-sig') as source:
        reader = csv.DictReader(source)
        if not {'anime_id', 'language'}.issubset(reader.fieldnames or ()):
            raise ValueError(f'manual origin-language CSV must contain anime_id and language columns: {path}')
        for row_number, row in enumerate(reader, 2):
            raw_language = (row.get('language') or '').strip()
            if not raw_language:
                continue
            try:
                anime_id = int(row.get('anime_id') or '')
                normalized_language = raw_language.casefold()
                language = (
                    _LANGUAGE_NAMES[normalized_language]
                    if normalized_language in _LANGUAGE_NAMES
                    else OriginLanguage(normalized_language)
                )
            except ValueError as error:
                raise ValueError(f'invalid origin-language CSV row {row_number}: {path}') from error
            if anime_id <= 0:
                raise ValueError(f'invalid anime_id on origin-language CSV row {row_number}: {path}')
            languages[anime_id] = language
    return languages


@lru_cache(maxsize=1)
def get_manual_origin_languages() -> dict[int, OriginLanguage]:
    """Lazily load and cache the default manual origin-language overrides."""
    return load_manual_origin_languages()
