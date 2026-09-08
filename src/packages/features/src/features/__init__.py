"""Kelbrum features package."""

from features.categorical import CategoricalFeatureStore
from features.manual_theme_corrections import MANUAL_THEME_ADDITIONS
from features.tag_assignment import MANUAL_TAG_ASSIGNMENTS
from features.tags import TAGS, Tag, TagAssignment, apply_tag_assignments, validate_tags_against_taxonomy

__all__ = [
    'MANUAL_TAG_ASSIGNMENTS',
    'MANUAL_THEME_ADDITIONS',
    'TAGS',
    'CategoricalFeatureStore',
    'Tag',
    'TagAssignment',
    'apply_tag_assignments',
    'validate_tags_against_taxonomy',
]
