"""Human-readable taxonomy labels for frontend projections."""

from processing.labels import normalize_label

_DISPLAY_OVERRIDES = {
    'avant_garde': 'Avant Garde',
    'award_winning': 'Award Winning',
    'boys_love': 'Boys Love',
    'girls_love': 'Girls Love',
    'sci_fi': 'Sci-Fi',
    'slice_of_life': 'Slice of Life',
}


def display_label(value: str) -> str:
    """Convert an internal taxonomy label to a readable frontend label."""
    normalized = normalize_label(value)
    return _DISPLAY_OVERRIDES.get(normalized, normalized.replace('_', ' ').title())
