"""Run the offline Kelbrum catalogue pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from config import (
    canonical_dir,
    embedding_cache_dir,
    frontend_data_dir,
    intermediate_dir,
    model_cache_dir,
    results_dir,
    setup_logging,
    tenrai_profile_full_path,
    tenrai_profile_snapshot_path,
    tenrai_r_plus_checkpoint_path,
    tenrai_r_plus_full_path,
    tenrai_r_plus_snapshot_path,
)
from features.config import EmbeddingModel, EmbeddingSource, FeatureConfig
from fetch.client import TenraiClient
from fetch.filters import CatalogueFilters
from pipeline.contracts import CatalogueProfilePaths, PipelineRunRequest
from pipeline.plan import PipelinePlan
from pipeline.run import run_catalogue_pipeline
from recommender.contracts import RecommendationConfig


def main() -> None:
    """Parse pipeline options and execute one configured catalogue run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--profile',
        choices=('r-plus', 'sfw', 'all'),
        default='r-plus',
        help='Pipeline profile to run (default: r-plus).',
    )
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--frontend-output-dir', type=Path)
    parser.add_argument('--recommendation-path', type=Path)
    parser.add_argument('--relationship-graph-path', type=Path)
    parser.add_argument('--with-embeddings', action='store_true')
    parser.add_argument('--overwrite-fetch', action='store_true')
    args = parser.parse_args()

    setup_logging()
    output_dir = args.output_dir or results_dir() / args.profile
    frontend_output_dir = args.frontend_output_dir or frontend_data_dir()
    recommendation_path = args.recommendation_path or intermediate_dir() / f'{output_dir.name}-recommendations'
    profile_paths = _profile_paths(args.profile)
    with TenraiClient() as client:
        run_catalogue_pipeline(
            PipelineRunRequest(
                client=client,
                profile=args.profile,
                profile_paths=profile_paths,
                pipeline_plan=PipelinePlan(
                    feature_config=FeatureConfig(
                        embedding=(
                            EmbeddingModel(
                                source=EmbeddingSource.LOCAL,
                                identifier=str(model_cache_dir() / 'all-MiniLM-L6-v2'),
                            )
                            if args.with_embeddings
                            else None
                        ),
                        include_bm25=True,
                        include_lsa=True,
                        source_snapshot_id=f'tenrai-anime-{args.profile}',
                    )
                ),
                recommendation_config=RecommendationConfig(),
                output_dir=output_dir,
                frontend_output_dir=frontend_output_dir,
                embedding_cache=(embedding_cache_dir() / f'tenrai-anime-{args.profile}.npy')
                if args.with_embeddings
                else None,
                relationship_graph_path=args.relationship_graph_path
                or canonical_dir() / f'tenrai-anime-{args.profile}-relationship-graph.json',
                recommendation_path=recommendation_path,
                overwrite_fetch=args.overwrite_fetch,
                recommendation_batch_size=1_000,
            )
        )


def _profile_paths(profile: str) -> CatalogueProfilePaths:
    """Resolve production defaults at the CLI boundary."""
    if profile == 'r-plus':
        snapshot = tenrai_r_plus_snapshot_path()
        return CatalogueProfilePaths(
            snapshot=snapshot,
            checkpoint=tenrai_r_plus_checkpoint_path(),
            full_artifact=tenrai_r_plus_full_path(),
            filters=CatalogueFilters.r_plus_catalogue(),
        )
    if profile == 'sfw':
        snapshot = tenrai_profile_snapshot_path('sfw')
        return CatalogueProfilePaths(
            snapshot=snapshot,
            checkpoint=snapshot.with_suffix('.checkpoint.json'),
            full_artifact=tenrai_profile_full_path('sfw'),
            filters=CatalogueFilters.sfw_catalogue(),
        )
    if profile == 'all':
        snapshot = tenrai_profile_snapshot_path('all')
        return CatalogueProfilePaths(
            snapshot=snapshot,
            checkpoint=snapshot.with_suffix('.checkpoint.json'),
            full_artifact=tenrai_profile_full_path('all'),
            filters=CatalogueFilters.all_anime(),
        )
    raise ValueError(f'unsupported catalogue profile: {profile}')


if __name__ == '__main__':
    main()
