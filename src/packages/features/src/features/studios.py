from typing import cast

import polars as pl


def studio_quality_profile(frame: pl.DataFrame, *, prior_count: int = 10) -> pl.DataFrame:
    """Return shrinkage-adjusted studio quality statistics from scored anime."""
    if prior_count < 1:
        raise ValueError('prior_count must be positive')
    required = {'studio_ids', 'score'}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f'studio quality requires columns: {", ".join(missing)}')
    scored = frame.select('studio_ids', 'score').explode('studio_ids').drop_nulls(subset=['studio_ids', 'score'])
    if scored.is_empty():
        return pl.DataFrame(
            schema={
                'studio_id': pl.Int64,
                'anime_count': pl.Int64,
                'mean_score': pl.Float64,
                'adjusted_score': pl.Float64,
                'score_std': pl.Float64,
                'high_score_rate': pl.Float64,
            }
        )
    global_mean_value = scored['score'].mean()
    if global_mean_value is None:
        raise ValueError('studio quality requires at least one scored anime')
    global_mean = cast('float', global_mean_value)
    return (
        scored.group_by('studio_ids')
        .agg(
            pl.len().alias('anime_count'),
            pl.col('score').mean().alias('mean_score'),
            pl.col('score').std(ddof=0).fill_null(0.0).alias('score_std'),
            (pl.col('score') >= 8.0).mean().alias('high_score_rate'),
        )
        .with_columns(
            (
                (pl.col('anime_count') * pl.col('mean_score') + prior_count * global_mean)
                / (pl.col('anime_count') + prior_count)
            ).alias('adjusted_score')
        )
        .rename({'studio_ids': 'studio_id'})
        .select('studio_id', 'anime_count', 'mean_score', 'adjusted_score', 'score_std', 'high_score_rate')
        .sort('adjusted_score', descending=True)
    )
