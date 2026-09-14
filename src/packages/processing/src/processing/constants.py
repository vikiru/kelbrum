"""Stable processing policy constants."""

PROCESSING_AUDIT_SCHEMA_VERSION = 'processing-v6-duration-parsing'
DEFAULT_MAX_YEAR = 2026
DEFAULT_ALLOWED_TYPES = frozenset({'TV', 'ONA', 'MOVIE'})
DEFAULT_EXCLUDED_GENRE_IDS = frozenset({9, 12, 49})
DEFAULT_MIN_MOVIE_DURATION_MINUTES = 20
PLACEHOLDER_IMAGE_URL = 'https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png'
