"""Kelbrum normalization package."""

from normalization.encoders import bucketize, clean_labels, multi_hot, one_hot
from normalization.metadata import MetadataState, OriginLanguage, collection_state, normalize_demographic, scalar_state
from normalization.policy import MissingPolicy, apply_missing_policy
from normalization.ratings import RatingClass, display_rating, normalize_rating, rating_metadata_state
from normalization.scalers import (
    BaseScaler,
    FittedState,
    MaxAbsScaler,
    MinMaxScaler,
    RobustScaler,
    StandardScaler,
    TransformDefinition,
    TransformName,
    log1p,
    restore,
    transform,
    transform_identity,
)

__all__ = [
    'BaseScaler',
    'FittedState',
    'MaxAbsScaler',
    'MetadataState',
    'MinMaxScaler',
    'MissingPolicy',
    'OriginLanguage',
    'RatingClass',
    'RobustScaler',
    'StandardScaler',
    'TransformDefinition',
    'TransformName',
    'apply_missing_policy',
    'bucketize',
    'clean_labels',
    'collection_state',
    'display_rating',
    'log1p',
    'multi_hot',
    'normalize_demographic',
    'normalize_rating',
    'one_hot',
    'rating_metadata_state',
    'restore',
    'scalar_state',
    'transform',
    'transform_identity',
]
