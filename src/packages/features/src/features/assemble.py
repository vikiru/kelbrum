"""Assemble deterministic feature blocks from canonical Polars data."""

from collections.abc import Iterable, Sequence

import msgspec
import numpy as np
import polars as pl

from anime_catalogue import order_catalogue_frame
from config import bind_logger, timed_event
from features.blocks import FeatureBlock, FeatureBundle
from features.categorical_blocks import CategoricalProperty
from features.composition import FeatureAssemblyPlan, FeatureStage, FeatureStageObserver
from features.config import FeatureConfig
from features.numeric import NumericNormalizer
from features.tags import TagAssignment

log = bind_logger(package='features', stage='assembly')


class FeatureAssemblyRequest(msgspec.Struct, frozen=True):
    """Inputs and extension points for one aligned feature assembly."""

    config: FeatureConfig
    synopsis_embedding_matrix: np.ndarray | None = None
    tag_assignments: Iterable[TagAssignment] | None = None
    plan: FeatureAssemblyPlan | None = None
    numeric_normalizer: NumericNormalizer | None = None
    stage_observer: FeatureStageObserver | None = None
    categorical_properties: Sequence[CategoricalProperty] | None = None
    run_id: str = '-'


def assemble_features(
    frame: pl.DataFrame,
    request: FeatureAssemblyRequest,
) -> FeatureBundle:
    """Build aligned categorical, set, text, time, and episode blocks."""
    active_plan = request.plan or FeatureAssemblyPlan.defaults(
        tag_assignments=request.tag_assignments,
        synopsis_embedding_matrix=request.synopsis_embedding_matrix,
        numeric_normalizer=request.numeric_normalizer,
        categorical_properties=request.categorical_properties,
    )
    _validate_required_columns(frame, active_plan.stages)
    ordered = order_catalogue_frame(frame)
    log.info('Assembling feature blocks for {} records.', ordered.height)
    anime_ids = ordered['mal_id'].to_numpy().astype(np.int64, copy=False)
    blocks: list[FeatureBlock] = []
    with timed_event(
        log,
        event_name='stage.completed',
        package='features',
        stage='assembly',
        run_id=request.run_id,
        row_count=ordered.height,
    ):
        for stage in active_plan.stages:
            stage_blocks = stage.build(ordered, anime_ids, request.config)
            if request.stage_observer is not None:
                request.stage_observer(stage.name, len(stage_blocks), ordered.height)
            blocks.extend(stage_blocks)
    log.info('Assembled {} feature blocks.', len(blocks))
    return FeatureBundle(anime_ids, tuple(blocks))


def _validate_required_columns(frame: pl.DataFrame, stages: Sequence[FeatureStage]) -> None:
    """Reject incomplete input before any feature stage starts building."""
    required = {'mal_id'} | frozenset(column for stage in stages for column in stage.required_columns)
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f'feature assembly requires columns: {", ".join(missing)}')
