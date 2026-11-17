"""Narrative structure and pacing topologies.

Defines serialized, episodic, procedural, and anthology topologies and their
pairwise compatibility matrix to prevent pacing whiplash (e.g. recommending
disconnected 10-minute avant-garde shorts for a 50-episode serialized epic).
"""

from enum import StrEnum
from typing import Final

from anime_catalogue.tags import Tag


class NarrativeTopology(StrEnum):
    """Pacing and consumption format."""

    SERIALIZED = 'serialized'
    EPISODIC = 'episodic'
    PROCEDURAL = 'procedural'
    ANTHOLOGY = 'anthology'


# Pairwise compatibility multiplier: S(anchor, candidate) in [0.0, 1.0]
TOPOLOGY_COMPATIBILITY_MATRIX: Final[dict[NarrativeTopology, dict[NarrativeTopology, float]]] = {
    NarrativeTopology.SERIALIZED: {
        NarrativeTopology.SERIALIZED: 1.00,
        NarrativeTopology.PROCEDURAL: 0.85,
        NarrativeTopology.EPISODIC: 0.60,
        NarrativeTopology.ANTHOLOGY: 0.25,
    },
    NarrativeTopology.PROCEDURAL: {
        NarrativeTopology.SERIALIZED: 0.88,
        NarrativeTopology.PROCEDURAL: 1.00,
        NarrativeTopology.EPISODIC: 0.85,
        NarrativeTopology.ANTHOLOGY: 0.40,
    },
    NarrativeTopology.EPISODIC: {
        NarrativeTopology.SERIALIZED: 0.65,
        NarrativeTopology.PROCEDURAL: 0.85,
        NarrativeTopology.EPISODIC: 1.00,
        NarrativeTopology.ANTHOLOGY: 0.70,
    },
    NarrativeTopology.ANTHOLOGY: {
        NarrativeTopology.SERIALIZED: 0.30,
        NarrativeTopology.PROCEDURAL: 0.45,
        NarrativeTopology.EPISODIC: 0.70,
        NarrativeTopology.ANTHOLOGY: 1.00,
    },
}


def infer_narrative_topology(tags: frozenset[str] | frozenset[Tag]) -> NarrativeTopology | None:
    """Infer narrative topology from assigned policy tags."""
    if Tag.ANTHOLOGY in tags:
        return NarrativeTopology.ANTHOLOGY
    if Tag.PROCEDURAL in tags:
        return NarrativeTopology.PROCEDURAL
    if Tag.EPISODIC in tags:
        return NarrativeTopology.EPISODIC
    if Tag.SERIALIZED in tags:
        return NarrativeTopology.SERIALIZED
    return None


def compute_topology_scoring_multiplier(
    anchor_topology: NarrativeTopology | None,
    candidate_topology: NarrativeTopology | None,
) -> float:
    """Return structural pacing multiplier in (0.0, 1.0]. Defaults to 1.0 if either is unclassified."""
    if anchor_topology is None or candidate_topology is None:
        return 1.0
    return TOPOLOGY_COMPATIBILITY_MATRIX[anchor_topology][candidate_topology]
