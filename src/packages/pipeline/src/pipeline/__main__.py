"""Run the offline Kelbrum catalogue pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from config import model_cache_dir, results_dir, setup_logging
from features.config import FeatureConfig
from models.contracts import RecommendationConfig
from pipeline.run import run_catalogue_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('default', 'sfw', 'r-plus', 'all'), default='default')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--overwrite-fetch', action='store_true')
    args = parser.parse_args()

    setup_logging()
    output_dir = args.output_dir or results_dir() / args.profile
    run_catalogue_pipeline(
        profile=args.profile,
        feature_config=FeatureConfig(
            embedding_model='all-MiniLM-L6-v2',
            embedding_model_path=str(model_cache_dir() / 'all-MiniLM-L6-v2'),
            include_bm25=True,
            include_lsa=True,
            source_snapshot_id=f'tenrai-anime-{args.profile}',
        ),
        recommendation_config=RecommendationConfig(),
        output_dir=output_dir,
        overwrite_fetch=args.overwrite_fetch,
        recommendation_batch_size=50,
    )


if __name__ == '__main__':
    main()
