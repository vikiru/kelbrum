"""Kelbrum features package."""

from features.blocks import AvailabilityPolicy
from features.categorical_blocks import CategoricalEncoding, CategoricalProperty, default_categorical_properties
from features.composition import FeatureAssemblyPlan, FeatureStage, FeatureStageObserver, default_feature_stages
from features.config import EmbeddingModel, EmbeddingSource, FeatureConfig
from features.constants import (
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_MODEL_CALIBRATIONS,
    default_embedding_gate,
)
from features.tag_assignment import (
    TagAssignmentRegistry,
    get_manual_tag_assignments,
    get_tag_assignment_registry,
    tag_assignment_registry_identity,
)
from features.tags import (
    TAG_REGISTRY,
    TAGS,
    Tag,
    TagAssignment,
    TagDefinition,
    TagRegistry,
    apply_tag_assignments,
    tag_registry_identity,
    validate_tags_against_taxonomy,
)

__all__ = [
    'DEFAULT_EMBEDDING_MODEL',
    'EMBEDDING_MODEL_CALIBRATIONS',
    'TAGS',
    'TAG_REGISTRY',
    'AvailabilityPolicy',
    'CategoricalEncoding',
    'CategoricalProperty',
    'EmbeddingModel',
    'EmbeddingSource',
    'FeatureAssemblyPlan',
    'FeatureConfig',
    'FeatureStage',
    'FeatureStageObserver',
    'Tag',
    'TagAssignment',
    'TagAssignmentRegistry',
    'TagDefinition',
    'TagRegistry',
    'apply_tag_assignments',
    'default_categorical_properties',
    'default_embedding_gate',
    'default_feature_stages',
    'get_manual_tag_assignments',
    'get_tag_assignment_registry',
    'tag_assignment_registry_identity',
    'tag_registry_identity',
    'validate_tags_against_taxonomy',
]
