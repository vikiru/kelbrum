"""Separate display synopsis text from conservative feature text."""

import re

import polars as pl

_URL = re.compile(r'https?://\S+', re.IGNORECASE)
_SOURCE_LINE = re.compile(r'(?i)^(?:source|read more|watch(?: it)?|official site)\s*:\s*.*$')
_WIKIPEDIA_LINE = re.compile(
    r'(?i)^(?:this article|the plot|plot summary)\s+(?:is|was)\s+(?:from|based on)\s+wikipedia.*$'
)
_ATTRIBUTION = re.compile(r'(?i)\s*\[?writ+t?en by mal rewrite\]?\s*$')


def feature_synopsis(value: str | None) -> str | None:
    """Remove known metadata and promotional boilerplate from model input only."""
    if not value:
        return None
    lines = []
    for line in value.splitlines():
        cleaned = _URL.sub('', line).strip()
        if not cleaned or _SOURCE_LINE.match(cleaned) or _WIKIPEDIA_LINE.match(cleaned):
            continue
        lines.append(cleaned)
    cleaned = _ATTRIBUTION.sub('', ' '.join(lines))
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned or None


def feature_synopsis_column(frame: pl.DataFrame, *, source_column: str = 'synopsis') -> pl.DataFrame:
    """Add a feature-only synopsis column through Polars expressions."""
    if source_column not in frame.columns:
        raise ValueError(f'synopsis source column is missing: {source_column}')
    return frame.with_columns(
        pl.col(source_column)
        .fill_null('')
        .str.replace_all(r'https?://\S+', '')
        .str.replace_all(r'(?im)^(?:source|read more|watch(?: it)?|official site)\s*:.*$', '')
        .str.replace_all(
            r'(?im)^(?:this article|the plot|plot summary)\s+(?:is|was)\s+(?:from|based on)\s+wikipedia.*$', ''
        )
        .str.replace_all(r'(?i)\s*\[?writ+t?en by mal rewrite\]?\s*$', '')
        .str.replace_all(r'\s+', ' ')
        .str.strip_chars()
        .replace('', None)
        .alias('synopsis_features')
    )
