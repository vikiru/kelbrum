"""Stable internal taxonomy labels used by processing rules."""

import re

_NON_ALPHANUMERIC = re.compile(r'[^a-z0-9]+')


def normalize_label(value: str) -> str:
    """Convert a taxonomy label to stable snake_case."""
    return _NON_ALPHANUMERIC.sub('_', value.strip().casefold()).strip('_')
