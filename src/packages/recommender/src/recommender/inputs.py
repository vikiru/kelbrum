"""Runtime data required to construct a prepared recommender."""

from collections.abc import Mapping

import msgspec
import numpy as np
import polars as pl
from numpy.typing import NDArray

from features.blocks import FeatureBundle
from features.synopsis import LatentConfig, TfidfConfig
from graph import RelationshipIndex
from recommender.scoring import PropertyValues
from recommender.surfacing import SurfacingPolicy


class RecommenderInputs(msgspec.Struct, frozen=True):
    """Hold runtime data separately from recommender policy choices."""

    frame: pl.DataFrame
    bundle: FeatureBundle
    relationship_index: RelationshipIndex | None = None
    synopsis_embedding_matrix: NDArray[np.floating] | None = None
    synopsis_tfidf_config: TfidfConfig | None = None
    synopsis_latent_config: LatentConfig | None = None
    surfacing_policy: SurfacingPolicy | None = None
    scoring_property_values: Mapping[str, PropertyValues] | None = None
    feature_configuration_identity: str = '-'
