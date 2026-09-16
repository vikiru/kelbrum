"""Optional synopsis embedding generation without persistence concerns."""

from collections.abc import Mapping, Sequence
from functools import lru_cache
from importlib import import_module
from re import split
from typing import Protocol, cast

import numpy as np
from numpy.typing import NDArray


class _CudaModule(Protocol):
    def is_available(self) -> bool: ...


class _TorchModule(Protocol):
    cuda: _CudaModule


class _SentenceTransformersModule(Protocol):
    SentenceTransformer: type['_SentenceTransformer']


class _Tokenizer(Protocol):
    def encode(self, text: str, *, add_special_tokens: bool, truncation: bool) -> list[int]: ...

    def decode(self, token_ids: Sequence[int], *, skip_special_tokens: bool) -> str: ...


class _SentenceTransformer(Protocol):
    def __init__(
        self,
        model_name: str,
        *,
        revision: str | None,
        model_kwargs: Mapping[str, object] | None,
        device: str,
    ) -> None: ...

    max_seq_length: int | None
    tokenizer: _Tokenizer

    def get_embedding_dimension(self) -> int | None: ...

    def encode(
        self,
        texts: Sequence[str],
        *,
        batch_size: int,
        normalize_embeddings: bool,
        convert_to_numpy: bool,
        show_progress_bar: bool,
    ) -> NDArray[np.floating]: ...


EMBEDDING_BATCH_SIZE = 128


def encode_synopsis_embeddings(
    texts: Sequence[str | None],
    *,
    model_name: str,
    revision: str | None = None,
    local_only: bool = True,
) -> NDArray[np.float32]:
    """Encode synopsis text; callers own caching and artifact persistence."""
    if not model_name.strip():
        raise ValueError('embedding model name cannot be empty')
    clean = [' '.join((text or '').split()) for text in texts]
    model = _embedding_model(model_name, revision, local_only, _embedding_device())
    return _encode_in_batches(model, clean)


def _embedding_device() -> str:
    """Select CUDA when available and retain a portable CPU fallback."""
    torch = cast('_TorchModule', import_module('torch'))
    return 'cuda' if torch.cuda.is_available() else 'cpu'


@lru_cache(maxsize=4)
def _embedding_model(
    model_name: str,
    revision: str | None,
    local_only: bool,
    device: str,
) -> _SentenceTransformer:
    module = cast('_SentenceTransformersModule', import_module('sentence_transformers'))
    model_kwargs = {'local_files_only': True} if local_only else None
    return module.SentenceTransformer(model_name, revision=revision, model_kwargs=model_kwargs, device=device)


def _encode_in_batches(model: _SentenceTransformer, texts: Sequence[str]) -> NDArray[np.float32]:
    """Encode sentence-aware token chunks and mean-pool each synopsis."""
    if not texts:
        dimension = model.get_embedding_dimension() or 0
        return np.empty((0, dimension), dtype=np.float32)
    sequence_length = model.max_seq_length or 3
    chunk_limit = max(sequence_length - 2, 1)
    chunks: list[str] = []
    owners: list[int] = []
    for owner, text in enumerate(texts):
        text_chunks = _chunk_text(model, text, chunk_limit)
        chunks.extend(text_chunks)
        owners.extend([owner] * len(text_chunks))
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


def _chunk_text(model: _SentenceTransformer, text: str, chunk_limit: int) -> list[str]:
    """Split one synopsis into tokenizer-sized, sentence-aware chunks."""
    tokenizer = model.tokenizer
    sentences = tuple(part.strip() for part in split(r'(?<=[.!?])\s+', text) if part.strip())
    chunks: list[str] = []
    pending: list[int] = []
    for sentence in sentences:
        sentence_ids = tokenizer.encode(sentence, add_special_tokens=False, truncation=False)
        if len(sentence_ids) > chunk_limit:
            if pending:
                chunks.append(tokenizer.decode(pending, skip_special_tokens=True).strip())
                pending = []
            chunks.extend(
                tokenizer.decode(sentence_ids[start : start + chunk_limit], skip_special_tokens=True).strip()
                for start in range(0, len(sentence_ids), chunk_limit)
            )
            continue
        if pending and len(pending) + len(sentence_ids) > chunk_limit:
            chunks.append(tokenizer.decode(pending, skip_special_tokens=True).strip())
            pending = []
        pending.extend(sentence_ids)
    if pending:
        chunks.append(tokenizer.decode(pending, skip_special_tokens=True).strip())
    return chunks
