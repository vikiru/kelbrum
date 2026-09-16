"""Composable feature-stage definitions for aligned feature assembly."""

from collections.abc import Callable, Iterable

import msgspec
import numpy as np
import polars as pl

from features.blocks import FeatureBlock
from features.categorical_blocks import CategoricalProperty, build_categorical_blocks
from features.config import FeatureConfig
from features.numeric import NumericNormalizer, build_numeric_blocks
from features.tags import TagAssignment
from features.text_blocks import build_text_blocks

FeatureStageBuilder = Callable[[pl.DataFrame, np.ndarray, FeatureConfig], tuple[FeatureBlock, ...]]
FeatureStageObserver = Callable[[str, int, int], None]


class FeatureStage(msgspec.Struct, frozen=True):
    """One independently replaceable feature-building stage."""

    name: str
    required_columns: frozenset[str]
    builder: FeatureStageBuilder

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError('feature stage name cannot be empty')

    def build(self, frame: pl.DataFrame, anime_ids: np.ndarray, config: FeatureConfig) -> tuple[FeatureBlock, ...]:
        """Build this stage's row-aligned feature blocks."""
        return self.builder(frame, anime_ids, config)


class FeatureAssemblyPlan(msgspec.Struct, frozen=True):
    """Declare the ordered feature stages used to build one feature bundle."""

    stages: tuple[FeatureStage, ...]

    def __post_init__(self) -> None:
        names = tuple(stage.name for stage in self.stages)
        if len(names) != len(set(names)):
            raise ValueError('feature stage names must be unique')

    @classmethod
    def defaults(
        cls,
        *,
        tag_assignments: Iterable[TagAssignment] | None,
        synopsis_embedding_matrix: np.ndarray | None,
        numeric_normalizer: NumericNormalizer | None = None,
        categorical_properties: Iterable[CategoricalProperty] | None = None,
    ) -> 'FeatureAssemblyPlan':
        """Create the production stage order from optional feature inputs."""
        return cls(
            default_feature_stages(
                tag_assignments=tag_assignments,
                synopsis_embedding_matrix=synopsis_embedding_matrix,
                numeric_normalizer=numeric_normalizer,
                categorical_properties=categorical_properties,
            )
        )


def default_feature_stages(
    *,
    tag_assignments: Iterable[TagAssignment] | None,
    synopsis_embedding_matrix: np.ndarray | None,
    numeric_normalizer: NumericNormalizer | None = None,
    categorical_properties: Iterable[CategoricalProperty] | None = None,
) -> tuple[FeatureStage, ...]:
    """Return the default stages in their stable production order."""
    return (
        FeatureStage(
            'categorical',
            frozenset({'anime_type', 'source', 'rating', 'genres', 'themes', 'demographics'}),
            lambda frame, anime_ids, config: build_categorical_blocks(
                frame,
                anime_ids,
                include_studios=config.include_studios,
                tag_assignments=tag_assignments,
                properties=categorical_properties,
            ),
        ),
        FeatureStage(
            'numeric',
            frozenset({'year', 'episodes', 'duration_minutes', 'score'}),
            lambda frame, _anime_ids, config: build_numeric_blocks(
                frame,
                config=config,
                normalizer=numeric_normalizer,
            ),
        ),
        FeatureStage(
            'text',
            frozenset({'synopsis_features'}),
            lambda frame, anime_ids, config: build_text_blocks(
                frame['synopsis_features'].to_list(),
                anime_ids,
                config=config,
                synopsis_embedding_matrix=synopsis_embedding_matrix,
            ),
        ),
    )
