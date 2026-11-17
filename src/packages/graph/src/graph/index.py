"""Immutable recommendation identity and relationship policy index."""

from collections.abc import Mapping, Sequence

import msgspec

from graph.contracts import EdgeAssertion, GraphRelation, IdentityEquivalenceAssertion, RelationMap, RelationshipScope
from graph.diagnostics import graph_fingerprint, render_graph


class RelationshipIndex(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Separate recommendation identity, story line entrypoints, anchor exclusions, and franchise context."""

    recommendation_entity_by_id: Mapping[int, int]
    recommendation_members_by_id: Mapping[int, frozenset[int]]
    exclusions_by_id: Mapping[int, frozenset[int]]
    exclusion_paths_by_pair: Mapping[tuple[int, int], tuple[EdgeAssertion, ...]]
    story_line_entrypoint_by_id: Mapping[int, int] = msgspec.field(default_factory=dict)
    story_line_members_by_id: Mapping[int, frozenset[int]] = msgspec.field(default_factory=dict)
    relations_by_id: RelationMap = msgspec.field(default_factory=dict)
    edge_assertions: tuple[EdgeAssertion, ...] = ()
    identity_assertions: tuple[IdentityEquivalenceAssertion, ...] = ()
    franchise_by_id: Mapping[int, frozenset[int]] = msgspec.field(default_factory=dict)
    media_type_by_id: Mapping[int, str | None] = msgspec.field(default_factory=dict)
    raw_relationship_version: str = 'unknown'
    identity_policy_version: str = 'recommendation-identity-v1'
    same_story_policy_version: str = 'same-story-v1'
    franchise_policy_version: str = 'franchise-v1'

    def __post_init__(self) -> None:
        ids = set(self.recommendation_entity_by_id)
        if ids != set(self.recommendation_members_by_id) or ids != set(self.exclusions_by_id):
            raise ValueError('identity, member, and exclusion indexes must cover the same catalogue IDs')
        if set(self.franchise_by_id) != ids:
            raise ValueError('franchise index must cover every catalogue ID')
        for anime_id in ids:
            entity_id = self.recommendation_entity_by_id[anime_id]
            if entity_id not in self.recommendation_members_by_id[anime_id]:
                raise ValueError(f'recommendation identity is outside its member set: {anime_id}')
            if anime_id not in self.exclusions_by_id[anime_id]:
                raise ValueError(f'same-story exclusions must include the anchor: {anime_id}')

    def recommendation_entity_id(self, anime_id: int) -> int:
        """Resolve reviewed identity equivalence; unknown IDs retain their own identity."""
        return self.recommendation_entity_by_id.get(anime_id, anime_id)

    def recommendation_entity_members(self, anime_id: int) -> frozenset[int]:
        """Return members of the recommendation identity containing ``anime_id``."""
        return self.recommendation_members_by_id.get(anime_id, frozenset({anime_id}))

    def story_line_entrypoint(self, anime_id: int) -> int:
        """Return the directed canonical entrypoint for a continuation story line."""
        return self.story_line_entrypoint_by_id.get(anime_id, anime_id)

    def story_line_id(self, anime_id: int) -> int:
        """Alias for story_line_entrypoint."""
        return self.story_line_entrypoint(anime_id)

    def story_line_members(self, anime_id: int) -> frozenset[int]:
        """Return all members in the continuation story line resolving to the entrypoint of ``anime_id``."""
        entrypoint = self.story_line_entrypoint(anime_id)
        return self.story_line_members_by_id.get(entrypoint, frozenset({anime_id}))

    def same_story_exclusions(self, anchor_id: int) -> frozenset[int]:
        """Return catalogue entries excluded for the anchor by typed policy edges."""
        return self.exclusions_by_id.get(anchor_id, frozenset({anchor_id}))

    def same_story_exclusion_path(self, anchor_id: int, candidate_id: int) -> tuple[EdgeAssertion, ...] | None:
        """Return the deterministic policy-edge witness, or ``None`` if not excluded."""
        if candidate_id == anchor_id:
            return ()
        return self.exclusion_paths_by_pair.get((anchor_id, candidate_id))

    def franchise_members(self, anime_id: int) -> frozenset[int]:
        """Return catalogue entries connected in the context-only franchise graph."""
        return self.franchise_by_id.get(anime_id, frozenset({anime_id}))

    def get_relationships(self, anime_id: int) -> tuple[GraphRelation, ...]:
        """Return retained source relationship records for one ID."""
        return tuple(self.relations_by_id.get(anime_id, ()))

    def entries_for(
        self,
        anime_id: int,
        *,
        scope: RelationshipScope = RelationshipScope.FRANCHISE,
        media_type: str | None = None,
    ) -> tuple[int, ...]:
        """Return sorted context or exclusion entries, optionally filtered by media type."""
        entries = (
            self.same_story_exclusions(anime_id)
            if scope is RelationshipScope.STORY
            else self.franchise_members(anime_id)
        )
        if media_type is None:
            return tuple(sorted(entries))
        expected_type = media_type.casefold()
        return tuple(
            entry_id
            for entry_id in sorted(entries)
            if (self.media_type_by_id.get(entry_id) or '').casefold() == expected_type
        )

    def fingerprint(self) -> str:
        """Return identity over raw data and all independent policy products."""
        return graph_fingerprint(
            self.recommendation_entity_by_id,
            self.recommendation_members_by_id,
            self.exclusions_by_id,
            self.exclusion_paths_by_pair,
            self.relations_by_id,
            self.franchise_by_id,
            self.media_type_by_id,
            self.edge_assertions,
            self.identity_assertions,
            self.raw_relationship_version,
            self.identity_policy_version,
            self.same_story_policy_version,
            self.franchise_policy_version,
            self.story_line_entrypoint_by_id,
            self.story_line_members_by_id,
        )

    # Deprecated compatibility APIs. They deliberately expose no broad-family identity.
    def canonical_id(self, anime_id: int) -> int:
        """Deprecated alias for recommendation_entity_id."""
        return self.recommendation_entity_id(anime_id)

    def family_for(self, anime_id: int) -> frozenset[int]:
        """Deprecated alias for same_story_exclusions; do not use for identity."""
        return self.same_story_exclusions(anime_id)

    def excluded_ids(self, anchor_id: int) -> frozenset[int]:
        """Deprecated alias for same_story_exclusions."""
        return self.same_story_exclusions(anchor_id)

    def franchise_for(self, anime_id: int) -> frozenset[int]:
        """Deprecated alias for franchise_members."""
        return self.franchise_members(anime_id)

    def is_same_story(self, anchor_id: int, candidate_id: int) -> bool:
        """Deprecated alias for anchor-specific same-story exclusion."""
        return candidate_id in self.same_story_exclusions(anchor_id)

    def cleanup(self, anchor_id: int, candidate_ids: Sequence[int]) -> tuple[int, ...]:
        """Deprecated legacy cleanup using exclusion and identity semantics separately."""
        excluded = self.same_story_exclusions(anchor_id)
        seen: set[int] = set()
        retained: list[int] = []
        for candidate_id in candidate_ids:
            entity_id = self.recommendation_entity_id(candidate_id)
            if candidate_id in excluded or entity_id in seen:
                continue
            seen.add(entity_id)
            retained.append(entity_id)
        return tuple(retained)

    def to_string(self, anime_id: int | None = None) -> str:
        """Render raw relationships and policy-derived identity for diagnostics."""
        return render_graph(
            self.recommendation_entity_by_id,
            self.recommendation_members_by_id,
            self.relations_by_id,
            anime_id,
        )
