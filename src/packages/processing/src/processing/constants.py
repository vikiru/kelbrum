"""Stable processing policy constants."""

from fetch.types import MediaType

PROCESSING_AUDIT_SCHEMA_VERSION = 'processing-v13-manual-metadata-parquet'
DEFAULT_MAX_YEAR = 2026
DEFAULT_ALLOWED_TYPES = frozenset({MediaType.TV, MediaType.ONA, MediaType.MOVIE})
DEFAULT_EXCLUDED_GENRE_IDS = frozenset({12, 49})
DEFAULT_MIN_MOVIE_DURATION_MINUTES = 20
DEFAULT_MIN_DURATION_MINUTES = 11
PLACEHOLDER_IMAGE_URL = 'https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png'
