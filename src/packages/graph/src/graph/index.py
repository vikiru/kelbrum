"""Immutable relationship graph index."""

from collections.abc import Mapping, Sequence

import msgspec

from graph.cleanup import cleanup_candidate_ids
from graph.contracts import GraphRelation, RelationMap, RelationshipScope
from graph.diagnostics import graph_fingerprint, render_graph


class RelationshipIndex(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Immutable same-story families, representatives, and retained edges."""

    family_by_id: Mapping[int, frozenset[int]]
    canonical_by_id: Mapping[int, int]
    relations_by_id: RelationMap = msgspec.field(default_factory=dict)
    franchise_by_id: Mapping[int, frozenset[int]] = msgspec.field(default_factory=dict)
    media_type_by_id: Mapping[int, str | None] = msgspec.field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate family and representative alignment at every construction boundary."""
        family_ids = _validate_story_families(self.family_by_id, self.canonical_by_id)
        _validate_franchise_families(self.franchise_by_id, family_ids)
        _validate_media_types(self.media_type_by_id, family_ids)

    def get_relationships(self, anime_id: int) -> tuple[GraphRelation, ...]:
        """Return retained relations for one node."""
        return tuple(self.relations_by_id.get(anime_id, ()))

    def excluded_ids(self, anchor_id: int) -> frozenset[int]:
        """Return the complete same-story family for an anchor."""
        return self.family_for(anchor_id)

    def family_for(self, anime_id: int) -> frozenset[int]:
        """Return the complete same-story family for an anime ID."""
        return self.family_by_id.get(anime_id, frozenset({anime_id}))

    def franchise_for(self, anime_id: int) -> frozenset[int]:
        """Return every indexed entry connected to the anchor's franchise."""
        return self.franchise_by_id.get(anime_id, self.family_for(anime_id))

    def entries_for(
        self,
        anime_id: int,
        *,
        scope: RelationshipScope = RelationshipScope.FRANCHISE,
        media_type: str | None = None,
    ) -> tuple[int, ...]:
        """Return sorted story or franchise entries, optionally filtered by media type."""
        entries = self.family_for(anime_id) if scope is RelationshipScope.STORY else self.franchise_for(anime_id)
        if media_type is None:
            return tuple(sorted(entries))
        expected_type = media_type.casefold()
        return tuple(
            entry_id
            for entry_id in sorted(entries)
            if (self.media_type_by_id.get(entry_id) or '').casefold() == expected_type
        )

    def canonical_id(self, anime_id: int) -> int:
        """Return the representative for an anime family member."""
        return self.canonical_by_id.get(anime_id, anime_id)

    def is_same_story(self, anchor_id: int, candidate_id: int) -> bool:
        """Return whether a candidate belongs to the anchor's canonical family."""
        family = self.family_for(anchor_id)
        return candidate_id in family or self.canonical_id(candidate_id) in family

    def cleanup(self, anchor_id: int, candidate_ids: Sequence[int]) -> tuple[int, ...]:
        """Remove the anchor family and retain one ID per candidate family."""
        return cleanup_candidate_ids(anchor_id, candidate_ids, self.family_by_id, self.canonical_by_id)

    def to_string(self, anime_id: int | None = None) -> str:
        """Render one node or the complete graph for diagnostics."""
        return render_graph(self.canonical_by_id, self.family_by_id, self.relations_by_id, anime_id)

    def fingerprint(self) -> str:
        """Return a stable identity for graph families and retained edges."""
        return graph_fingerprint(
            self.family_by_id,
            self.canonical_by_id,
            self.relations_by_id,
            self.franchise_by_id,
            self.media_type_by_id,
        )


def _validate_story_families(families: Mapping[int, frozenset[int]], canonical_ids: Mapping[int, int]) -> set[int]:
    """Validate same-story families and return their indexed node IDs."""
    family_ids = set(families)
    if set(canonical_ids) != family_ids:
        raise ValueError('relationship families and canonical IDs must cover the same nodes')
    for anime_id, family in families.items():
        if anime_id <= 0 or not family or anime_id not in family:
            raise ValueError(f'invalid relationship family for anime ID: {anime_id}')
        if any(member <= 0 for member in family):
            raise ValueError(f'relationship families require positive anime IDs: {anime_id}')
        if canonical_ids[anime_id] not in family:
            raise ValueError(f'canonical ID is outside its relationship family: {anime_id}')
    return family_ids


def _validate_franchise_families(franchise_by_id: Mapping[int, frozenset[int]], family_ids: set[int]) -> None:
    """Validate optional franchise connectivity for the same indexed nodes."""
    franchise_ids = set(franchise_by_id)
    if franchise_ids and franchise_ids != family_ids:
        raise ValueError('franchise families and canonical IDs must cover the same nodes')
    for anime_id, franchise in franchise_by_id.items():
        if not franchise or anime_id not in franchise:
            raise ValueError(f'invalid franchise family for anime ID: {anime_id}')


def _validate_media_types(media_types: Mapping[int, str | None], family_ids: set[int]) -> None:
    """Validate media-type metadata against the indexed graph nodes."""
    if not set(media_types).issubset(family_ids):
        raise ValueError('media types cannot reference unknown anime IDs')
    if any(value is not None and not isinstance(value, str) for value in media_types.values()):
        raise ValueError('media types must be strings or null')
