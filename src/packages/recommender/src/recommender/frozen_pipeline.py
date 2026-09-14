"""Frozen production recommendation ordering over independent path evidence."""

from collections.abc import Callable, Mapping, Sequence

import msgspec
import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

from anime_catalogue import AnimeCatalogue
from features.blocks import FeatureBundle
from features.categorical import CategoricalFeatureStore
from features.synopsis import LatentConfig, TfidfConfig
from features.tag_assignment import MANUAL_TAG_ASSIGNMENTS
from features.tags import apply_tag_assignments
from models.contracts import RawRecommendation, RecommendationItem
from processing.ratings import RatingPolicy
from recommender.paths import AffinityPathIndex, CategoricalPathIndex, build_synopsis_path_index
from recommender.relationship_graph import RelationshipIndex
from recommender.surfacing import SurfacingPolicy
from recommender.union import (
    CATEGORICAL_EVIDENCE_PATHS,
    DEFAULT_RETRIEVAL_FAMILY_BUDGET,
    PATH_FAMILIES,
    RETRIEVAL_PATH_ORDER,
    RETRIEVAL_REDUCER_VERSION,
    SEMANTIC_EVIDENCE_PATHS,
    RetrievalDiagnostics,
    RetrievalFamilyBudget,
    RetrievalMode,
    UnionCandidate,
    build_union,
    reduce_path_results,
)
from recommender.weighted_v2 import WeightedV2Index

RECOMMENDER_POLICY_VERSION = 'normalized-v6-continuous-similarity-surfacing'
SYNOPSIS_WEIGHT = 0.42
TAG_WEIGHT = 0.24
THEME_WEIGHT = 0.18
GENRE_WEIGHT = 0.10
DEMOGRAPHIC_WEIGHT = 0.06
DEMOGRAPHIC_COMPATIBILITY = {
    'shoujo': {'shoujo': 1.0, 'josei': 0.7},
    'josei': {'josei': 1.0, 'shoujo': 0.7},
    'shounen': {'shounen': 1.0, 'seinen': 0.7},
    'seinen': {'seinen': 1.0, 'shounen': 0.7},
}


def _embedding_matrix(bundle: FeatureBundle) -> NDArray[np.floating] | None:
    """Return the aligned embedding block when preparation generated one."""
    block = bundle.block('synopsis-embedding')
    return None if block is None else np.asarray(block.values, dtype=np.float32)


class Recommender:
    """Production recommender with shared retrieval indexes and frozen v2 scoring."""

    def __init__(
        self,
        frame: pl.DataFrame,
        bundle: FeatureBundle,
        rating_policy: RatingPolicy | None = None,
        relationship_index: RelationshipIndex | None = None,
        include_bm25: bool = True,
        include_lsa: bool = True,
        include_embedding: bool = True,
        synopsis_embedding_matrix: NDArray[np.floating] | None = None,
        include_tags: bool = True,
        retrieval_limit: int = 300,
        synopsis_tfidf_config: TfidfConfig | None = None,
        synopsis_latent_config: LatentConfig | None = None,
        surfacing_policy: SurfacingPolicy | None = None,
        retrieval_mode: RetrievalMode = RetrievalMode.FAMILY_REDUCED,
        retrieval_family_budget: RetrievalFamilyBudget = DEFAULT_RETRIEVAL_FAMILY_BUDGET,
    ) -> None:
        self._catalogue = AnimeCatalogue.from_frame(frame)
        self._catalogue.validate_aligned_ids(bundle.anime_ids.tolist(), source_name='feature bundle')
        self._anime_ids = self._catalogue.anime_ids
        self._index_by_id = self._catalogue.index_by_id
        self._titles = dict(zip(self._anime_ids, self._catalogue.titles, strict=True))
        self._genres = self._catalogue.genres
        self._themes = self._catalogue.themes
        self._demographics = self._catalogue.demographics
        tag_map = apply_tag_assignments(self._anime_ids, MANUAL_TAG_ASSIGNMENTS) if include_tags else {}
        categorical = CategoricalFeatureStore.from_catalogue(self._catalogue, tag_map)
        self._tags = categorical.tags
        self._ratings = self._catalogue.ratings
        self._rating_policy = rating_policy or RatingPolicy()
        self._eligible_ids_by_rating = {
            parent_rating: frozenset(
                anime_id
                for anime_id, candidate_rating in zip(self._anime_ids, self._ratings, strict=True)
                if self._rating_policy.evaluate(parent_rating, candidate_rating).allowed
            )
            for parent_rating in set(self._ratings)
        }
        self._relationship_index = relationship_index
        self._include_tags = include_tags
        if retrieval_limit < 1:
            raise ValueError('retrieval_limit must be positive')
        self._retrieval_limit = retrieval_limit
        self._retrieval_mode = retrieval_mode
        self._retrieval_family_budget = retrieval_family_budget
        self._last_retrieval_diagnostics = RetrievalDiagnostics(0, 0, 0, {})
        self._surfacing_policy = surfacing_policy or SurfacingPolicy()
        self._weighted_v2 = WeightedV2Index(bundle)
        synopsis = build_synopsis_path_index(self._anime_ids, self._catalogue.synopsis_features)
        if include_bm25:
            bm25_block = bundle.block('synopsis-bm25')
            if bm25_block is not None and isinstance(bm25_block.values, csr_matrix):
                synopsis.fit_bm25_matrix(bm25_block.values)
            else:
                synopsis.fit_bm25()
        if include_lsa:
            lsa_block = bundle.block('synopsis-lsa')
            if lsa_block is not None and not isinstance(lsa_block.values, csr_matrix):
                synopsis.fit_lsa_matrix(lsa_block.values)
            else:
                synopsis.fit_lsa(synopsis_tfidf_config, synopsis_latent_config)
        if synopsis_embedding_matrix is None and include_embedding:
            synopsis_embedding_matrix = _embedding_matrix(bundle)
        if synopsis_embedding_matrix is not None:
            synopsis.fit_embedding_matrix(np.asarray(synopsis_embedding_matrix, dtype=np.float32))
        self._enabled_synopsis_paths = tuple(
            name
            for name, enabled in (
                ('bm25', include_bm25),
                ('lsa', include_lsa),
                ('embedding', synopsis_embedding_matrix is not None),
            )
            if enabled
        )
        self._synopsis = synopsis
        categorical_maps = categorical.mappings()
        self._genres_by_id = {key: frozenset(val) for key, val in categorical_maps['genres'].items()}
        self._themes_by_id = {key: frozenset(val) for key, val in categorical_maps['themes'].items()}
        self._demographics_by_id = {key: frozenset(val) for key, val in categorical_maps['demographics'].items()}
        self._tags_by_id = {key: frozenset(val) for key, val in categorical_maps['tags'].items()}
        self._categorical_indexes = {
            'genres': CategoricalPathIndex(self._anime_ids, self._genres),
            'themes': CategoricalPathIndex(self._anime_ids, self._themes),
            'tags': CategoricalPathIndex(self._anime_ids, self._tags),
        }
        studio_values = tuple(
            tuple(str(studio_id) for studio_id in values) for values in frame.sort('mal_id')['studio_ids'].to_list()
        )
        self._affinity_indexes = {
            'demographic': AffinityPathIndex(self._anime_ids, self._demographics, DEMOGRAPHIC_COMPATIBILITY),
            'studio': AffinityPathIndex(self._anime_ids, studio_values),
        }

    @property
    def relationship_fingerprint(self) -> str:
        """Return the structural graph identity used by this recommender."""
        if self._relationship_index is None:
            return 'none'
        return self._relationship_index.fingerprint()

    @property
    def retrieval_identity(self) -> str:
        """Return a deterministic identity for retrieval and family reduction."""
        budget = self._retrieval_family_budget
        return msgspec.json.encode(
            {
                'version': RETRIEVAL_REDUCER_VERSION,
                'mode': self._retrieval_mode.value,
                'budgets': {
                    'semantic': budget.semantic,
                    'structured': budget.structured,
                    'neighbourhood': budget.neighbourhood,
                    'affinity': budget.affinity,
                },
                'enabled_paths': self._enabled_synopsis_paths,
                'path_order': RETRIEVAL_PATH_ORDER,
                'path_families': PATH_FAMILIES,
            }
        ).decode('utf-8')

    @property
    def last_retrieval_diagnostics(self) -> RetrievalDiagnostics:
        """Return aggregate counts from the most recent raw recommendation batch."""
        return self._last_retrieval_diagnostics

    def recommend(
        self,
        source_anime_id: int,
        *,
        limit: int,
    ) -> tuple[RecommendationItem, ...]:
        raw_items = self.raw_recommend_many((source_anime_id,))[source_anime_id]
        return self._present_raw_items(raw_items, limit=limit)

    def recommend_many(
        self,
        source_anime_ids: Sequence[int],
        *,
        limit: int,
    ) -> Mapping[int, tuple[RecommendationItem, ...]]:
        """Return independent per-source results while retaining shared indexes."""
        raw_results = self.raw_recommend_many(source_anime_ids)
        return {
            source_id: self._present_raw_items(raw_results[source_id], limit=limit) for source_id in source_anime_ids
        }

    def recommend_ids_many(
        self,
        source_anime_ids: Sequence[int],
        *,
        limit: int,
    ) -> Mapping[int, tuple[int, ...]]:
        """Return production recommendation IDs without materializing debug details."""
        raw_results = self.raw_recommend_many(source_anime_ids)
        return {
            source_id: tuple(item.anime_id for item in self._surfacing_policy.surface(raw_results[source_id])[:limit])
            for source_id in source_anime_ids
        }

    def _present_raw_items(
        self,
        raw_items: Sequence[RawRecommendation],
        *,
        limit: int,
    ) -> tuple[RecommendationItem, ...]:
        surfaced_items = self._surfacing_policy.surface(raw_items)[:limit]
        return tuple(_recommendation_item(item) for item in surfaced_items)

    def raw_similarity_many(
        self,
        source_anime_ids: Sequence[int],
    ) -> Mapping[int, tuple[tuple[int, int, float, tuple[str, ...]], ...]]:
        """Return pre-qualification canonical similarity rows for experiments."""
        source_indices = tuple(self._index_by_id[source_anime_id] for source_anime_id in source_anime_ids)
        streamed = {
            name: self._synopsis.rank_many_streaming(name, source_indices, limit=self._retrieval_limit)
            for name in self._enabled_synopsis_paths
        }
        weighted = self._weighted_v2.rank_many_streaming(source_indices, limit=self._retrieval_limit)
        categorical = {
            name: index.rank_many(source_indices, limit=self._retrieval_limit)
            for name, index in self._categorical_indexes.items()
        }
        affinity = {
            name: index.rank_many(source_indices, limit=self._retrieval_limit)
            for name, index in self._affinity_indexes.items()
        }
        results: dict[int, tuple[tuple[int, int, float, tuple[str, ...]], ...]] = {}
        unbounded_count = 0
        reduced_count = 0
        family_counts = {'semantic': 0, 'structured': 0, 'neighbourhood': 0, 'affinity': 0}
        for row_number, source_anime_id in enumerate(source_anime_ids):
            path_results = [
                ('weighted-v2', weighted[row_number]),
                ('genres', categorical['genres'][row_number]),
                ('themes', categorical['themes'][row_number]),
                ('tags', categorical['tags'][row_number]),
            ]
            path_results.extend((name, streamed[name][row_number]) for name in self._enabled_synopsis_paths)
            path_results.extend((name, affinity[name][row_number]) for name in self._affinity_indexes)
            unbounded_count += sum(len(values) for _, values in path_results)
            path_results = reduce_path_results(
                path_results,
                mode=self._retrieval_mode,
                budgets=self._retrieval_family_budget,
            )
            reduced_count += len({candidate_id for _, values in path_results for candidate_id, _ in values})
            for path, values in path_results:
                family = PATH_FAMILIES[path]
                family_counts[family] += len({candidate_id for candidate_id, _ in values})
            results[source_anime_id] = raw_score_frozen_union(
                source_anime_id,
                build_union(path_results),
                genres_by_id=self._genres_by_id,
                themes_by_id=self._themes_by_id,
                demographics_by_id=self._demographics_by_id,
                tags_by_id=self._tags_by_id,
                relationship_index=self._relationship_index,
                is_eligible=self._eligible_ids_by_rating.get(
                    self._ratings[self._index_by_id[source_anime_id]], frozenset()
                ).__contains__,
            )
        self._last_retrieval_diagnostics = RetrievalDiagnostics(
            len(source_anime_ids), unbounded_count, reduced_count, family_counts
        )
        return results

    def raw_recommend_many(
        self,
        source_anime_ids: Sequence[int],
    ) -> Mapping[int, tuple[RawRecommendation, ...]]:
        """Return canonical ranked candidates before qualification or display policy."""
        raw_results = self.raw_similarity_many(source_anime_ids)
        return {
            source_id: tuple(
                RawRecommendation(
                    anime_id=candidate_id,
                    winning_alias_id=winning_alias_id,
                    score=score,
                    retrieval_paths=paths,
                    semantic_available=any(path in SEMANTIC_EVIDENCE_PATHS for path in paths),
                    categorical_available=any(path in CATEGORICAL_EVIDENCE_PATHS for path in paths),
                )
                for candidate_id, winning_alias_id, score, paths in candidates
            )
            for source_id, candidates in raw_results.items()
        }

    def search_recommendations(
        self,
        source_anime_id: int,
        query: int | str,
        *,
        limit: int = 10,
    ) -> tuple[RecommendationItem, ...]:
        """Find ranked recommendations for one source by ID or title text."""
        if limit < 1:
            raise ValueError('limit must be positive')
        recommendations = self.recommend(source_anime_id, limit=100)
        if isinstance(query, int):
            return tuple(item for item in recommendations if item.anime_id == query)[:limit]
        normalized_query = query.strip().casefold()
        if not normalized_query:
            raise ValueError('recommendation search query cannot be empty')
        return tuple(
            item for item in recommendations if normalized_query in self._titles.get(item.anime_id, '').casefold()
        )[:limit]


def _recommendation_item(raw: RawRecommendation) -> RecommendationItem:
    """Map surfaced raw evidence to the lightweight frontend result contract."""
    return RecommendationItem(
        anime_id=raw.anime_id,
        score=raw.score,
        contributions=(('normalized_fusion', raw.score),),
    )


def raw_score_frozen_union(
    source_anime_id: int,
    candidates: Sequence[UnionCandidate],
    *,
    genres_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    themes_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    tags_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    demographics_by_id: Mapping[int, Sequence[str] | frozenset[str]],
    relationship_index: RelationshipIndex | None = None,
    is_eligible: Callable[[int], bool] | None = None,
) -> tuple[tuple[int, int, float, tuple[str, ...]], ...]:
    """Score every structurally valid union candidate without qualification."""
    source_genres = frozenset(genres_by_id.get(source_anime_id, ()))
    source_themes = frozenset(themes_by_id.get(source_anime_id, ()))
    source_demographics = frozenset(demographics_by_id.get(source_anime_id, ()))
    source_tags = frozenset(tags_by_id.get(source_anime_id, ()))
    scored: list[tuple[int, int, float, tuple[str, ...]]] = []
    for candidate in candidates:
        candidate_id = candidate.anime_id
        if candidate_id == source_anime_id or (is_eligible is not None and not is_eligible(candidate_id)):
            continue
        canonical_id = relationship_index.canonical_id(candidate_id) if relationship_index else candidate_id
        if relationship_index and canonical_id in relationship_index.excluded_ids(source_anime_id):
            continue
        synopsis_score = max(
            (item.score for item in candidate.evidence if item.path in SEMANTIC_EVIDENCE_PATHS),
            default=0.0,
        )
        cand_tags = tags_by_id.get(candidate_id, ())
        cand_tags_set = cand_tags if isinstance(cand_tags, (frozenset, set)) else frozenset(cand_tags)
        tag_score = _coverage(source_tags, cand_tags_set)
        theme_score = _dice(source_themes, themes_by_id.get(candidate_id, ()))
        genre_score = _coverage(source_genres, genres_by_id.get(candidate_id, ()))
        demographic_score = _dice(source_demographics, demographics_by_id.get(candidate_id, ()))
        score = (
            SYNOPSIS_WEIGHT * synopsis_score
            + TAG_WEIGHT * tag_score
            + THEME_WEIGHT * theme_score
            + GENRE_WEIGHT * genre_score
            + DEMOGRAPHIC_WEIGHT * demographic_score
        )
        scored.append((canonical_id, candidate_id, score, tuple(sorted(item.path for item in candidate.evidence))))
    deduplicated: dict[int, tuple[int, float, set[str]]] = {}
    for candidate_id, alias_id, score, paths in scored:
        current = deduplicated.get(candidate_id)
        if current is None:
            deduplicated[candidate_id] = (alias_id, score, set(paths))
            continue
        best_alias_id, best_score, retained_paths = current
        retained_paths.update(paths)
        if score > best_score:
            best_alias_id, best_score = alias_id, score
        deduplicated[candidate_id] = (best_alias_id, best_score, retained_paths)
    return tuple(
        (candidate_id, alias_id, score, tuple(sorted(paths)))
        for candidate_id, (alias_id, score, paths) in sorted(deduplicated.items(), key=_sort_scored_candidates)
    )


def _sort_scored_candidates(
    item: tuple[int, tuple[int, float, set[str]]],
) -> tuple[float, int]:
    return (-item[1][1], item[0])


def _dice(source: frozenset[str] | set[str], candidate: Sequence[str] | frozenset[str] | set[str] | None) -> float:
    if not candidate:
        return 0.0
    candidate_set = candidate if isinstance(candidate, (frozenset, set)) else frozenset(candidate)
    denominator = len(source) + len(candidate_set)
    return 2.0 * len(source & candidate_set) / denominator if denominator else 0.0


def _coverage(source: frozenset[str] | set[str], candidate: Sequence[str] | frozenset[str] | set[str] | None) -> float:
    """Measure how much of the source metadata the candidate preserves."""
    if not source or not candidate:
        return 0.0
    candidate_set = candidate if isinstance(candidate, (frozenset, set)) else frozenset(candidate)
    return len(source & candidate_set) / len(source)
