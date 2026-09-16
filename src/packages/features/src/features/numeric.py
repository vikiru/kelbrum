"""Build row-aligned numeric and numeric-bucket feature blocks."""

from collections.abc import Callable

import numpy as np
import polars as pl
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

from features.blocks import FeatureBlock
from features.config import FeatureConfig
from features.encoders import episode_buckets, year_buckets
from normalization.encoders import bucketize
from normalization.policy import MissingPolicy, apply_missing_policy
from normalization.scalers import transform

NumericNormalizer = Callable[[NDArray[np.float64], str, FeatureConfig], NDArray[np.float64]]


def build_numeric_blocks(
    frame: pl.DataFrame,
    *,
    config: FeatureConfig,
    normalizer: NumericNormalizer | None = None,
) -> tuple[FeatureBlock, ...]:
    """Build configured numeric buckets and one normalized numeric block."""
    episode_values = frame['episodes'].to_list()
    year_values = frame['year'].to_list()
    duration_values = frame['duration_minutes'].to_list()
    score_values = frame['score'].to_list()
    blocks = [
        _bucket_block(
            'episodes-bucket',
            episode_buckets(episode_values, boundaries=config.episode_boundaries),
            ('episodes',),
            [value is not None and value >= 1 for value in episode_values],
        ),
        _bucket_block(
            'year-bucket',
            year_buckets(year_values, boundaries=config.year_boundaries),
            ('year',),
            [value is not None and value >= config.year_boundaries[0] for value in year_values],
        ),
        _bucket_block(
            'duration-bucket',
            bucketize(duration_values, boundaries=config.duration_boundaries, missing_below=0),
            ('duration_minutes',),
            [value is not None and value >= 0 for value in duration_values],
        ),
    ]
    numeric_columns = ['year', 'episodes', 'duration_minutes']
    if config.include_quality_features:
        score_bucket = bucketize(score_values, boundaries=config.score_boundaries, missing_below=0)
        blocks.append(
            _bucket_block(
                'score-bucket',
                (score_bucket[0], (*score_bucket[1][:-1], '9-10')),
                ('score',),
                [value is not None and value >= 0 for value in score_values],
            )
        )
        numeric_columns.append('score')
    numeric = frame.select(numeric_columns).to_numpy().astype(np.float64, copy=False)
    available = np.isfinite(numeric)
    active_normalizer = normalizer or normalize_numeric
    normalized = np.column_stack(
        [active_normalizer(numeric[:, index], column, config) for index, column in enumerate(numeric_columns)]
    )
    blocks.append(
        FeatureBlock(
            'numeric',
            'numeric',
            normalized,
            tuple(numeric_columns),
            tuple(numeric_columns),
            row_available=available.any(axis=1),
            dimension_available=available,
        )
    )
    return tuple(blocks)


def normalize_numeric(values: NDArray[np.float64], column: str, config: FeatureConfig) -> NDArray[np.float64]:
    """Apply the configured missing-value policy and fitted transform chain."""
    if config.numeric_missing_policy is MissingPolicy.PRESERVE and np.isnan(values).any():
        observed = ~np.isnan(values)
        if not observed.any():
            return np.full((values.size, 1), np.nan, dtype=np.float64)
        preserved = np.full((values.size, 1), np.nan, dtype=np.float64)
        preserved[observed, 0] = transform(values[observed], config.numeric_transforms.get(column, ())).ravel()
        return preserved
    return transform(
        apply_missing_policy(values, config.numeric_missing_policy),
        config.numeric_transforms.get(column, ()),
    )


def _bucket_block(
    name: str,
    encoded: tuple[csr_matrix, tuple[str, ...]],
    source_properties: tuple[str, ...],
    available: list[bool],
) -> FeatureBlock:
    values, column_names = encoded
    return FeatureBlock(
        name,
        'one-hot',
        values,
        column_names,
        source_properties,
        np.asarray(available, dtype=bool),
    )
