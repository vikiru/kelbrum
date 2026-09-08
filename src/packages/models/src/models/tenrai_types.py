"""Canonical values for Tenrai response enums."""

_MEDIA_TYPES = {
    'TV': 'TV',
    'TV_SPECIAL': 'TV_SPECIAL',
    'MOVIE': 'MOVIE',
    'OVA': 'OVA',
    'ONA': 'ONA',
    'SPECIAL': 'SPECIAL',
    'MUSIC': 'MUSIC',
    'CM': 'CM',
    'PV': 'PV',
}


def normalize_media_type(value: str | None) -> str | None:
    """Normalize Tenrai response media types to stable uppercase values."""
    if value is None:
        return None
    normalized = value.strip().upper().replace('-', '_').replace(' ', '_')
    return _MEDIA_TYPES.get(normalized, normalized or None)
