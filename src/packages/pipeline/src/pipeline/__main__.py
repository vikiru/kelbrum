"""Run the offline Kelbrum catalogue pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from config import (
    Settings,
    bind_logger,
    canonical_dir,
    embedding_cache_dir,
    frontend_data_dir,
    huggingface_model_path,
    intermediate_dir,
    model_cache_dir,
    results_dir,
    setup_logging,
    tenrai_full_path,
    tenrai_profile_checkpoint_path,
    tenrai_profile_full_path,
    tenrai_profile_snapshot_path,
    tenrai_r_plus_checkpoint_path,
    tenrai_r_plus_full_path,
    tenrai_r_plus_snapshot_path,
)
from features.config import EmbeddingModel, EmbeddingSource, FeatureConfig
from features.constants import DEFAULT_EMBEDDING_MODEL, default_embedding_batch_size, default_embedding_gate
from fetch.client import TenraiClient
from fetch.errors import FetchError
from fetch.filters import CatalogueFilters
from fetch.profiles import CatalogueProfile
from pipeline.contracts import CatalogueProfilePaths, PipelineRunRequest
from pipeline.plan import PipelinePlan
from pipeline.run import run_catalogue_pipeline
from recommender.contracts import RecommendationConfig
from recommender.plan import RecommenderPlan
from storage.errors import StorageError

if TYPE_CHECKING:
    from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for catalogue pipeline runs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--profile',
        choices=('default', 'r-plus', 'sfw', 'all'),
        default='r-plus',
        help='Pipeline profile to run (default: r-plus).',
    )
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--frontend-output-dir', type=Path)
    parser.add_argument('--recommendation-path', type=Path)
    parser.add_argument('--relationship-graph-path', type=Path)
    parser.add_argument(
        '--with-embeddings',
        '--without-embeddings',
        dest='with_embeddings',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Enable the configured synopsis embedding path (default: enabled).',
    )
    parser.add_argument(
        '--embedding-model',
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help=f'Embedding model identifier (HF repo ID or local path, default: {DEFAULT_EMBEDDING_MODEL}).',
    )
    parser.add_argument(
        '--embedding-tau-min',
        type=float,
        default=None,
        help='Lower similarity threshold for soft embedding gate (tau min).',
    )
    parser.add_argument(
        '--embedding-tau-max',
        type=float,
        default=None,
        help='Upper similarity threshold for soft embedding gate (tau max).',
    )
    parser.add_argument(
        '--embedding-batch-size',
        type=int,
        default=None,
        help='Embedding inference batch size (model-specific default when omitted).',
    )
    parser.add_argument('--overwrite-fetch', action='store_true')
    parser.add_argument(
        '--update',
        action='store_true',
        help='Run incremental profile update before executing pipeline stages.',
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse pipeline options and execute one configured catalogue run."""
    args = build_parser().parse_args(argv)

    setup_logging(level=Settings().log_level)
    log = bind_logger(package='pipeline', stage='pipeline')

    try:
        output_dir = args.output_dir or results_dir() / args.profile
        frontend_output_dir = args.frontend_output_dir or frontend_data_dir()
        recommendation_path = args.recommendation_path or intermediate_dir() / f'{output_dir.name}-recommendations'
        profile_paths = _profile_paths(args.profile)
        catalogue_profile = _catalogue_profile(args.profile)

        embedding_model_obj: EmbeddingModel | None = None
        resolved_model_path: Path | None = None
        rec_plan: RecommenderPlan | None = None
        model_id = args.embedding_model or DEFAULT_EMBEDDING_MODEL
        embedding_batch_size = (
            args.embedding_batch_size
            if args.embedding_batch_size is not None
            else default_embedding_batch_size(model_id)
        )
        if args.with_embeddings:
            resolved_model_path = _resolve_local_model_path(model_id)
            embedding_model_obj = EmbeddingModel(
                source=EmbeddingSource.LOCAL if resolved_model_path is not None else EmbeddingSource.REMOTE,
                identifier=model_id,
            )
            cal_low, cal_high = default_embedding_gate(model_id)
            tau_low = args.embedding_tau_min if args.embedding_tau_min is not None else cal_low
            tau_high = args.embedding_tau_max if args.embedding_tau_max is not None else cal_high
            rec_plan = RecommenderPlan(
                embedding_gate_low=tau_low,
                embedding_gate_high=tau_high,
            )

        with TenraiClient(profile=catalogue_profile) as client:
            if args.update:
                result = client.update_catalogue(
                    snapshot_path=profile_paths.snapshot,
                    filters=profile_paths.filters,
                    full_artifact_path=profile_paths.full_artifact,
                )
                log.info(
                    'Incremental update complete: {} new, {} updated, {} rejected, {} failed.',
                    result.new_count,
                    result.updated_count,
                    result.rejected_count,
                    len(result.failed_ids),
                )
                if result.failed_ids:
                    log.log(
                        'ERROR',
                        'Incremental update failed for {} anime IDs: {}.',
                        len(result.failed_ids),
                        result.failed_ids,
                    )
                    return 1
            run_catalogue_pipeline(
                PipelineRunRequest(
                    client=client,
                    profile=args.profile,
                    profile_paths=profile_paths,
                    pipeline_plan=PipelinePlan(
                        feature_config=FeatureConfig(
                            embedding=embedding_model_obj,
                            embedding_batch_size=embedding_batch_size,
                            include_bm25=True,
                            include_lsa=True,
                            source_snapshot_id=f'tenrai-anime-{args.profile}',
                        ),
                        recommender_plan=rec_plan,
                    ),
                    recommendation_config=RecommendationConfig(),
                    output_dir=output_dir,
                    frontend_output_dir=frontend_output_dir,
                    embedding_cache=(embedding_cache_dir() / f'tenrai-anime-{args.profile}.npy')
                    if args.with_embeddings
                    else None,
                    embedding_model_path=resolved_model_path,
                    relationship_graph_path=args.relationship_graph_path
                    or canonical_dir() / f'tenrai-anime-{args.profile}-relationship-graph.json',
                    recommendation_path=recommendation_path,
                    overwrite_fetch=args.overwrite_fetch,
                    recommendation_batch_size=1_000,
                )
            )
    except (FetchError, StorageError, OSError, ValueError) as error:
        log.log('ERROR', 'Pipeline failed: {}', error)
        return 1
    return 0


def _resolve_local_model_path(model_id: str) -> Path | None:
    """Resolve a local embedding model directory without mutating its canonical ID."""
    model_path = Path(model_id)
    if model_path.is_dir():
        return model_path
    structured_path = huggingface_model_path(model_id)
    if structured_path.is_dir():
        return structured_path
    cached_model_path = model_cache_dir() / model_path.name
    if cached_model_path.is_dir():
        return cached_model_path
    return None


def _catalogue_profile(profile: str) -> CatalogueProfile:
    """Resolve the fetch profile matching a pipeline CLI profile."""
    if profile == 'r-plus':
        return CatalogueProfile.r_plus(limit=50)
    if profile == 'sfw':
        return CatalogueProfile.sfw(limit=50)
    if profile in {'default', 'all'}:
        return CatalogueProfile.all_anime(limit=50)
    raise ValueError(f'unsupported catalogue profile: {profile}')


def _profile_paths(profile: str) -> CatalogueProfilePaths:
    """Resolve production defaults at the CLI boundary."""
    if profile == 'r-plus':
        return CatalogueProfilePaths(
            snapshot=tenrai_r_plus_snapshot_path(),
            checkpoint=tenrai_r_plus_checkpoint_path(),
            full_artifact=tenrai_r_plus_full_path(),
            filters=CatalogueFilters.r_plus_catalogue(),
        )
    if profile == 'sfw':
        return CatalogueProfilePaths(
            snapshot=tenrai_profile_snapshot_path('sfw'),
            checkpoint=tenrai_profile_checkpoint_path('sfw'),
            full_artifact=tenrai_profile_full_path('sfw'),
            filters=CatalogueFilters.sfw_catalogue(),
        )
    if profile == 'all':
        return CatalogueProfilePaths(
            snapshot=tenrai_profile_snapshot_path('all'),
            checkpoint=tenrai_profile_checkpoint_path('all'),
            full_artifact=tenrai_profile_full_path('all'),
            filters=CatalogueFilters.all_anime(),
        )
    if profile == 'default':
        return CatalogueProfilePaths(
            snapshot=tenrai_full_path(),
            checkpoint=tenrai_full_path().with_suffix('.checkpoint.json'),
            full_artifact=tenrai_full_path(),
            filters=CatalogueFilters.all_anime(),
        )
    raise ValueError(f'unsupported catalogue profile: {profile}')


if __name__ == '__main__':
    raise SystemExit(main())
