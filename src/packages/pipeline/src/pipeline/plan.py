"""Declarative pipeline choices and runtime build inputs."""

from collections.abc import Sequence
from pathlib import Path

import msgspec
import polars as pl

from features.composition import FeatureAssemblyPlan
from features.config import FeatureConfig
from graph import ManualRelationshipRow, RelationshipIndex
from recommender.plan import RecommenderPlan


class PipelinePlan(msgspec.Struct, frozen=True):
    """Group feature and recommender choices for one pipeline build."""

    feature_config: FeatureConfig
    feature_assembly_plan: FeatureAssemblyPlan | None = None
    recommender_plan: RecommenderPlan | None = None


class PipelineInputs(msgspec.Struct, frozen=True):
    """Hold prepared catalogue inputs needed by the in-memory build."""

    frame: pl.DataFrame
    fetched_date: str
    embedding_cache: Path | None = None
    embedding_model_path: Path | None = None
    relationship_index: RelationshipIndex | None = None
    manual_relationships: Sequence[ManualRelationshipRow] = ()
    source_artifact_sha256: str | None = None
    run_id: str = '-'
