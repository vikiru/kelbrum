"""Recommendation and frontend export stage for a completed pipeline run."""

from collections.abc import Sequence
from pathlib import Path

import msgspec

from config import bind_logger, derive_payload_identity
from export.catalogue import write_catalogue_projections
from export.contracts import FrontendProvenance
from export.frontend import write_featured_artifacts
from fetch.contracts import TenraiAnimeEntry
from graph import RelationshipIndex
from pipeline.build import PipelineRun
from pipeline.recommendation_chunks import DEFAULT_BATCH_SIZE, RecommendationChunkRequest, write_recommendation_chunks
from pipeline.recommendation_export import export_catalogue_stage
from processing.contracts import CanonicalAnime
from recommender.contracts import RecommendationConfig

DEFAULT_RECOMMENDATION_BATCH_SIZE = DEFAULT_BATCH_SIZE
log = bind_logger(package='pipeline', stage='export')


class RecommendationExportRequest(msgspec.Struct, frozen=True):
    """Frontend and recommendation destinations for one export stage."""

    frontend_output_dir: Path
    recommendation_path: Path
    recommendation_config: RecommendationConfig
    provenance: FrontendProvenance
    relationship_index: RelationshipIndex | None = None
    recommendation_batch_size: int = DEFAULT_RECOMMENDATION_BATCH_SIZE
    run_id: str = '-'


def write_recommendation_artifacts(
    run: PipelineRun,
    records: Sequence[CanonicalAnime],
    full_entries: Sequence[TenraiAnimeEntry],
    request: RecommendationExportRequest,
) -> None:
    """Rank the processed catalogue and write frontend-owned artifacts."""
    log.info('Exporting recommendations and frontend artifacts for {} records.', len(records))
    resolved_provenance = msgspec.structs.replace(
        request.provenance,
        catalogue_fingerprint=derive_payload_identity(records),
        relationship_graph_fingerprint=run.recommender.relationship_fingerprint,
    )

    featured_paths = write_featured_artifacts(
        records,
        output_dir=request.frontend_output_dir,
        relationship_index=request.relationship_index,
    )
    projections = write_catalogue_projections(records, output_dir=request.frontend_output_dir)
    write_recommendation_chunks(
        run.recommender,
        records,
        RecommendationChunkRequest(
            output_path=request.recommendation_path,
            recommendation_config=request.recommendation_config,
            source_identity=derive_payload_identity(resolved_provenance),
            batch_size=request.recommendation_batch_size,
            run_id=request.run_id,
        ),
    )
    export_catalogue_stage(
        records,
        full_entries,
        recommendation_path=request.recommendation_path,
        output_dir=request.frontend_output_dir,
        provenance=resolved_provenance,
        featured_paths=featured_paths,
        projections=projections,
    )
    log.info('Exported recommendation chunks, homepage, Top 100, and catalogue artifacts.')
