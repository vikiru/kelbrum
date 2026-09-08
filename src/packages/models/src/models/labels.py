"""Stable internal labels and human-readable display labels."""

import re

_NON_ALPHANUMERIC = re.compile(r'[^a-z0-9]+')
_DISPLAY_OVERRIDES = {
    'avant_garde': 'Avant Garde',
    'award_winning': 'Award Winning',
    'boys_love': 'Boys Love',
    'girls_love': 'Girls Love',
    'sci_fi': 'Sci-Fi',
    'slice_of_life': 'Slice of Life',
}


def normalize_label(value: str) -> str:
    """Convert a taxonomy label to stable snake_case."""
    return _NON_ALPHANUMERIC.sub('_', value.strip().casefold()).strip('_')


def display_label(value: str) -> str:
    """Convert an internal taxonomy label to a readable frontend label."""
    normalized = normalize_label(value)
    return _DISPLAY_OVERRIDES.get(normalized, normalized.replace('_', ' ').title())
