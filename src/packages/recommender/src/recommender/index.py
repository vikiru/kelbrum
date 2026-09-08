"""Cosine-similarity recommendations over aligned feature blocks."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import cast

import msgspec
import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize

from features.blocks import FeatureBundle
from models.contracts import LegacySimilarityConfig, RecommendationItem, RecommendationResult
from recommender.identity_policy import bounded_same_story_exclusions
from storage.arrays import read_array, read_sparse, write_array, write_sparse
from storage.json_io import read_json, write_json

FeatureMatrix = NDArray[np.float32] | csr_matrix
IntVector = NDArray[np.int64]


def _feature_matrix(bundle: FeatureBundle) -> FeatureMatrix:
    matrix = bundle.matrix()
    if isinstance(matrix, csr_matrix):
        matrix = normalize(matrix, norm='l2', axis=1, copy=False)
        if not np.isfinite(matrix.data).all():
            raise ValueError('feature bundle contains non-finite values')
        return matrix
    matrix = np.asarray(matrix, dtype=np.float32)
    if not np.isfinite(matrix).all():
        raise ValueError('feature bundle contains non-finite values')
    return normalize(matrix, norm='l2', axis=1)


class SimilarityIndex(msgspec.Struct, frozen=True):
    anime_ids: IntVector
    index_by_anime_id: Mapping[int, int]
    vectors: FeatureMatrix
    knn: NearestNeighbors
    semantic_available: NDArray[np.bool_]

    def save(self, directory: Path, *, config_identity: str = '') -> None:
        """Persist reusable numeric state; the lightweight KNN index is rebuilt on load."""
        directory.mkdir(parents=True, exist_ok=True)
        write_array(directory / 'anime-ids.npy', self.anime_ids)
        if isinstance(self.vectors, csr_matrix):
            write_sparse(directory / 'vectors.npz', self.vectors)
        else:
            write_array(directory / 'vectors.npy', self.vectors)
        write_array(directory / 'semantic-available.npy', self.semantic_available)
        identity = sha256(self.anime_ids.tobytes()).hexdigest()
        write_json(
            directory / 'manifest.json',
            {
                'schema_version': 'similarity-index-v1',
                'rows': len(self.anime_ids),
                'id_checksum': identity,
                'vector_shape': self.vectors.shape,
                'config_identity': config_identity,
                'generated_at': datetime.now(UTC).isoformat(),
            },
        )

    @classmethod
    def load(cls, directory: Path, *, config_identity: str = '') -> 'SimilarityIndex':
        manifest = read_json(directory / 'manifest.json', dict[str, object])
        if manifest.get('schema_version') != 'similarity-index-v1':
            raise ValueError(f'unsupported similarity index artifact: {directory}')
        anime_ids = np.asarray(read_array(directory / 'anime-ids.npy'), dtype=np.int64)
        sparse_path = directory / 'vectors.npz'
        vectors: FeatureMatrix
        if sparse_path.is_file():
            vectors = read_sparse(sparse_path).astype(np.float32)
        else:
            vectors = np.asarray(read_array(directory / 'vectors.npy'), dtype=np.float32)
        semantic_available = np.asarray(read_array(directory / 'semantic-available.npy'), dtype=bool)
        if (
            manifest.get('rows') != anime_ids.size
            or manifest.get('id_checksum') != sha256(anime_ids.tobytes()).hexdigest()
            or tuple(cast('tuple[int, ...]', manifest.get('vector_shape', ()))) != vectors.shape
            or manifest.get('config_identity') != config_identity
            or vectors.shape[0] != anime_ids.size
            or semantic_available.shape != (anime_ids.size,)
        ):
            raise ValueError(f'inconsistent similarity index artifact: {directory}')
        knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1).fit(vectors)
        index_by_anime_id = {int(anime_id): index for index, anime_id in enumerate(anime_ids)}
        return cls(anime_ids, index_by_anime_id, vectors, knn, semantic_available)

    @classmethod
    def build(cls, bundle: FeatureBundle) -> 'SimilarityIndex':
        vectors = _feature_matrix(bundle)
        knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)
        knn.fit(vectors)
        semantic_blocks = {'synopsis-embedding', 'synopsis-tfidf'}
        available = np.zeros(bundle.anime_ids.size, dtype=bool)
        for block in bundle.blocks:
            if block.name in semantic_blocks:
                available |= block.availability()
        anime_ids = bundle.anime_ids.copy()
        index_by_anime_id = {int(anime_id): index for index, anime_id in enumerate(anime_ids)}
        return cls(anime_ids, index_by_anime_id, vectors, knn, available)

    def recommend(
        self,
        source_anime_id: int,
        *,
        config: LegacySimilarityConfig,
        fetched_date: str,
        excluded_ids: frozenset[int] = frozenset(),
        same_story_relations: Mapping[int, Sequence[tuple[int, str]]] | None = None,
        same_story_max_depth: int = 2,
    ) -> RecommendationResult:
        source_index = self.index_by_anime_id.get(source_anime_id)
        if source_index is None:
            raise KeyError(f'anime ID not found: {source_anime_id}')
        candidate_mask = np.ones(self.anime_ids.size, dtype=bool)
        if same_story_relations is not None:
            excluded_ids = excluded_ids | bounded_same_story_exclusions(
                source_anime_id, same_story_relations, max_depth=same_story_max_depth
            )
        if excluded_ids:
            excluded_mask = np.isin(self.anime_ids, tuple(excluded_ids))
        else:
            excluded_mask = np.zeros(self.anime_ids.size, dtype=bool)
        if config.backend == 'knn':
            candidate_count = int(candidate_mask.sum())
            query_size = min(self.anime_ids.size, max(config.limit * 4, config.limit + len(excluded_ids) + 1))
            while True:
                distances, indices = self.knn.kneighbors(
                    self.vectors[source_index : source_index + 1], n_neighbors=query_size
                )
                scores = np.full(self.anime_ids.size, -np.inf, dtype=np.float32)
                scores[indices[0]] = 1.0 - distances[0]
                visible = candidate_mask & (self.anime_ids != source_anime_id) & ~excluded_mask
                if config.require_semantic:
                    visible &= self.semantic_available
                visible &= scores >= config.minimum_score
                if int(visible.sum()) >= config.limit or query_size >= candidate_count:
                    break
                query_size = min(candidate_count, query_size * 2)
        else:
            if isinstance(self.vectors, csr_matrix):
                product = self.vectors @ self.vectors.getrow(source_index).transpose()
            else:
                product = self.vectors @ self.vectors[source_index]
            scores = (
                np.asarray(product.toarray()).ravel()
                if isinstance(product, csr_matrix)
                else np.asarray(product).ravel()
            )
        valid = candidate_mask & (self.anime_ids != source_anime_id) & (scores >= config.minimum_score)
        if config.require_semantic:
            valid &= self.semantic_available
        valid &= ~excluded_mask
        candidate_indices = np.flatnonzero(valid)
        order = np.lexsort((self.anime_ids[candidate_indices], -scores[candidate_indices]))
        ranked_indices = candidate_indices[order[: config.limit]]
        items = tuple(
            RecommendationItem(
                int(self.anime_ids[index]),
                float(scores[index]),
                (('cosine', float(scores[index])),),
            )
            for index in ranked_indices
        )
        return RecommendationResult(source_anime_id, items, fetched_date)
