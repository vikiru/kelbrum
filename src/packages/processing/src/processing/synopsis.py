"""Separate display synopsis text from conservative feature text."""

import re

import polars as pl

_URL = re.compile(r'https?://\S+', re.IGNORECASE)
_SOURCE_LINE = re.compile(r'(?i)^(?:source|read more|watch(?: it)?|official site)\s*:\s*.*$')
_WIKIPEDIA_LINE = re.compile(
    r'(?i)^(?:this article|the plot|plot summary)\s+(?:is|was)\s+(?:from|based on)\s+wikipedia.*$'
)
SOURCE_CITATION_PATTERN = (
    r'(?i)\s+source\s*:\s*(?:\(?\s*)?(?:ann\b|official\s+website\b|myanimelist\b|mal\s+rewrite\b|'
    r'https?://\S+|[\w.-]+\.(?:org|com|net|jp)\b)[^\n]*\s*$'
)
_SOURCE_CITATION = re.compile(SOURCE_CITATION_PATTERN)
ATTRIBUTION_PATTERN = (
    r'(?i)(?:'
    r'\[writ+t?en by [^\]]+\]'
    r'|\(writ+t?en by [^)]+\)'
    r'|\((?:source|translated by)\s*:[^)]*\)'
    r'|\[(?:source|translated by)\s*:[^]]*\]'
    r')'
    r'(?:\s*(?:About\s+[A-Z]|Note\s*(?:that|the|:)|Based on|\*Based on|'
    r'Project by|Double feature|Aired along side)[^\n]*$)?'
)
_ATTRIBUTION = re.compile(ATTRIBUTION_PATTERN)


def feature_synopsis(value: str | None) -> str | None:
    """Remove known metadata and promotional boilerplate from model input only."""
    if not value:
        return None
    lines = []
    for line in value.splitlines():
        cleaned = _SOURCE_CITATION.sub('', line)
        cleaned = _URL.sub('', cleaned).strip()
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
        .str.replace_all(SOURCE_CITATION_PATTERN, '')
        .str.replace_all(r'https?://\S+', '')
        .str.replace_all(r'(?im)^(?:source|read more|watch(?: it)?|official site)\s*:.*$', '')
        .str.replace_all(
            r'(?im)^(?:this article|the plot|plot summary)\s+(?:is|was)\s+(?:from|based on)\s+wikipedia.*$', ''
        )
        .str.replace_all(ATTRIBUTION_PATTERN, '')
        .str.replace_all(r'\s+', ' ')
        .str.strip_chars()
        .replace('', None)
        .alias('synopsis_features')
    )
