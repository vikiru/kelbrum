"""Thin Polars adapters over normalization strategies."""

import polars as pl

from normalization.scalers import MaxAbsScaler, MinMaxScaler, RobustScaler, StandardScaler


def transform_series(
    series: pl.Series,
    scaler: MaxAbsScaler | MinMaxScaler | RobustScaler | StandardScaler,
) -> pl.Series:
    """Fit and transform one numeric Series while preserving its name."""
    values = series.to_numpy()
    transformed = scaler.fit_transform(values)
    return pl.Series(series.name, transformed.ravel())
