"""Typed, normalized relationship graph contracts."""

from collections.abc import Mapping, Sequence
from enum import StrEnum

import msgspec


class RelationType(StrEnum):
    """Normalized relation vocabulary accepted by graph policies."""

    ADAPTATION = 'Adaptation'
    ALTERNATIVE_SETTING = 'Alternative Setting'
    ALTERNATIVE_VERSION = 'Alternative Version'
    BASED_ON = 'Based on'
    CHARACTER = 'Character'
    FULL_STORY = 'Full Story'
    MANUAL = 'Artificial/Manual'
    OTHER = 'Other'
    PARENT_STORY = 'Parent Story'
    PREQUEL = 'Prequel'
    SEQUEL = 'Sequel'
    SIDE_STORY = 'Side Story'
    SPIN_OFF = 'Spin-Off'
    SUMMARY = 'Summary'


class RelationshipScope(StrEnum):
    """Relationship scopes exposed to callers querying graph entries."""

    STORY = 'story'
    FRANCHISE = 'franchise'


class GraphNode(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """A catalogue node after source-specific decoding has been completed."""

    anime_id: int
    media_type: str | None = None


class GraphRelation(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """A directed, normalized relation from one node to another."""

    target_id: int
    relation: RelationType


RelationMap = Mapping[int, Sequence[GraphRelation]]
