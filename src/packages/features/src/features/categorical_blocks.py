"""Build categorical and curated tag feature blocks."""

from collections.abc import Iterable
from enum import StrEnum

import msgspec
import numpy as np
import polars as pl

from features.blocks import FeatureBlock
from features.tag_assignment import TAG_ASSIGNMENT_REGISTRY
from features.tags import TagAssignment, apply_tag_assignments
from normalization.encoders import multi_hot, one_hot


class CategoricalEncoding(StrEnum):
    ONE_HOT = 'one-hot'
    MULTI_HOT = 'multi-hot'


class CategoricalProperty(msgspec.Struct, frozen=True):
    """Describe one independently extracted categorical feature property."""

    name: str
    encoding: CategoricalEncoding
    source_column: str | None = None
    manual_tags: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError('categorical property name cannot be empty')
        if self.manual_tags == (self.source_column is not None):
            raise ValueError('categorical property must use either a source column or manual tags')


def default_categorical_properties(*, include_studios: bool) -> tuple[CategoricalProperty, ...]:
    """Return the stable production categorical property order."""
    properties = [
        *(
            CategoricalProperty(column, CategoricalEncoding.ONE_HOT, source_column=column)
            for column in (
                'anime_type',
                'source',
                'rating',
            )
        ),
        *(
            CategoricalProperty(column, CategoricalEncoding.MULTI_HOT, source_column=column)
            for column in (
                'genres',
                'themes',
                'demographics',
            )
        ),
        CategoricalProperty('tags', CategoricalEncoding.MULTI_HOT, manual_tags=True),
    ]
    if include_studios:
        properties.append(CategoricalProperty('studios', CategoricalEncoding.MULTI_HOT, source_column='studios'))
    return tuple(properties)


def build_categorical_blocks(
    frame: pl.DataFrame,
    anime_ids: np.ndarray,
    *,
    include_studios: bool,
    tag_assignments: Iterable[TagAssignment] | None = None,
    properties: Iterable[CategoricalProperty] | None = None,
) -> tuple[FeatureBlock, ...]:
    """Build one-hot, multi-hot, and manually assigned tag blocks."""
    active_properties = (
        tuple(properties) if properties is not None else default_categorical_properties(include_studios=include_studios)
    )
    blocks: list[FeatureBlock] = []
    for property_spec in active_properties:
        if property_spec.encoding is CategoricalEncoding.ONE_HOT:
            raw_values = _scalar_values(frame, property_spec)
            values, names = one_hot(raw_values)
            available = np.asarray(
                [
                    bool(value and value.strip().lower() not in {'unknown', 'n/a', 'not available'})
                    for value in raw_values
                ],
                dtype=bool,
            )
            blocks.append(
                FeatureBlock(
                    property_spec.name,
                    property_spec.encoding.value,
                    values,
                    names,
                    (property_spec.name,),
                    available,
                )
            )
            continue
        if property_spec.manual_tags:
            active_assignments = TAG_ASSIGNMENT_REGISTRY.assignments if tag_assignments is None else tag_assignments
            assigned_tags = apply_tag_assignments(anime_ids, active_assignments)
            raw_values = [assigned_tags.get(int(anime_id), ()) for anime_id in anime_ids]
        else:
            raw_values = _label_values(frame, property_spec)
        values, names = multi_hot(raw_values)
        blocks.append(
            FeatureBlock(property_spec.name, property_spec.encoding.value, values, names, (property_spec.name,))
        )
    return tuple(blocks)


def _scalar_values(frame: pl.DataFrame, property_spec: CategoricalProperty) -> tuple[str | None, ...]:
    if property_spec.source_column is None:
        raise ValueError(f'one-hot property has no source column: {property_spec.name}')
    return tuple(value if isinstance(value, str) else None for value in frame[property_spec.source_column].to_list())


def _label_values(frame: pl.DataFrame, property_spec: CategoricalProperty) -> tuple[tuple[str, ...], ...]:
    if property_spec.source_column is None:
        raise ValueError(f'multi-hot property has no source column: {property_spec.name}')
    return tuple(_label_row(value) for value in frame[property_spec.source_column].to_list())


def _label_row(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise TypeError('categorical multi-hot columns must contain lists or null values')
    return tuple(item for item in value if isinstance(item, str))
