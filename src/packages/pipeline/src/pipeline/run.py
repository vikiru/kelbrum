"""Top-level catalogue pipeline orchestration."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from uuid import uuid4

import loguru  # noqa: TC002

from config import LogEvent, bind_logger, derive_payload_identity, emit_event, timed_event
from export.contracts import FrontendProvenance
from features.config import FeatureConfig  # noqa: TC001
from fetch.contracts import TenraiAnimeEntry  # noqa: TC001
from graph import RelationshipIndex  # noqa: TC001
from pipeline.build import PipelineRun, SnapshotBuildRequest, build_from_snapshot, build_pipeline, write_manifest
from pipeline.contracts import CatalogueProfilePaths, PipelineRunRequest  # noqa: TC001
from pipeline.export_stage import (
    DEFAULT_RECOMMENDATION_BATCH_SIZE,
    RecommendationExportRequest,
    write_recommendation_artifacts,
)
from pipeline.input_stages import load_or_enrich, load_or_fetch
from pipeline.processing_stage import _processed_cache_matches, audit_count
from processing.contracts import CanonicalAnime  # noqa: TC001
from recommender.contracts import RecommendationConfig  # noqa: TC001
from storage.hashing import sha256_file
from storage.json_io import read_json


def run_catalogue_pipeline(
    request: PipelineRunRequest,
) -> PipelineRun:
    """Run one explicit catalogue profile through enrichment and artifact generation."""
    execution_id = request.run_id or uuid4().hex
    run_log = bind_logger(package='pipeline', run_id=execution_id)
    run_log.info('Starting pipeline [{}].', request.profile.upper())
    full_entries = _load_pipeline_entries(request)
    run, records, graph = _build_pipeline(request, execution_id)
    accepted_ids = {record.mal_id for record in records}
    output_entries = [entry for entry in full_entries if entry.mal_id in accepted_ids]
    processing_audit = read_json(request.output_dir / 'processing-audit.json', dict[str, object])
    _export_pipeline_artifacts(
        request,
        run,
        records,
        output_entries,
        graph,
        processing_audit,
        execution_id,
        run_log,
    )
    run_log.info('Completed pipeline [{}].', request.profile.upper())
    return run


def _load_pipeline_entries(request: PipelineRunRequest) -> list[TenraiAnimeEntry]:
    """Fetch and enrich the entries required by one pipeline run."""
    entries = load_or_fetch(
        request.client,
        request.profile_paths.snapshot,
        request.profile_paths.checkpoint,
        request.profile_paths.filters,
        request.overwrite_fetch,
    )
    return list(
        load_or_enrich(
            request.client,
            entries,
            request.profile_paths.full_artifact,
            request.overwrite_fetch,
            request.profile,
        )
    )


def _build_pipeline(
    request: PipelineRunRequest,
    execution_id: str,
) -> tuple[PipelineRun, tuple[CanonicalAnime, ...], RelationshipIndex | None]:
    """Build canonical, feature, graph, and recommendation artifacts."""
    return build_from_snapshot(
        SnapshotBuildRequest(
            snapshot_path=request.profile_paths.full_artifact,
            parquet_path=request.output_dir / 'canonical.parquet',
            audit_path=request.output_dir / 'processing-audit.json',
            snapshot_id=request.profile_paths.snapshot.stem,
            pipeline_plan=request.pipeline_plan,
            full_artifact=request.profile_paths.full_artifact,
            entrypoint_snapshot=request.profile_paths.snapshot,
            embedding_cache=request.embedding_cache,
            relationship_graph_path=request.relationship_graph_path,
            processing_policy=request.processing_policy,
            run_id=execution_id,
        )
    )


def _export_pipeline_artifacts(
    request: PipelineRunRequest,
    run: PipelineRun,
    records: tuple[CanonicalAnime, ...],
    output_entries: list[TenraiAnimeEntry],
    graph: RelationshipIndex | None,
    processing_audit: dict[str, object],
    execution_id: str,
    run_log: loguru.Logger,
) -> None:
    """Write the manifest and all frontend artifacts for one completed build."""
    with timed_event(
        run_log,
        event_name='stage.completed',
        package='pipeline',
        stage='export',
        run_id=execution_id,
        row_count=len(records),
    ):
        write_manifest(run, str(request.output_dir / 'pipeline-manifest.json'))
        write_recommendation_artifacts(
            run,
            records,
            output_entries,
            RecommendationExportRequest(
                frontend_output_dir=request.frontend_output_dir,
                recommendation_path=request.recommendation_path,
                recommendation_config=request.recommendation_config,
                relationship_index=graph,
                recommendation_batch_size=request.recommendation_batch_size,
                run_id=execution_id,
                provenance=_build_provenance(
                    profile=request.profile,
                    paths=request.profile_paths,
                    records=records,
                    processing_audit=processing_audit,
                    feature_config=request.pipeline_plan.feature_config,
                    recommendation_config=request.recommendation_config,
                    run=run,
                ),
            ),
        )
    emit_event(
        run_log,
        LogEvent(
            event_name='artifacts.completed',
            package='pipeline',
            stage='export',
            run_id=execution_id,
            row_count=len(records),
            artifact_bytes=_directory_size(request.frontend_output_dir),
        ),
    )


def _build_provenance(
    *,
    profile: str,
    paths: CatalogueProfilePaths,
    records: tuple[CanonicalAnime, ...],
    processing_audit: dict[str, object],
    feature_config: FeatureConfig,
    recommendation_config: RecommendationConfig,
    run: PipelineRun,
) -> FrontendProvenance:
    """Build frontend provenance from the exact inputs used by this run."""
    return FrontendProvenance(
        profile=profile,
        source_snapshot=paths.snapshot.name,
        enrichment_snapshot=paths.full_artifact.name,
        snapshot_sha256=sha256_file(paths.snapshot),
        enrichment_sha256=sha256_file(paths.full_artifact),
        processed_count=len(records),
        accepted_count=audit_count(processing_audit, 'accepted_count', len(records)),
        rejected_count=audit_count(processing_audit, 'rejected_count', 0),
        feature_config_identity=derive_payload_identity(feature_config),
        recommendation_config_identity=derive_payload_identity(recommendation_config),
        retrieval_identity=run.recommender.retrieval_identity,
        union_identity=run.recommender.union_identity,
        ranking_identity=run.recommender.ranking_identity,
        recommender_policy_identity=run.recommender.policy_identity,
    )


def _directory_size(path: Path) -> int:
    """Return the aggregate size of generated files beneath a directory."""
    return sum(item.stat().st_size for item in path.rglob('*') if item.is_file())


__all__ = [
    'DEFAULT_RECOMMENDATION_BATCH_SIZE',
    'PipelineRun',
    '_processed_cache_matches',
    'build_from_snapshot',
    'build_pipeline',
    'run_catalogue_pipeline',
    'write_manifest',
    'write_recommendation_artifacts',
]
