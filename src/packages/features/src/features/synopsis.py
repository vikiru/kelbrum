"""Configurable synopsis-only feature builders used by catalogue pipelines."""

import re
from collections.abc import Sequence

import msgspec
import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import normalize

_MIN_PROJECTION_INPUT_SIZE = 2

NON_NARRATIVE_SENTENCE_PATTERNS: tuple[str, ...] = (
    r'(?i)\b(?:based\s+on|adapted\s+from|serialized\s+in)\s+(?:the\s+)?(?:hit\s+|popular\s+|award[- ]winning\s+)?'
    r'(?:light\s+novel|manga|web\s+novel|visual\s+novel|novel|game|4-koma|webtoon|eroge|mobile\s+game|'
    r'media\s+franchise|card\s+game|toy\s+line|playstation\s+game|novel\s+series)\b',
    r'(?i)\b(?:won|received|awarded|recipient of|nominated for)\b.*?\b(?:award|prize|festival|excellence)\b',
    r'(?i)\b(?:season\s+[0-9]+|part\s+[0-9]+|cour\s+[0-9]+)\s+(?:focuses|continues|follows|picks up|takes place)\b',
    r'(?i)\b(?:at the end of|where it left off at|prior to the events of)\s+season\s+[0-9]+\b',
    r'(?i)\b(?:included\s+in|bundled\s+with)\s+the\s+(?:[0-9]+(?:st|nd|rd|th)\s+)?(?:blu-ray|dvd|manga|volume)\b',
    r'(?i)\bthe\s+japan\s+blu-ray/dvd\s+release\s+date\s+is\b',
    r'(?i)\bno\s+synopsis\s+has\s+been\s+added\s+for\s+this\s+series\s+yet\b',
    r'(?i)\bclick\s+here\s+to\s+update\s+this\s+information\b',
    r'(?i)\[written\s+by\s+mal\s+rewrite\]',
    r'(?i)\(source:\s*[^)]+\)',
    r'(?i)\bsource:\s*[^.!?]+[.!?]?',
    r'(?i)^\s*(?:broadcast|airing|aired on|premiere[sd]? on|licensed by|streamed on)\b.*',
)

_NON_NARRATIVE_DISCARD_REGEX: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern) for pattern in NON_NARRATIVE_SENTENCE_PATTERNS
)

SEQUEL_SPARSE_CONTINUATION_PATTERN: str = (
    r'(?i)^\s*(?:'
    r'(?:the\s+)?(?:second|2nd|third|3rd|fourth|4th|fifth|5th|final|next)\s+(?:season|series|part|cour)\b'
    r'|sequel\s+to\b'
    r'|continuation\s+of\b'
    r'|direct\s+continuation\b'
    r'|second\s+half\s+of\b'
    r'|remake\s+of\b'
    r'|season\s+[0-9]+\b'
    r'|part\s+[0-9]+\b'
    r')'
)

_SEQUEL_SPARSE_REGEX: re.Pattern[str] = re.compile(SEQUEL_SPARSE_CONTINUATION_PATTERN)
_SENTENCE_SPLIT_REGEX: re.Pattern[str] = re.compile(r'(?<=[.!?])\s+|\n+')
_TOKEN_BOUNDS_REGEX: re.Pattern[str] = re.compile(r'^[^\w]+|[^\w]+$')


class TfidfConfig(msgspec.Struct, frozen=True):
    """Stable TF-IDF vectorizer settings."""

    ngram_range: tuple[int, int] = (1, 2)
    sublinear_tf: bool = True
    stop_words: str | None = 'english'
    min_df: int = 2
    max_df: float = 0.95
    max_features: int = 5_000


class LatentConfig(msgspec.Struct, frozen=True):
    """Stable latent synopsis projection settings."""

    dimensions: int = 200
    random_state: int = 42
    max_iter: int = 200


class SynopsisFeatures(msgspec.Struct, frozen=True):
    """Aligned synopsis matrix and vocabulary metadata."""

    matrix: csr_matrix
    vocabulary: tuple[str, ...]


def is_sparse_sequel_synopsis(text: str | None, *, max_length: int = 200) -> bool:
    """Detect whether a synopsis is a sparse sequel placeholder lacking narrative context."""
    if not text:
        return True
    stripped = text.strip()
    if len(stripped) < 60:
        return True
    return len(stripped) < max_length and bool(_SEQUEL_SPARSE_REGEX.search(stripped))


def clean_single_synopsis(text: str | None, *, strip_mid_sentence_nouns: bool = True) -> str:
    """Normalize whitespace, purge non-narrative metadata, and optionally strip proper nouns."""
    if not text:
        return ''
    cleaned = re.sub(r'(?i)\[written\s+by\s+mal\s+rewrite\]', '', text)
    cleaned = re.sub(r'(?i)\(source:\s*[^)]+\)', '', cleaned)

    raw_sentences = _SENTENCE_SPLIT_REGEX.split(cleaned)
    kept_sentences: list[str] = []
    for sentence in raw_sentences:
        candidate_sentence = sentence.strip()
        if not candidate_sentence:
            continue
        if any(regex.search(candidate_sentence) for regex in _NON_NARRATIVE_DISCARD_REGEX):
            continue

        if strip_mid_sentence_nouns:
            tokens = candidate_sentence.split()
            if not tokens:
                continue
            preserved_tokens = [tokens[0]]
            for token in tokens[1:]:
                bare_token = _TOKEN_BOUNDS_REGEX.sub('', token)
                if bare_token and bare_token[0].isupper() and bare_token != 'I' and not bare_token.isdigit():  # noqa: S105
                    continue
                preserved_tokens.append(token)
            kept_sentences.append(' '.join(preserved_tokens))
        else:
            kept_sentences.append(candidate_sentence)

    return ' '.join(kept_sentences).strip()


def clean_synopses(texts: Sequence[str | None], *, strip_mid_sentence_nouns: bool = True) -> list[str]:
    """Normalize missing values, strip non-narrative metadata sentences, and remove proper nouns."""
    return [clean_single_synopsis(text, strip_mid_sentence_nouns=strip_mid_sentence_nouns) for text in texts]


def tfidf(texts: Sequence[str | None], config: TfidfConfig | None = None) -> SynopsisFeatures:
    """Build a deterministic sparse TF-IDF representation."""
    active = config or TfidfConfig()
    if active.min_df < 1 or active.max_features < 1:
        raise ValueError('min_df and max_features must be positive')
    if not 0.0 < active.max_df <= 1.0:
        raise ValueError('max_df must be greater than 0 and at most 1')
    cleaned = clean_synopses(texts)
    if not any(cleaned):
        return SynopsisFeatures(csr_matrix((len(cleaned), 0), dtype=np.float32), ())
    vectorizer = TfidfVectorizer(
        ngram_range=active.ngram_range,
        sublinear_tf=active.sublinear_tf,
        stop_words=active.stop_words,
        min_df=active.min_df,
        max_df=active.max_df,
        max_features=active.max_features,
        strip_accents='unicode',
    )
    try:
        matrix = vectorizer.fit_transform(cleaned)
    except ValueError as error:
        message = str(error).lower()
        if not any(
            fragment in message
            for fragment in ('no terms remain', 'empty vocabulary', 'max_df corresponds to < documents')
        ):
            raise
        return SynopsisFeatures(csr_matrix((len(cleaned), 0), dtype=np.float32), ())
    return SynopsisFeatures(csr_matrix(matrix, dtype=np.float32), tuple(vectorizer.get_feature_names_out()))


def bm25(
    texts: Sequence[str | None],
    *,
    k1: float = 1.5,
    b: float = 0.75,
    min_df: int = 1,
    max_features: int = 25_000,
) -> SynopsisFeatures:
    """Build a sparse BM25-weighted term matrix for exact cosine retrieval."""
    if k1 < 0.0 or b < 0.0 or b > 1.0:
        raise ValueError('BM25 requires k1 >= 0 and b in [0, 1]')
    if min_df < 1 or max_features < 1:
        raise ValueError('min_df and max_features must be positive')
    cleaned = clean_synopses(texts)
    if not any(cleaned):
        return SynopsisFeatures(csr_matrix((len(cleaned), 0), dtype=np.float32), ())
    base = CountVectorizer(
        ngram_range=(1, 2),
        stop_words='english',
        min_df=min_df,
        max_features=max_features,
    )
    try:
        counts = csr_matrix(base.fit_transform(cleaned), dtype=np.float32)
    except ValueError as error:
        message = str(error).lower()
        if not any(
            fragment in message
            for fragment in ('no terms remain', 'empty vocabulary', 'max_df corresponds to < documents')
        ):
            raise
        return SynopsisFeatures(csr_matrix((len(cleaned), 0), dtype=np.float32), ())
    lengths = np.asarray(counts.sum(axis=1)).ravel()
    average_length = float(lengths.mean()) if len(lengths) else 0.0
    denominator = np.full(lengths.shape, k1, dtype=np.float32)
    if average_length:
        denominator = k1 * (1.0 - b + b * lengths / average_length)
    data = counts.data.copy()
    row_indices = np.repeat(np.arange(counts.shape[0]), np.diff(counts.indptr))
    data *= (k1 + 1.0) / (data + denominator[row_indices])
    document_frequency = np.bincount(counts.indices, minlength=counts.shape[1]).astype(np.float32)
    inverse_document_frequency = np.log1p((counts.shape[0] - document_frequency + 0.5) / (document_frequency + 0.5))
    data *= inverse_document_frequency[counts.indices]
    weighted = csr_matrix((data, counts.indices, counts.indptr), shape=counts.shape)
    normalized = normalize(weighted, norm='l2', axis=1, copy=False)
    return SynopsisFeatures(normalized, tuple(base.get_feature_names_out()))


def lsa(tfidf_features: SynopsisFeatures, config: LatentConfig | None = None) -> NDArray[np.float32]:
    """Project TF-IDF features into a normalized LSA/SVD matrix."""
    active = config or LatentConfig()
    rows, columns = tfidf_features.matrix.shape
    if rows < _MIN_PROJECTION_INPUT_SIZE or columns < _MIN_PROJECTION_INPUT_SIZE:
        return np.zeros((rows, 0), dtype=np.float32)
    dimensions = min(active.dimensions, rows - 1, columns - 1)
    projected = TruncatedSVD(n_components=dimensions, random_state=active.random_state).fit_transform(
        tfidf_features.matrix
    )
    return np.asarray(normalize(projected, norm='l2'), dtype=np.float32)


def nmf(tfidf_features: SynopsisFeatures, config: LatentConfig | None = None) -> NDArray[np.float32]:
    """Project TF-IDF features into a normalized NMF matrix."""
    active = config or LatentConfig()
    rows, columns = tfidf_features.matrix.shape
    if rows == 0 or columns == 0:
        return np.zeros((rows, 0), dtype=np.float32)
    dimensions = min(active.dimensions, rows, columns)
    projected = NMF(
        n_components=dimensions,
        init='nndsvda',
        random_state=active.random_state,
        max_iter=active.max_iter,
    ).fit_transform(tfidf_features.matrix)
    return np.asarray(normalize(projected, norm='l2'), dtype=np.float32)
