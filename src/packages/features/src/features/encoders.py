"""Feature encoders for categorical, set-valued, text, and episode data."""

import hashlib
import re
from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

import msgspec
import numpy as np
import torch
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from sentence_transformers import SentenceTransformer

from features.constants import DEFAULT_EMBEDDING_MODEL
from normalization.encoders import bucketize, clean_labels, multi_hot
from normalization.scalers import log1p
from storage.arrays import read_array
from storage.json_io import read_json, write_json

EMBEDDING_BATCH_SIZE = 128


def _embedding_device() -> str:
    """Select CUDA when available and retain a portable CPU fallback."""
    return 'cuda' if torch.cuda.is_available() else 'cpu'


@lru_cache(maxsize=4)
def _embedding_model(model_name: str, local_only: bool, device: str) -> SentenceTransformer:
    model_kwargs = {'local_files_only': True} if local_only else None
    return SentenceTransformer(model_name, model_kwargs=model_kwargs, device=device)


def synopsis_embeddings(
    texts: Sequence[str | None],
    *,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    cache_path: Path | None = None,
    ordered_ids: Sequence[int] | NDArray[np.int64] | None = None,
    source_snapshot_id: str | None = None,
    logical_model_name: str | None = None,
    source_artifact_sha256: str | None = None,
    local_only: bool = True,
) -> NDArray[np.float32]:
    """Encode synopsis text using a caller-selected sentence-transformer model."""
    if not model_name.strip():
        raise ValueError('embedding model name cannot be empty')
    clean = [' '.join((text or '').split()) for text in texts]
    if ordered_ids is not None and len(ordered_ids) != len(clean):
        raise ValueError('ordered_ids must match synopsis rows')
    manifest_path = cache_path.with_suffix(cache_path.suffix + '.manifest.json') if cache_path is not None else None
    expected_manifest = {
        'model_name': logical_model_name or model_name,
        'row_count': len(clean),
        'text_hash': hashlib.sha256(msgspec.json.encode(clean)).hexdigest(),
        'ordered_mal_ids_hash': hashlib.sha256(
            msgspec.json.encode([int(value) for value in (ordered_ids if ordered_ids is not None else ())])
        ).hexdigest()
        if ordered_ids is not None
        else None,
        'source_snapshot_id': source_snapshot_id,
        'source_artifact_sha256': source_artifact_sha256,
        'preprocessing_version': 2,
        'generated_at': datetime.now(UTC).isoformat(),
    }
    if cache_path is not None and cache_path.is_file():
        if manifest_path is None or not manifest_path.is_file():
            raise ValueError(f'embedding cache is missing its manifest: {cache_path}')
        manifest = read_json(manifest_path, dict[str, object])
        comparable = {key: value for key, value in expected_manifest.items() if key != 'generated_at'}
        if not any(value is not None and manifest.get(key) != value for key, value in comparable.items()):
            cached = read_array(cache_path)
            if cached.ndim == 2 and cached.shape[0] == len(clean):
                return np.asarray(cached, dtype=np.float32)
    model = _embedding_model(model_name, local_only, _embedding_device())
    embeddings = _encode_in_batches(model, clean)
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = cache_path.with_name(f'{cache_path.name}.tmp.npy')
        temporary_path.unlink(missing_ok=True)
        try:
            _write_embedding_cache(temporary_path, embeddings)
            temporary_path.replace(cache_path)
        finally:
            temporary_path.unlink(missing_ok=True)
        if manifest_path is not None:
            write_json(manifest_path, expected_manifest)
    return embeddings


def _encode_in_batches(model: SentenceTransformer, texts: Sequence[str]) -> NDArray[np.float32]:
    """Encode sentence-aware token chunks and mean-pool each synopsis."""
    if not texts:
        dimension = model.get_embedding_dimension() or 0
        return np.empty((0, dimension), dtype=np.float32)
    tokenizer = model.tokenizer
    sequence_length = model.max_seq_length or 3
    chunk_limit = max(sequence_length - 2, 1)
    chunks: list[str] = []
    owners: list[int] = []
    for owner, text in enumerate(texts):
        sentences = tuple(part.strip() for part in re.split(r'(?<=[.!?])\s+', text) if part.strip())
        pending: list[int] = []
        for sentence in sentences:
            sentence_ids = tokenizer.encode(sentence, add_special_tokens=False, truncation=False)
            if len(sentence_ids) > chunk_limit:
                if pending:
                    chunks.append(tokenizer.decode(pending, skip_special_tokens=True).strip())
                    owners.append(owner)
                    pending = []
                for start in range(0, len(sentence_ids), chunk_limit):
                    chunks.append(
                        tokenizer.decode(sentence_ids[start : start + chunk_limit], skip_special_tokens=True).strip()
                    )
                    owners.append(owner)
                continue
            if pending and len(pending) + len(sentence_ids) > chunk_limit:
                chunks.append(tokenizer.decode(pending, skip_special_tokens=True).strip())
                owners.append(owner)
                pending = []
            pending.extend(sentence_ids)
        if pending:
            chunks.append(tokenizer.decode(pending, skip_special_tokens=True).strip())
            owners.append(owner)
    dimension = model.get_embedding_dimension() or 0
    if not chunks:
        return np.zeros((len(texts), dimension), dtype=np.float32)
    pooled = np.zeros((len(texts), dimension), dtype=np.float32)
    counts = np.zeros(len(texts), dtype=np.int32)
    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        stop = start + EMBEDDING_BATCH_SIZE
        encoded = model.encode(
            chunks[start:stop],
            batch_size=EMBEDDING_BATCH_SIZE,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        for vector, owner in zip(np.asarray(encoded, dtype=np.float32), owners[start:stop], strict=True):
            pooled[owner] += vector
            counts[owner] += 1
    present = counts > 0
    pooled[present] /= counts[present, None]
    norms = np.linalg.norm(pooled[present], axis=1, keepdims=True)
    pooled[present] /= np.where(norms == 0.0, 1.0, norms)
    return pooled


def _write_embedding_cache(path: Path, embeddings: NDArray[np.float32]) -> None:
    """Write embeddings through a memory-mapped array to bound temporary memory use."""
    mapped = np.lib.format.open_memmap(
        path,
        mode='w+',
        dtype=np.float32,
        shape=embeddings.shape,
    )
    try:
        mapped[:] = embeddings
        mapped.flush()
    finally:
        del mapped


def episode_buckets(
    episodes: Sequence[int | None],
    *,
    boundaries: tuple[int, ...] = (1, 12, 17, 29, 51, 101, 301, 500),
) -> tuple[csr_matrix, tuple[str, ...]]:
    """Encode episode counts using configurable inclusive lower bounds."""
    if not boundaries or boundaries[0] != 1 or tuple(sorted(boundaries)) != boundaries:
        raise ValueError('episode boundaries must be sorted and start at 1')
    return bucketize(episodes, boundaries=boundaries, missing_below=1)


def year_buckets(
    years: Sequence[int | None],
    *,
    boundaries: tuple[int, ...] = (1917, 1980, 1992, 2008, 2016, 2021, 2025),
) -> tuple[csr_matrix, tuple[str, ...]]:
    """Encode release years into configurable inclusive ranges."""
    if not boundaries or tuple(sorted(boundaries)) != boundaries:
        raise ValueError('year boundaries must be sorted and non-empty')
    return bucketize(years, boundaries=boundaries, missing_below=boundaries[0])


def year_continuous(years: Sequence[int | None], *, minimum: int = 1917, maximum: int = 2027) -> NDArray[np.float32]:
    """Return bounded year values while preserving missing years as NaN."""
    if minimum >= maximum:
        raise ValueError('minimum year must be less than maximum year')
    values = np.asarray([float(year) if year is not None else np.nan for year in years], dtype=np.float32)
    return np.asarray(np.clip((values - minimum) / (maximum - minimum), 0.0, 1.0), dtype=np.float32)


def episode_log1p(episodes: Sequence[int | None]) -> NDArray[np.float64]:
    """Return log1p episode counts while preserving missing values as NaN."""
    values = np.asarray([float(count) if count is not None and count >= 0 else np.nan for count in episodes])
    present = np.isfinite(values)
    output = np.full(values.shape, np.nan, dtype=np.float64)
    output[present] = log1p(values[present]).ravel()
    return output


def studio_multi_hot(
    studios: Iterable[Iterable[str]], *, minimum_frequency: int = 3
) -> tuple[csr_matrix, tuple[str, ...]]:
    """Build an opt-in studio block while pruning rare studios."""
    rows = [clean_labels(row) for row in studios]
    frequencies = Counter(studio for row in rows for studio in row)
    retained = [tuple(studio for studio in row if frequencies[studio] >= minimum_frequency) for row in rows]
    return multi_hot(retained)


def studio_frequency(studios: Iterable[Iterable[str]]) -> NDArray[np.float32]:
    """Return the number of catalogue titles associated with each anime's studios."""
    rows = [set(clean_labels(row)) for row in studios]
    frequencies = Counter(studio for row in rows for studio in row)
    return np.asarray([sum(frequencies[studio] for studio in row) for row in rows], dtype=np.float32)


def studio_quality_features(
    studios: Iterable[Iterable[str]],
    scores: Sequence[float | None],
    ranks: Sequence[float | None],
) -> NDArray[np.float32]:
    """Return optional studio median score/rank and title-count features.

    Aggregates are computed from the supplied catalogue only. Missing values remain NaN
    so the owning feature policy can choose an appropriate imputation strategy.
    """
    rows = [set(clean_labels(row)) for row in studios]
    if len(rows) != len(scores) or len(rows) != len(ranks):
        raise ValueError('studios, scores, and ranks must have the same length')
    score_by_studio: dict[str, list[float]] = {}
    rank_by_studio: dict[str, list[float]] = {}
    for row, score, rank in zip(rows, scores, ranks, strict=True):
        for studio in row:
            if score is not None:
                score_by_studio.setdefault(studio, []).append(score)
            if rank is not None:
                rank_by_studio.setdefault(studio, []).append(rank)
    output = np.full((len(rows), 3), np.nan, dtype=np.float32)
    for index, row in enumerate(rows):
        score_values = [value for studio in row for value in score_by_studio.get(studio, [])]
        rank_values = [value for studio in row for value in rank_by_studio.get(studio, [])]
        if score_values:
            output[index, 0] = np.median(score_values)
        if rank_values:
            output[index, 1] = np.median(rank_values)
        output[index, 2] = sum(len(score_by_studio.get(studio, [])) for studio in row)
    return output
