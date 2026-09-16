"""Thin Polars adapters over normalization strategies."""

import polars as pl

from normalization.scalers import BaseScaler


def transform_series(
    series: pl.Series,
    scaler: BaseScaler,
) -> pl.Series:
    """Fit and transform one numeric Series while preserving its name."""
    values = series.to_numpy()
    transformed = scaler.fit_transform(values)
    return pl.Series(series.name, transformed.ravel())
