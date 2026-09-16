"""The versioned curation resource consumed by pipeline stages."""

from collections.abc import Mapping, Sequence

import msgspec

from config import derive_payload_identity
from features.tag_assignment import TAG_ASSIGNMENT_REGISTRY
from features.tags import TagAssignment
from graph.registry import MANUAL_RELATIONSHIPS, manual_relationships_identity
from processing.theme_corrections import MANUAL_THEME_ADDITIONS, ThemeCorrection, theme_correction_registry_identity


class CurationSnapshot(msgspec.Struct, frozen=True):
    """Materialized curation facts and one identity for cache consumers."""

    theme_additions: Mapping[int, tuple[str, ...]]
    tagged_anime_ids: frozenset[int]
    theme_identity: str
    tag_identity: str
    relation_identity: str
    theme_removals: Mapping[int, tuple[str, ...]] = msgspec.field(default_factory=dict)

    @property
    def identity(self) -> str:
        """Return the identity of all curation resources used by the pipeline."""
        return derive_payload_identity(
            {
                'theme_additions': sorted(self.theme_additions.items()),
                'theme_removals': sorted(self.theme_removals.items()),
                'tagged_anime_ids': sorted(self.tagged_anime_ids),
                'theme_identity': self.theme_identity,
                'tag_identity': self.tag_identity,
                'relation_identity': self.relation_identity,
            }
        )


class CurationAudit(msgspec.Struct, frozen=True):
    """Catalogue IDs referenced by curation resources but not present in the build."""

    missing_theme_ids: tuple[int, ...] = ()
    missing_tag_ids: tuple[int, ...] = ()
    missing_relation_ids: tuple[int, ...] = ()

    @property
    def missing_count(self) -> int:
        """Return the number of distinct missing curation references."""
        return len(self.missing_theme_ids) + len(self.missing_tag_ids) + len(self.missing_relation_ids)


def load_curation_snapshot() -> CurationSnapshot:
    """Materialize the checked-in curation resources for pipeline consumers."""
    return CurationSnapshot(
        theme_additions=_theme_additions(MANUAL_THEME_ADDITIONS),
        theme_removals=_theme_removals(MANUAL_THEME_ADDITIONS),
        tagged_anime_ids=_tagged_anime_ids(TAG_ASSIGNMENT_REGISTRY.assignments),
        theme_identity=theme_correction_registry_identity(),
        tag_identity=TAG_ASSIGNMENT_REGISTRY.identity(),
        relation_identity=manual_relationships_identity(MANUAL_RELATIONSHIPS),
    )


def audit_curation(snapshot: CurationSnapshot, known_ids: set[int]) -> CurationAudit:
    """Find curation references that cannot be applied to the active catalogue."""
    relation_ids = {
        relation_id for source_id, targets in MANUAL_RELATIONSHIPS.items() for relation_id in (source_id, *targets)
    }
    return CurationAudit(
        missing_theme_ids=tuple(sorted(set(snapshot.theme_additions) - known_ids)),
        missing_tag_ids=tuple(sorted(snapshot.tagged_anime_ids - known_ids)),
        missing_relation_ids=tuple(sorted(relation_ids - known_ids)),
    )


def _theme_additions(corrections: Sequence[ThemeCorrection]) -> dict[int, tuple[str, ...]]:
    """Flatten theme corrections into one anime-indexed mapping."""
    additions: dict[int, tuple[str, ...]] = {}
    for correction in corrections:
        for anime_id in correction.anime_ids:
            additions[anime_id] = (*additions.get(anime_id, ()), *correction.themes)
    return additions


def _theme_removals(corrections: Sequence[ThemeCorrection]) -> dict[int, tuple[str, ...]]:
    """Flatten curated theme removals into one anime-indexed mapping."""
    removals: dict[int, tuple[str, ...]] = {}
    for correction in corrections:
        for anime_id in correction.anime_ids:
            removals[anime_id] = (*removals.get(anime_id, ()), *correction.remove_themes)
    return removals


def _tagged_anime_ids(assignments: Sequence[TagAssignment]) -> frozenset[int]:
    """Return IDs covered by all curated tag assignments."""
    return frozenset(anime_id for assignment in assignments for anime_id in assignment.anime_ids)
