"""Frozen production recommendation ordering over independent path evidence."""

from collections.abc import Mapping, Sequence
from types import FunctionType

import msgspec
import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

from anime_catalogue import AnimeCatalogue
from config import derive_payload_identity, derive_stage_identity
from features.blocks import AvailabilityPolicy, FeatureBundle
from features.synopsis import LatentConfig, TfidfConfig
from features.tag_assignment import TAG_ASSIGNMENT_REGISTRY, tag_assignment_registry_identity
from features.tags import apply_tag_assignments, tag_registry_identity
from recommender.contracts import RawRecommendation, RecommendationItem
from recommender.inputs import RecommenderInputs
from recommender.paths import AffinityPathIndex, CategoricalPathIndex, SynopsisPathIndex, build_synopsis_path_index
from recommender.plan import RecommenderPlan
from recommender.properties import SimilarityProperty
from recommender.qualification import canonical_candidate_ids, qualify_candidates
from recommender.rating_policy import RatingPolicy
from recommender.retrieval import RetrievalEngine
from recommender.scoring import (
    ScoringMetric,
    score_candidates,
    to_recommendation_item,
)
from recommender.surfacing import SurfacingPolicy
from recommender.union import (
    CATEGORICAL_EVIDENCE_PATHS,
    SEMANTIC_EVIDENCE_PATHS,
    RetrievalDiagnostics,
    RetrievalFamilyBudget,
    RetrievalMode,
)
from recommender.weighted_v2 import WeightedV2Index

RECOMMENDER_POLICY_DESCRIPTOR = {
    'score_domain': 'finite-non-negative',
    'retrieval': 'deterministic-path-reduction',
    'ranking': 'score-descending-candidate-id-ascending',
}
DEMOGRAPHIC_COMPATIBILITY = {
    'shoujo': {'shoujo': 1.0, 'josei': 0.7},
    'josei': {'josei': 1.0, 'shoujo': 0.7},
    'shounen': {'shounen': 1.0, 'seinen': 0.7},
    'seinen': {'seinen': 1.0, 'shounen': 0.7},
}


class _CatalogueState(msgspec.Struct, frozen=True):
    """Prepared row-aligned catalogue facts consumed by scoring and retrieval."""

    frame: pl.DataFrame
    catalogue: AnimeCatalogue
    anime_ids: tuple[int, ...]
    index_by_id: Mapping[int, int]
    titles: Mapping[int, str]
    genres: tuple[tuple[str, ...], ...]
    themes: tuple[tuple[str, ...], ...]
    demographics: tuple[tuple[str, ...], ...]
    tags: tuple[tuple[str, ...], ...]
    ratings: tuple[str, ...]
    eligible_ids_by_rating: Mapping[str, frozenset[int]]
    genres_by_id: Mapping[int, frozenset[str]]
    themes_by_id: Mapping[int, frozenset[str]]
    demographics_by_id: Mapping[int, frozenset[str]]
    tags_by_id: Mapping[int, frozenset[str]]


class _RetrievalState(msgspec.Struct, frozen=True):
    """Prepared path indexes and resolved path configuration."""

    engine: RetrievalEngine
    similarity_properties: tuple[SimilarityProperty, ...]


def _prepare_catalogue(
    frame: pl.DataFrame,
    bundle: FeatureBundle,
    rating_policy: RatingPolicy,
    include_tags: bool,
) -> _CatalogueState:
    """Validate and prepare all row-aligned catalogue facts."""
    ordered_frame = frame.sort('mal_id')
    catalogue = AnimeCatalogue.from_frame(ordered_frame)
    catalogue.validate_aligned_ids(bundle.anime_ids.tolist(), source_name='feature bundle')
    anime_ids = catalogue.anime_ids
    genres = catalogue.genres
    themes = catalogue.themes
    demographics = catalogue.demographics
    tag_map = apply_tag_assignments(anime_ids, TAG_ASSIGNMENT_REGISTRY.assignments) if include_tags else {}
    tags = tuple(tuple(tag_map.get(anime_id, ())) for anime_id in anime_ids)
    genres_by_id, themes_by_id, demographics_by_id, tags_by_id = _build_feature_maps(
        anime_ids,
        genres,
        themes,
        demographics,
        tags,
    )
    return _CatalogueState(
        frame=ordered_frame,
        catalogue=catalogue,
        anime_ids=anime_ids,
        index_by_id=catalogue.index_by_id,
        titles=dict(zip(anime_ids, catalogue.titles, strict=True)),
        genres=genres,
        themes=themes,
        demographics=demographics,
        tags=tags,
        ratings=catalogue.ratings,
        eligible_ids_by_rating=_build_eligibility_index(anime_ids, catalogue.ratings, rating_policy),
        genres_by_id=genres_by_id,
        themes_by_id=themes_by_id,
        demographics_by_id=demographics_by_id,
        tags_by_id=tags_by_id,
    )


def _embedding_matrix(bundle: FeatureBundle) -> NDArray[np.floating] | None:
    """Return the aligned embedding block when preparation generated one."""
    block = bundle.block('synopsis-embedding')
    return None if block is None else np.asarray(block.values, dtype=np.float32)


def _metric_identity(metric: ScoringMetric) -> str:
    if isinstance(metric, FunctionType):
        return f'{metric.__module__}.{metric.__qualname__}'
    metric_type = type(metric)
    return f'{metric_type.__module__}.{metric_type.__qualname__}'


def _build_eligibility_index(
    anime_ids: Sequence[int],
    ratings: Sequence[str],
    rating_policy: RatingPolicy,
) -> dict[str, frozenset[int]]:
    """Precompute the candidate IDs allowed for each source rating."""
    return {
        parent_rating: frozenset(
            anime_id
            for anime_id, candidate_rating in zip(anime_ids, ratings, strict=True)
            if rating_policy.evaluate(parent_rating, candidate_rating).allowed
        )
        for parent_rating in set(ratings)
    }


def _build_feature_maps(
    anime_ids: Sequence[int],
    genres: Sequence[Sequence[str]],
    themes: Sequence[Sequence[str]],
    demographics: Sequence[Sequence[str]],
    tags: Sequence[Sequence[str]],
) -> tuple[
    dict[int, frozenset[str]],
    dict[int, frozenset[str]],
    dict[int, frozenset[str]],
    dict[int, frozenset[str]],
]:
    """Build ID-keyed feature maps used by the scoring stage."""
    return (
        dict(zip(anime_ids, map(frozenset, genres), strict=True)),
        dict(zip(anime_ids, map(frozenset, themes), strict=True)),
        dict(zip(anime_ids, map(frozenset, demographics), strict=True)),
        dict(zip(anime_ids, map(frozenset, tags), strict=True)),
    )


def _build_synopsis_index(
    anime_ids: Sequence[int],
    synopsis_features: Sequence[str | None],
    bundle: FeatureBundle,
    active_paths: Sequence[str],
    *,
    include_bm25: bool,
    include_lsa: bool,
    include_embedding: bool,
    embedding_matrix: NDArray[np.floating] | None,
    tfidf_config: TfidfConfig | None,
    latent_config: LatentConfig | None,
) -> tuple[SynopsisPathIndex, tuple[str, ...]]:
    """Fit the enabled synopsis indexes and return their active path names."""
    index = build_synopsis_path_index(anime_ids, synopsis_features)
    if include_bm25 and 'bm25' in active_paths:
        block = bundle.block('synopsis-bm25')
        if block is not None and isinstance(block.values, csr_matrix):
            index.fit_bm25_matrix(block.values)
        else:
            index.fit_bm25()
    if include_lsa and 'lsa' in active_paths:
        block = bundle.block('synopsis-lsa')
        if block is not None and not isinstance(block.values, csr_matrix):
            index.fit_lsa_matrix(block.values)
        else:
            index.fit_lsa(tfidf_config, latent_config)
    if embedding_matrix is None and include_embedding and 'embedding' in active_paths:
        embedding_matrix = _embedding_matrix(bundle)
    if embedding_matrix is not None and 'embedding' in active_paths:
        index.fit_embedding_matrix(np.asarray(embedding_matrix, dtype=np.float32))
    enabled_paths = tuple(
        path
        for path, enabled in (
            ('bm25', include_bm25 and 'bm25' in active_paths),
            ('lsa', include_lsa and 'lsa' in active_paths),
            ('embedding', embedding_matrix is not None and 'embedding' in active_paths),
        )
        if enabled
    )
    return index, enabled_paths


def _build_structured_indexes(
    anime_ids: Sequence[int],
    frame: pl.DataFrame,
    genres: Sequence[Sequence[str]],
    themes: Sequence[Sequence[str]],
    demographics: Sequence[Sequence[str]],
    tags: Sequence[Sequence[str]],
    active_paths: Sequence[str],
) -> tuple[dict[str, CategoricalPathIndex], dict[str, AffinityPathIndex]]:
    """Build categorical and affinity indexes for the enabled structured paths."""
    categorical_values = {'genres': genres, 'themes': themes, 'tags': tags}
    categorical = {
        name: CategoricalPathIndex(anime_ids, values)
        for name, values in categorical_values.items()
        if name in active_paths
    }
    studio_values = tuple(tuple(str(studio_id) for studio_id in values) for values in frame['studio_ids'].to_list())
    affinity_values = {
        'demographic': AffinityPathIndex(anime_ids, demographics, DEMOGRAPHIC_COMPATIBILITY),
        'studio': AffinityPathIndex(anime_ids, studio_values),
    }
    affinity = {name: index for name, index in affinity_values.items() if name in active_paths}
    return categorical, affinity


def _build_retrieval_state(
    state: _CatalogueState,
    bundle: FeatureBundle,
    active_paths: Sequence[str],
    *,
    include_bm25: bool,
    include_lsa: bool,
    include_embedding: bool,
    synopsis_embedding_matrix: NDArray[np.floating] | None,
    synopsis_tfidf_config: TfidfConfig | None,
    synopsis_latent_config: LatentConfig | None,
    retrieval_limit: int,
    retrieval_batch_size: int,
    retrieval_mode: RetrievalMode,
    retrieval_family_budget: RetrievalFamilyBudget,
    similarity_properties: Sequence[SimilarityProperty] | None,
    availability_policy: AvailabilityPolicy | None,
) -> _RetrievalState:
    """Build weighted, synopsis, categorical, and affinity retrieval indexes."""
    weighted_v2 = (
        WeightedV2Index(bundle, properties=similarity_properties, availability_policy=availability_policy)
        if 'weighted-v2' in active_paths
        else None
    )
    synopsis, enabled_synopsis_paths = _build_synopsis_index(
        state.anime_ids,
        state.catalogue.synopsis_features,
        bundle,
        active_paths,
        include_bm25=include_bm25,
        include_lsa=include_lsa,
        include_embedding=include_embedding,
        embedding_matrix=synopsis_embedding_matrix,
        tfidf_config=synopsis_tfidf_config,
        latent_config=synopsis_latent_config,
    )
    resolved_paths = tuple(
        path for path in active_paths if path not in {'bm25', 'lsa', 'embedding'} or path in enabled_synopsis_paths
    )
    categorical, affinity = _build_structured_indexes(
        state.anime_ids,
        state.frame,
        state.genres,
        state.themes,
        state.demographics,
        state.tags,
        active_paths,
    )
    return _RetrievalState(
        engine=RetrievalEngine(
            synopsis,
            weighted_v2,
            categorical,
            affinity,
            retrieval_limit=retrieval_limit,
            retrieval_batch_size=retrieval_batch_size,
            mode=retrieval_mode,
            family_budget=retrieval_family_budget,
            enabled_paths=resolved_paths,
        ),
        similarity_properties=() if weighted_v2 is None else weighted_v2.properties,
    )


class Recommender:
    """Production recommender with shared retrieval indexes and frozen v2 scoring."""

    def __init__(
        self,
        inputs: RecommenderInputs,
        plan: RecommenderPlan,
    ) -> None:
        active_retrieval_paths = plan.retrieval_paths
        self._rating_policy = plan.rating_policy
        state = _prepare_catalogue(inputs.frame, inputs.bundle, self._rating_policy, plan.has_path('tags'))
        self._catalogue_state = state
        self._relationship_index = inputs.relationship_index
        self._relationship_policy_identity = plan.relationship_policy_identity
        self._union_policy = plan.union_policy
        self._ranking_policy = plan.ranking_policy
        self._scoring_properties = plan.scoring_properties
        self._scoring_property_values = dict(inputs.scoring_property_values or {})
        self._availability_policy_identity = plan.availability_policy_identity
        self._feature_configuration_identity = inputs.feature_configuration_identity
        self._synopsis_tfidf_config = inputs.synopsis_tfidf_config
        self._synopsis_latent_config = inputs.synopsis_latent_config
        self._surfacing_policy = inputs.surfacing_policy or SurfacingPolicy()
        retrieval_state = _build_retrieval_state(
            state,
            inputs.bundle,
            active_retrieval_paths,
            include_bm25=plan.has_path('bm25'),
            include_lsa=plan.has_path('lsa'),
            include_embedding=plan.has_path('embedding'),
            synopsis_embedding_matrix=inputs.synopsis_embedding_matrix,
            synopsis_tfidf_config=inputs.synopsis_tfidf_config,
            synopsis_latent_config=inputs.synopsis_latent_config,
            retrieval_limit=plan.retrieval_limit,
            retrieval_batch_size=plan.retrieval_batch_size,
            retrieval_mode=plan.retrieval_mode,
            retrieval_family_budget=plan.retrieval_family_budget,
            similarity_properties=plan.similarity_properties,
            availability_policy=plan.availability_policy,
        )
        self._similarity_properties = retrieval_state.similarity_properties
        self._retrieval = retrieval_state.engine

    @property
    def relationship_fingerprint(self) -> str:
        """Return the structural graph identity used by this recommender."""
        if self._relationship_index is None:
            return 'none'
        return self._relationship_index.fingerprint()

    @property
    def retrieval_identity(self) -> str:
        """Return a deterministic identity for retrieval and family reduction."""
        return self._retrieval.identity

    @property
    def union_identity(self) -> str:
        """Return the active candidate-merging policy identity."""
        return self._union_policy.identity

    @property
    def ranking_identity(self) -> str:
        """Return the active ordering policy identity."""
        return self._ranking_policy.identity

    @property
    def policy_identity(self) -> str:
        """Return one deterministic identity for all recommendation policy choices."""
        return derive_stage_identity(
            'recommender',
            contract_identity='recommendation-policy-v1',
            source_identity='none',
            configuration_identity=derive_payload_identity(self._policy_configuration()),
            policy_identity=derive_payload_identity(RECOMMENDER_POLICY_DESCRIPTOR),
            producer_identity='recommender.frozen_pipeline',
        )

    def _policy_configuration(self) -> dict[str, object]:
        """Build the semantic configuration payload used by policy identity."""
        return {
            'recommender_policy': RECOMMENDER_POLICY_DESCRIPTOR,
            'relationship_graph': self.relationship_fingerprint,
            'relationship_policy': self._relationship_policy_identity,
            'catalogue': derive_payload_identity(tuple(self._catalogue_state.anime_ids)),
            'feature_configuration': self._feature_configuration_identity,
            'synopsis_configuration': {
                'tfidf': self._synopsis_tfidf_config,
                'latent': self._synopsis_latent_config,
            },
            'rating': self._rating_policy.identity,
            'retrieval': self.retrieval_identity,
            'union': self.union_identity,
            'ranking': self.ranking_identity,
            'surfacing': {
                'name': self._surfacing_policy.name,
                'minimum_score': self._surfacing_policy.minimum_score,
                'maximum_results': self._surfacing_policy.maximum_results,
            },
            'similarity_properties': [
                {
                    'name': property_spec.name,
                    'weight': property_spec.weight,
                    'metric': property_spec.metric,
                    'content': property_spec.contributes_to_content,
                }
                for property_spec in self._similarity_properties
            ],
            'scoring_properties': [
                {
                    'name': property_spec.name,
                    'weight': property_spec.weight,
                    'metric': property_spec.metric_identity or _metric_identity(property_spec.metric),
                }
                for property_spec in self._scoring_properties
            ],
            'availability_policy': self._availability_policy_identity,
            'tag_vocabulary_identity': tag_registry_identity(),
            'tag_assignment_identity': tag_assignment_registry_identity(),
        }

    @property
    def last_retrieval_diagnostics(self) -> RetrievalDiagnostics:
        """Return aggregate counts from the most recent raw recommendation batch."""
        return self._retrieval.last_diagnostics

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
        return tuple(to_recommendation_item(item.anime_id, item.score) for item in surfaced_items)

    def raw_similarity_many(
        self,
        source_anime_ids: Sequence[int],
    ) -> Mapping[int, tuple[tuple[int, int, float, tuple[str, ...]], ...]]:
        """Return pre-qualification canonical similarity rows for experiments."""
        source_indices = tuple(
            self._catalogue_state.index_by_id[source_anime_id] for source_anime_id in source_anime_ids
        )
        retrieval = self._retrieval.retrieve(source_indices)
        results: dict[int, tuple[tuple[int, int, float, tuple[str, ...]], ...]] = {}
        for row_number, source_anime_id in enumerate(source_anime_ids):
            path_results = retrieval.results[row_number]
            qualified = qualify_candidates(
                source_anime_id,
                self._union_policy.merge(path_results),
                relationship_index=self._relationship_index,
                is_eligible=self._catalogue_state.eligible_ids_by_rating.get(
                    self._catalogue_state.ratings[self._catalogue_state.index_by_id[source_anime_id]],
                    frozenset(),
                ).__contains__,
            )
            results[source_anime_id] = score_candidates(
                source_anime_id,
                qualified,
                genres_by_id=self._catalogue_state.genres_by_id,
                themes_by_id=self._catalogue_state.themes_by_id,
                demographics_by_id=self._catalogue_state.demographics_by_id,
                tags_by_id=self._catalogue_state.tags_by_id,
                canonical_ids=canonical_candidate_ids(qualified, self._relationship_index),
                ranking_policy=self._ranking_policy,
                properties=self._scoring_properties,
                property_values=self._scoring_property_values,
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
            item
            for item in recommendations
            if normalized_query in self._catalogue_state.titles.get(item.anime_id, '').casefold()
        )[:limit]
