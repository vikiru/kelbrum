"""Kelbrum features package."""

from features.blocks import AvailabilityPolicy
from features.categorical_blocks import CategoricalEncoding, CategoricalProperty, default_categorical_properties
from features.composition import FeatureAssemblyPlan, FeatureStage, FeatureStageObserver, default_feature_stages
from features.config import EmbeddingModel, EmbeddingSource, FeatureConfig
from features.tag_assignment import (
    MANUAL_TAG_ASSIGNMENTS,
    TAG_ASSIGNMENT_REGISTRY,
    TagAssignmentRegistry,
    tag_assignment_registry_identity,
)
from features.tags import (
    TAG_REGISTRY,
    TAGS,
    Tag,
    TagAssignment,
    TagRegistry,
    apply_tag_assignments,
    tag_registry_identity,
    validate_tags_against_taxonomy,
)

__all__ = [
    'MANUAL_TAG_ASSIGNMENTS',
    'TAGS',
    'TAG_ASSIGNMENT_REGISTRY',
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
    'TagRegistry',
    'apply_tag_assignments',
    'default_categorical_properties',
    'default_feature_stages',
    'tag_assignment_registry_identity',
    'tag_registry_identity',
    'validate_tags_against_taxonomy',
]
