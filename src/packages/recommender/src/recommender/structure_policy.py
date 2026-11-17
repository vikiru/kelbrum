"""Narrative structure affinity policy for serialized, episodic, and anthology anime."""

from enum import StrEnum
from typing import Final

import msgspec

from features.tags import Tag


class NarrativeStructure(StrEnum):
    ANTHOLOGY = 'ANTHOLOGY'
    EPISODIC = 'EPISODIC'
    SERIALIZED = 'SERIALIZED'
    UNKNOWN = 'UNKNOWN'


class NarrativeProfile(msgspec.Struct, frozen=True):
    """Resolved narrative form for a catalogue entry."""

    structure: NarrativeStructure


class NarrativeStructurePolicy(msgspec.Struct, frozen=True):
    anthology_to_anthology_boost: float = 1.15
    anthology_to_episodic_boost: float = 1.08
    episodic_to_episodic_boost: float = 1.06
    serialized_to_anthology_dampen: float = 0.90
    anthology_to_serialized_dampen: float = 0.92

    def multiplier(
        self,
        source_structure: str | NarrativeStructure | NarrativeProfile | None,
        candidate_structure: str | NarrativeStructure | NarrativeProfile | None,
    ) -> float:
        if isinstance(source_structure, NarrativeProfile):
            source_structure = source_structure.structure
        if isinstance(candidate_structure, NarrativeProfile):
            candidate_structure = candidate_structure.structure
        s_s = str(source_structure or '').strip().upper()
        c_s = str(candidate_structure or '').strip().upper()

        if s_s == NarrativeStructure.ANTHOLOGY:
            if c_s == NarrativeStructure.ANTHOLOGY:
                return self.anthology_to_anthology_boost
            if c_s == NarrativeStructure.EPISODIC:
                return self.anthology_to_episodic_boost
            if c_s == NarrativeStructure.SERIALIZED:
                return self.anthology_to_serialized_dampen

        elif s_s == NarrativeStructure.EPISODIC:
            if c_s in (NarrativeStructure.EPISODIC, NarrativeStructure.ANTHOLOGY):
                return self.episodic_to_episodic_boost

        elif s_s == NarrativeStructure.SERIALIZED and c_s == NarrativeStructure.ANTHOLOGY:
            return self.serialized_to_anthology_dampen

        return 1.0


DEFAULT_NARRATIVE_STRUCTURE_POLICY: Final[NarrativeStructurePolicy] = NarrativeStructurePolicy()


def resolve_narrative_structure(
    tags: frozenset[str] | set[str] | tuple[str, ...],
    synopsis: str | None = None,
) -> NarrativeStructure:
    tag_set = {str(t).strip().casefold() for t in tags}
    if Tag.ANTHOLOGY in tag_set:
        return NarrativeStructure.ANTHOLOGY
    if Tag.EPISODIC in tag_set:
        return NarrativeStructure.EPISODIC
    if Tag.SERIALIZED in tag_set:
        return NarrativeStructure.SERIALIZED

    if synopsis:
        s_lower = synopsis.casefold()
        if any(w in s_lower for w in ('anthology', 'short stories', 'collection of short', 'omnibus', 'vignettes')):
            return NarrativeStructure.ANTHOLOGY
        if any(
            w in s_lower
            for w in ('episodic', 'standalone stories', 'case-of-the-week', 'monster of the week', 'self-contained')
        ):
            return NarrativeStructure.EPISODIC

    return NarrativeStructure.UNKNOWN


def resolve_narrative_profile(
    tags: frozenset[str] | set[str] | tuple[str, ...],
    synopsis: str | None = None,
) -> NarrativeProfile:
    return NarrativeProfile(structure=resolve_narrative_structure(tags, synopsis))
