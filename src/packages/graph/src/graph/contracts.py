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


class IdentityIntent(StrEnum):
    DISTINCT = 'distinct'
    IDENTITY_EQUIVALENT = 'identity-equivalent'


class SameStoryIntent(StrEnum):
    CONTINUATION = 'continuation'
    SAME_STORY_LINK = 'same-story-link'
    PAIRWISE_EXCLUSION = 'pairwise-exclusion'
    FRANCHISE_ONLY = 'franchise-only'
    NEEDS_REVIEW = 'needs-review'


class TraversalMode(StrEnum):
    TRANSITIVE = 'transitive'
    ENDPOINT_ONLY = 'endpoint-only'
    NONE = 'none'


class EdgeAssertion(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Policy interpretation kept separate from the source relationship record."""

    source_id: int
    target_id: int
    relation_type: RelationType
    provenance: str
    source_record_id: str
    identity_intent: IdentityIntent
    same_story_intent: SameStoryIntent
    traversal_mode: TraversalMode
    rationale: str
    policy_version: str


class IdentityEquivalenceAssertion(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    source_id: int
    target_id: int
    rationale: str
    provenance: str
    policy_version: str = 'recommendation-identity-v1'

    def __post_init__(self) -> None:
        if self.source_id <= 0 or self.target_id <= 0 or self.source_id == self.target_id:
            raise ValueError('identity-equivalent IDs must be distinct positive catalogue IDs')
        if not self.rationale.strip() or not self.provenance.strip():
            raise ValueError('identity equivalences require rationale and provenance')


class ManualEdgePolicy(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Reviewed intent for one manually curated undirected relationship."""

    source_id: int
    target_id: int
    same_story_intent: SameStoryIntent
    rationale: str
    provenance: str
    identity_intent: IdentityIntent = IdentityIntent.DISTINCT
    traversal_mode: TraversalMode | None = None
    relation_type: RelationType = RelationType.MANUAL

    def __post_init__(self) -> None:
        if self.source_id <= 0 or self.target_id <= 0 or self.source_id == self.target_id:
            raise ValueError('manual edge endpoints must be distinct positive IDs')
        if not self.rationale.strip() or not self.provenance.strip():
            raise ValueError('typed manual edges require rationale and provenance')
        if (
            self.identity_intent is IdentityIntent.IDENTITY_EQUIVALENT
            and self.same_story_intent is not SameStoryIntent.FRANCHISE_ONLY
        ):
            raise ValueError('identity-equivalent manual edges must not imply same-story exclusion')


class ManualRelationshipRow(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """One typed record parsed from the supplementary manual relations CSV."""

    source_id: int
    source_title: str
    target_id: int
    target_title: str
    relation_type: str
    same_story_intent: SameStoryIntent
    traversal_mode: TraversalMode
    identity_intent: IdentityIntent
    provenance: str


class GraphNode(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """A catalogue node after source-specific decoding has been completed."""

    anime_id: int
    media_type: str | None = None


class GraphRelation(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """A directed, normalized relation from one node to another."""

    target_id: int
    relation: RelationType


RelationMap = Mapping[int, Sequence[GraphRelation]]
