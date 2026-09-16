"""Build in-memory feature and recommendation stages from canonical data."""

from datetime import UTC, datetime
from pathlib import Path

import msgspec
import polars as pl

from anime_catalogue import order_catalogue_frame
from config import derive_payload_identity
from features.assemble import FeatureAssemblyRequest, assemble_features
from features.blocks import FeatureBundle
from features.config import FeatureConfig
from features.synopsis import LatentConfig, TfidfConfig
from graph import RelationshipIndex
from pipeline.contracts import PipelineManifest
from pipeline.embedding_cache import prepare_embedding_cache
from pipeline.input_stages import validate_entrypoint_pair
from pipeline.plan import PipelineInputs, PipelinePlan
from pipeline.processing_stage import load_or_process_records
from pipeline.relationship_cache import load_or_build_relationship_graph
from processing.build import canonical_frame
from processing.contracts import CanonicalAnime
from processing.eligibility import EligibilityPolicy
from recommender.contracts import RecommendationConfig, RecommendationItem, RecommendationResult
from recommender.frozen_pipeline import Recommender
from recommender.inputs import RecommenderInputs
from recommender.plan import RecommenderPlan
from recommender.union import AVAILABLE_RETRIEVAL_PATHS
from storage.hashing import sha256_file
from storage.json_io import write_json


class SnapshotBuildRequest(msgspec.Struct, frozen=True):
    """Filesystem and policy inputs for one snapshot-backed pipeline build."""

    snapshot_path: Path
    parquet_path: Path
    audit_path: Path
    snapshot_id: str
    pipeline_plan: PipelinePlan
    fetched_date: str | None = None
    full_artifact: Path | None = None
    entrypoint_snapshot: Path | None = None
    embedding_cache: Path | None = None
    relationship_graph_path: Path | None = None
    processing_policy: EligibilityPolicy | None = None
    run_id: str = '-'


class PipelineRun(msgspec.Struct, frozen=True):
    """Completed in-memory feature and recommendation indexes."""

    features: FeatureBundle
    recommender: Recommender
    manifest: PipelineManifest

    def recommend(
        self,
        source_anime_id: int,
        *,
        config: RecommendationConfig,
        fetched_date: str,
    ) -> RecommendationResult:
        return RecommendationResult(
            source_anime_id,
            self.recommender.recommend(source_anime_id, limit=config.limit),
            fetched_date,
        )

    def search_recommendations(
        self, source_anime_id: int, query: int | str, *, limit: int = 10
    ) -> tuple[RecommendationItem, ...]:
        """Search one source's ranked recommendations by ID or title."""
        return self.recommender.search_recommendations(source_anime_id, query, limit=limit)


def build_pipeline(
    inputs: PipelineInputs,
    plan: PipelinePlan,
) -> PipelineRun:
    """Build all in-memory downstream artifacts from one prepared input object."""
    ordered_frame = order_catalogue_frame(inputs.frame)
    ordered_ids = tuple(int(value) for value in ordered_frame.get_column('mal_id').to_list())
    cached_embeddings = prepare_embedding_cache(
        ordered_frame['synopsis_features'].to_list(),
        ordered_ids,
        config=plan.feature_config,
        cache_path=inputs.embedding_cache,
        source_artifact_sha256=inputs.source_artifact_sha256,
    )
    bundle = assemble_features(
        ordered_frame,
        FeatureAssemblyRequest(
            config=plan.feature_config,
            synopsis_embedding_matrix=cached_embeddings,
            plan=plan.feature_assembly_plan,
            run_id=inputs.run_id,
        ),
    )
    synopsis_tfidf_config, synopsis_latent_config = _synopsis_configs(plan.feature_config)
    active_plan = plan.recommender_plan or _default_recommender_plan(plan.feature_config)
    recommender = _build_recommender(
        ordered_frame,
        bundle,
        feature_config=plan.feature_config,
        plan=active_plan,
        relationship_index=inputs.relationship_index,
        synopsis_tfidf_config=synopsis_tfidf_config,
        synopsis_latent_config=synopsis_latent_config,
    )
    manifest = PipelineManifest(
        schema_version='kelbrum-pipeline-v1',
        fetched_date=inputs.fetched_date,
        anime_count=bundle.anime_ids.size,
        feature_block_names=tuple(block.name for block in bundle.blocks),
        status='complete',
    )
    return PipelineRun(bundle, recommender, manifest)


def _default_recommender_plan(feature_config: FeatureConfig) -> RecommenderPlan:
    """Translate feature flags into the default retrieval composition."""
    disabled_paths = {
        path
        for path, enabled in (
            ('bm25', feature_config.include_bm25),
            ('lsa', feature_config.include_lsa),
        )
        if not enabled
    }
    paths = tuple(path for path in AVAILABLE_RETRIEVAL_PATHS if path not in disabled_paths)
    return RecommenderPlan(retrieval_paths=paths)


def _build_recommender(
    frame: pl.DataFrame,
    bundle: FeatureBundle,
    *,
    feature_config: FeatureConfig,
    plan: RecommenderPlan,
    relationship_index: RelationshipIndex | None,
    synopsis_tfidf_config: TfidfConfig,
    synopsis_latent_config: LatentConfig,
) -> Recommender:
    """Build the recommender through the plan seam when one is supplied."""
    feature_identity = derive_payload_identity(feature_config)
    return Recommender(
        RecommenderInputs(
            frame,
            bundle,
            relationship_index=relationship_index,
            synopsis_tfidf_config=synopsis_tfidf_config,
            synopsis_latent_config=synopsis_latent_config,
            feature_configuration_identity=feature_identity,
        ),
        plan,
    )


def build_from_snapshot(
    request: SnapshotBuildRequest,
) -> tuple[PipelineRun, tuple[CanonicalAnime, ...], RelationshipIndex | None]:
    """Process one accepted snapshot and build downstream in-memory indexes."""
    generated_at = request.fetched_date or datetime.now(UTC).isoformat()
    if request.full_artifact is not None:
        validate_entrypoint_pair(request.entrypoint_snapshot or request.snapshot_path, request.full_artifact)
    policy = request.processing_policy or EligibilityPolicy()
    records = load_or_process_records(
        request.snapshot_path,
        request.parquet_path,
        request.audit_path,
        snapshot_id=request.snapshot_id,
        policy=policy,
        run_id=request.run_id,
    )
    relationship_index = _load_relationship_index(
        request.full_artifact,
        request.relationship_graph_path,
        records,
        run_id=request.run_id,
    )
    run = build_pipeline(
        PipelineInputs(
            frame=canonical_frame(records),
            fetched_date=generated_at,
            embedding_cache=request.embedding_cache,
            relationship_index=relationship_index,
            source_artifact_sha256=sha256_file(request.parquet_path),
            run_id=request.run_id,
        ),
        request.pipeline_plan,
    )
    return run, records, relationship_index


def _load_relationship_index(
    full_artifact: Path | None,
    relationship_graph_path: Path | None,
    records: tuple[CanonicalAnime, ...],
    *,
    run_id: str,
) -> RelationshipIndex | None:
    """Load or rebuild relationship evidence when full entries are available."""
    if full_artifact is None:
        return None
    if relationship_graph_path is None:
        raise ValueError('relationship_graph_path is required with full_artifact')
    return load_or_build_relationship_graph(
        full_artifact,
        relationship_graph_path,
        tuple(record.mal_id for record in records),
        {record.mal_id: record.anime_type for record in records},
        run_id=run_id,
    ).index


def write_manifest(run: PipelineRun, path: str) -> None:
    """Write the completed pipeline manifest as minified JSON."""
    write_json(Path(path), run.manifest)


def _synopsis_configs(config: FeatureConfig) -> tuple[TfidfConfig, LatentConfig]:
    """Translate feature settings into synopsis index configuration types."""
    return (
        TfidfConfig(
            ngram_range=config.synopsis_ngram_range,
            sublinear_tf=config.synopsis_sublinear_tf,
            stop_words=config.synopsis_stop_words,
            min_df=config.synopsis_min_df,
            max_df=config.synopsis_max_df,
            max_features=config.synopsis_max_features,
        ),
        LatentConfig(dimensions=config.latent_dimensions, max_iter=config.latent_max_iter),
    )
