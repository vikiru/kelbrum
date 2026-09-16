from pathlib import Path
from typing import cast

import numpy as np
import pytest

from features.config import EmbeddingModel, EmbeddingSource, FeatureConfig
from pipeline.cache_metadata import (
    CacheCompatibilityError,
    CacheMetadata,
    build_cache_metadata,
    validate_cache_metadata,
)
from pipeline.contracts import EmbeddingCacheManifest
from pipeline.embedding_cache import load_embedding_cache, prepare_embedding_cache
from pipeline.recommendation_chunks import _load_reusable_manifest
from storage.arrays import write_array
from storage.json_io import write_json


def _metadata(**changes: object) -> CacheMetadata:
    values: dict[str, object] = {
        'artifact_kind': 'feature-matrix',
        'schema_identity': 'features-v2',
        'source_identity': 'snapshot-sha',
        'ordered_ids': (20, 10),
        'shape': (2, 8),
        'content_hash': 'matrix-sha',
        'configuration_identity': 'features-config',
        'policy_identity': 'rating-policy',
        'producer_identity': 'features-producer',
    }
    values.update(changes)
    return build_cache_metadata(
        artifact_kind=cast('str', values['artifact_kind']),
        schema_identity=cast('str', values['schema_identity']),
        source_identity=cast('str', values['source_identity']),
        ordered_ids=cast('tuple[int, ...]', values['ordered_ids']),
        shape=cast('tuple[int, ...]', values['shape']),
        content_hash=cast('str', values['content_hash']),
        configuration_identity=cast('str', values['configuration_identity']),
        policy_identity=cast('str', values['policy_identity']),
        producer_identity=cast('str', values['producer_identity']),
    )


def test_cache_metadata_is_deterministic_and_accepts_matching_inputs() -> None:
    first = _metadata()
    second = _metadata()

    assert first == second
    validate_cache_metadata(first, second)


@pytest.mark.parametrize(
    ('field', 'value'),
    [
        ('schema_identity', 'features-v3'),
        ('source_identity', 'other-snapshot'),
        ('ordered_ids', (10, 20)),
        ('shape', (2, 9)),
        ('content_hash', 'other-matrix'),
        ('configuration_identity', 'other-config'),
        ('policy_identity', 'other-policy'),
        ('producer_identity', 'other-producer'),
    ],
)
def test_cache_metadata_rejects_semantic_or_shape_changes(field: str, value: object) -> None:
    with pytest.raises(CacheCompatibilityError, match='incompatible'):
        validate_cache_metadata(_metadata(), _metadata(**{field: value}))


def test_cache_metadata_rejects_shape_with_wrong_row_count() -> None:
    with pytest.raises(ValueError, match='row count'):
        _metadata(shape=(3, 8))


def test_embedding_cache_loads_an_explicit_path_without_scanning_siblings(tmp_path: Path) -> None:
    expected_path = tmp_path / 'snapshot.npy'
    stale_path = tmp_path / 'stale.npy'
    write_array(expected_path, np.ones((2, 3), dtype=np.float32))
    write_array(stale_path, np.zeros((2, 3), dtype=np.float32))
    expected = EmbeddingCacheManifest(
        schema_version='embedding-cache-v4',
        model=EmbeddingModel(source=EmbeddingSource.REMOTE, identifier='test-model'),
        row_count=2,
        text_hash='',
        ordered_ids_hash='ids',
        source_snapshot_id=None,
        source_artifact_sha256=None,
        row_keys=(),
    )
    write_json(expected_path.with_suffix('.npy.manifest.json'), expected)

    result = load_embedding_cache(expected_path, expected=expected, row_count=2)

    assert expected_path == tmp_path / 'snapshot.npy'
    assert result is not None
    assert np.all(result == 1)


def test_corrupt_embedding_manifest_is_treated_as_a_cache_miss(tmp_path: Path) -> None:
    cache_path = tmp_path / 'snapshot.npy'
    write_array(cache_path, np.ones((2, 3), dtype=np.float32))
    cache_path.with_suffix('.npy.manifest.json').write_text('{corrupt', encoding='utf-8')

    expected = EmbeddingCacheManifest(
        schema_version='embedding-cache-v4',
        model=EmbeddingModel(source=EmbeddingSource.REMOTE, identifier='test-model'),
        row_count=2,
        text_hash='',
        ordered_ids_hash='',
        source_snapshot_id=None,
        source_artifact_sha256=None,
        row_keys=(),
    )
    assert load_embedding_cache(cache_path, expected=expected, row_count=2) is None


def test_embedding_cache_reuses_unchanged_rows_after_catalogue_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    encoded_batches: list[list[str]] = []

    def encode(texts: list[str], *, model_name: str, revision: str | None, local_only: bool) -> np.ndarray:
        del model_name, revision, local_only
        encoded_batches.append(texts)
        return np.asarray([[float(len(text)), float(index)] for index, text in enumerate(texts)], dtype=np.float32)

    monkeypatch.setattr('pipeline.embedding_cache.encode_synopsis_embeddings', encode)
    cache_path = tmp_path / 'snapshot.npy'
    config = FeatureConfig(
        embedding=EmbeddingModel(source=EmbeddingSource.REMOTE, identifier='test-model'),
        source_snapshot_id='snapshot',
    )

    first = prepare_embedding_cache(
        ['alpha', 'beta'],
        [10, 20],
        config=config,
        cache_path=cache_path,
        source_artifact_sha256='first-source',
    )
    second = prepare_embedding_cache(
        ['beta', 'gamma'],
        [20, 30],
        config=config,
        cache_path=cache_path,
        source_artifact_sha256='second-source',
    )

    assert first is not None
    assert second is not None
    assert encoded_batches == [('alpha', 'beta'), ['gamma']]
    np.testing.assert_array_equal(second[0], first[1])
    assert second[1, 0] == 5


def test_corrupt_recommendation_manifest_is_treated_as_a_cache_miss(tmp_path: Path) -> None:
    manifest_path = tmp_path / 'manifest.json'
    manifest_path.write_text('{corrupt', encoding='utf-8')

    assert (
        _load_reusable_manifest(manifest_path, expected_identity='identity', configuration_fingerprint='config') is None
    )
