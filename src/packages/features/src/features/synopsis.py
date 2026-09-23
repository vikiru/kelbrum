"""Configurable synopsis-only feature builders used by catalogue pipelines."""

from collections.abc import Sequence

import msgspec
import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import normalize

_MIN_PROJECTION_INPUT_SIZE = 2


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


def clean_synopses(texts: Sequence[str | None]) -> list[str]:
    """Normalize missing and whitespace-only synopsis values consistently."""
    return [' '.join((text or '').split()) for text in texts]


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


def bm25(texts: Sequence[str | None], *, k1: float = 1.5, b: float = 0.75) -> SynopsisFeatures:
    """Build a sparse BM25-weighted term matrix for exact cosine retrieval."""
    if k1 < 0.0 or b < 0.0 or b > 1.0:
        raise ValueError('BM25 requires k1 >= 0 and b in [0, 1]')
    base = CountVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)
    cleaned = clean_synopses(texts)
    if not any(cleaned):
        return SynopsisFeatures(csr_matrix((len(cleaned), 0), dtype=np.float32), ())
    try:
        counts = csr_matrix(base.fit_transform(cleaned), dtype=np.float32)
    except ValueError as error:
        if 'empty vocabulary' not in str(error).lower():
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
    normalized = normalize(weighted, norm='l2', axis=1, copy=False).tocsr()
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
