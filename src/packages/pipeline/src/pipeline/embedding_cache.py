"""Pipeline-owned loading and persistence for optional embedding artifacts."""

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import msgspec
import numpy as np
from numpy.typing import NDArray

from config import LogEvent, bind_logger, derive_payload_identity, emit_event
from features.config import EmbeddingModel, FeatureConfig
from features.embeddings import encode_synopsis_embeddings
from pipeline.contracts import EmbeddingCacheManifest
from storage.arrays import read_array, write_array
from storage.errors import StorageError
from storage.json_io import read_json, write_json

EmbeddingMatrix = NDArray[np.float32]
EMBEDDING_CACHE_SCHEMA = 'embedding-cache-v4'
_MATRIX_DIMENSIONS = 2
log = bind_logger(package='pipeline', stage='embeddings')


class _ReusableEmbeddingRows(msgspec.Struct, frozen=True):
    values: EmbeddingMatrix
    row_indices: dict[str, int]


class _LegacyEmbeddingCacheManifest(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Describe the v3 embedding manifest retained for one-time cache migration."""

    schema_version: str
    model_name: str
    model_path: str
    local_only: bool
    row_count: int
    text_hash: str
    ordered_ids_hash: str
    source_snapshot_id: str | None
    source_artifact_sha256: str | None
    row_keys: tuple[str, ...]
    generated_at: str = ''


def prepare_embedding_cache(
    texts: Sequence[str | None],
    ordered_ids: Sequence[int],
    *,
    config: FeatureConfig,
    cache_path: Path | None,
    source_artifact_sha256: str | None,
) -> EmbeddingMatrix | None:
    """Reuse or generate embeddings when the feature configuration enables them."""
    if config.embedding is None:
        return None
    if len(texts) != len(ordered_ids):
        raise ValueError('embedding texts and IDs must have the same length')
    clean_texts = _clean_texts(texts)
    row_keys = _embedding_row_keys(clean_texts, ordered_ids)
    expected = _cache_manifest(
        texts,
        ordered_ids,
        config=config,
        source_artifact_sha256=source_artifact_sha256,
        include_timestamp=False,
    )
    artifact_identity = derive_payload_identity(expected)
    if cache_path is not None:
        cached = load_embedding_cache(cache_path, expected=expected, row_count=len(ordered_ids))
        if cached is not None:
            emit_event(
                log,
                LogEvent(
                    event_name='cache.decision',
                    package='pipeline',
                    stage='embeddings',
                    cache_decision='reused',
                    cache_reason='identity-and-alignment-match',
                    row_count=len(ordered_ids),
                    artifact_identity=artifact_identity,
                ),
            )
            return cached
    emit_event(
        log,
        LogEvent(
            event_name='cache.decision',
            package='pipeline',
            stage='embeddings',
            cache_decision='rebuilt',
            cache_reason='missing-or-invalid' if cache_path is not None else 'cache-disabled',
            row_count=len(ordered_ids),
            artifact_identity=artifact_identity,
        ),
    )
    reusable = _load_reusable_rows(cache_path, config=config) if cache_path is not None else None
    values = _build_embedding_matrix(clean_texts, row_keys, reusable, config=config)
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        write_array(cache_path, values)
        write_json(
            _manifest_path(cache_path),
            _cache_manifest(
                texts,
                ordered_ids,
                config=config,
                source_artifact_sha256=source_artifact_sha256,
                include_timestamp=True,
            ),
        )
        log.info('Wrote embedding cache for {} rows to {}.', len(ordered_ids), cache_path)
    return values


def _build_embedding_matrix(
    texts: Sequence[str],
    row_keys: Sequence[str],
    reusable: _ReusableEmbeddingRows | None,
    *,
    config: FeatureConfig,
) -> EmbeddingMatrix:
    """Reuse unchanged rows and encode only new or changed synopsis text."""
    model = _configured_model(config)
    if reusable is None:
        return encode_synopsis_embeddings(
            texts,
            model_name=model.identifier,
            revision=model.revision,
            local_only=model.local_only,
        )

    values = np.empty((len(texts), reusable.values.shape[1]), dtype=np.float32)
    missing_indices: list[int] = []
    missing_texts: list[str] = []
    for index, (row_key, text) in enumerate(zip(row_keys, texts, strict=True)):
        cached_index = reusable.row_indices.get(row_key)
        if cached_index is None:
            missing_indices.append(index)
            missing_texts.append(text)
        else:
            values[index] = reusable.values[cached_index]

    if missing_texts:
        generated = encode_synopsis_embeddings(
            missing_texts,
            model_name=model.identifier,
            revision=model.revision,
            local_only=model.local_only,
        )
        if generated.shape[1] != values.shape[1]:
            raise ValueError('embedding cache dimensions do not match the current model')
        values[missing_indices] = generated
    return values


def load_embedding_cache(
    cache_path: Path,
    *,
    expected: EmbeddingCacheManifest,
    row_count: int,
) -> EmbeddingMatrix | None:
    """Load an aligned cache only when its complete semantic manifest matches."""
    manifest_path = _manifest_path(cache_path)
    if not cache_path.is_file() or not manifest_path.is_file():
        return None
    try:
        manifest = read_json(manifest_path, EmbeddingCacheManifest)
        if _without_timestamp(manifest) != expected:
            return None
        values = np.asarray(read_array(cache_path), dtype=np.float32)
        if values.ndim != _MATRIX_DIMENSIONS or values.shape[0] != row_count:
            return None
    except (StorageError, ValueError):
        return None
    else:
        return values


def _cache_manifest(
    texts: Sequence[str | None],
    ordered_ids: Sequence[int],
    *,
    config: FeatureConfig,
    source_artifact_sha256: str | None,
    include_timestamp: bool,
) -> EmbeddingCacheManifest:
    """Build the semantic manifest that proves an embedding cache is reusable."""
    clean = _clean_texts(texts)
    if config.embedding is None:
        raise ValueError('embedding model is required to build a cache manifest')
    return EmbeddingCacheManifest(
        schema_version=EMBEDDING_CACHE_SCHEMA,
        model=config.embedding,
        row_count=len(clean),
        text_hash=derive_payload_identity(clean),
        ordered_ids_hash=derive_payload_identity(ordered_ids),
        source_snapshot_id=config.source_snapshot_id,
        source_artifact_sha256=source_artifact_sha256,
        row_keys=_embedding_row_keys(clean, ordered_ids),
        generated_at=datetime.now(UTC).isoformat() if include_timestamp else '',
    )


def _manifest_path(cache_path: Path) -> Path:
    """Return the sidecar manifest path for an embedding array."""
    return cache_path.with_suffix(cache_path.suffix + '.manifest.json')


def _clean_texts(texts: Sequence[str | None]) -> tuple[str, ...]:
    """Normalize missing synopsis values before embedding and cache-key generation."""
    return tuple(' '.join((text or '').split()) for text in texts)


def _embedding_row_keys(texts: Sequence[str], ordered_ids: Sequence[int]) -> tuple[str, ...]:
    """Create stable per-row keys from anime IDs and cleaned synopsis text."""
    return tuple(
        derive_payload_identity({'anime_id': anime_id, 'text': text})
        for anime_id, text in zip(ordered_ids, texts, strict=True)
    )


def _load_reusable_rows(cache_path: Path, *, config: FeatureConfig) -> _ReusableEmbeddingRows | None:
    """Load a model-compatible cache even when catalogue order or membership changed."""
    manifest_path = _manifest_path(cache_path)
    if not cache_path.is_file() or not manifest_path.is_file():
        return None
    try:
        manifest = read_json(manifest_path, EmbeddingCacheManifest)
        if not _current_manifest_matches_model(manifest, config):
            return None
        return _load_reusable_values(cache_path, manifest.row_keys)
    except (StorageError, ValueError):
        return _load_legacy_reusable_rows(manifest_path, cache_path, config)


def _load_legacy_reusable_rows(
    manifest_path: Path,
    cache_path: Path,
    config: FeatureConfig,
) -> _ReusableEmbeddingRows | None:
    """Load the previous flattened manifest format for a safe one-time migration."""
    try:
        manifest = read_json(manifest_path, _LegacyEmbeddingCacheManifest)
        if not _legacy_manifest_matches_model(manifest, config):
            return None
        return _load_reusable_values(cache_path, manifest.row_keys)
    except (StorageError, ValueError):
        return None


def _load_reusable_values(cache_path: Path, row_keys: Sequence[str]) -> _ReusableEmbeddingRows | None:
    """Validate reusable embedding rows and build their row-key lookup."""
    values = np.asarray(read_array(cache_path), dtype=np.float32)
    shape_matches = values.ndim == _MATRIX_DIMENSIONS and values.shape[0] == len(row_keys)
    if not shape_matches or len(set(row_keys)) != len(row_keys):
        return None
    return _ReusableEmbeddingRows(values=values, row_indices={key: index for index, key in enumerate(row_keys)})


def _current_manifest_matches_model(manifest: EmbeddingCacheManifest, config: FeatureConfig) -> bool:
    """Check the current manifest schema and configured model identity."""
    return (
        manifest.schema_version == EMBEDDING_CACHE_SCHEMA
        and config.embedding is not None
        and manifest.model == config.embedding
    )


def _legacy_manifest_matches_model(manifest: _LegacyEmbeddingCacheManifest, config: FeatureConfig) -> bool:
    """Check the flattened v3 model fields against the current local model."""
    model = config.embedding
    return (
        manifest.schema_version == 'embedding-cache-v3'
        and model is not None
        and manifest.model_name == Path(model.identifier).name
        and manifest.model_path == model.identifier
        and manifest.local_only == model.local_only
    )


def _without_timestamp(manifest: EmbeddingCacheManifest) -> EmbeddingCacheManifest:
    """Remove runtime-only generation time before comparing cache identities."""
    return EmbeddingCacheManifest(
        schema_version=manifest.schema_version,
        model=manifest.model,
        row_count=manifest.row_count,
        text_hash=manifest.text_hash,
        ordered_ids_hash=manifest.ordered_ids_hash,
        source_snapshot_id=manifest.source_snapshot_id,
        source_artifact_sha256=manifest.source_artifact_sha256,
        row_keys=manifest.row_keys,
    )


def _configured_model(config: FeatureConfig) -> EmbeddingModel:
    """Return the configured model or explain why embedding generation is disabled."""
    if config.embedding is None:
        raise ValueError('embedding model is required to generate embeddings')
    return config.embedding
