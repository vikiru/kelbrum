from recommender.structure_policy import (
    NarrativeStructure,
    NarrativeStructurePolicy,
    resolve_narrative_structure,
)


def test_narrative_structure_resolution_from_tags_and_synopsis() -> None:
    # Resolves from tags
    assert resolve_narrative_structure(frozenset({'Anthology'})) is NarrativeStructure.ANTHOLOGY
    assert resolve_narrative_structure(frozenset({'Episodic'})) is NarrativeStructure.EPISODIC
    assert resolve_narrative_structure(frozenset({'Serialized'})) is NarrativeStructure.SERIALIZED

    # Resolves from synopsis keywords when tags absent
    assert (
        resolve_narrative_structure(frozenset(), synopsis='A short stories collection.') is NarrativeStructure.ANTHOLOGY
    )
    assert (
        resolve_narrative_structure(frozenset(), synopsis='An omnibus of independent tales.')
        is NarrativeStructure.ANTHOLOGY
    )
    assert (
        resolve_narrative_structure(frozenset(), synopsis='Self-contained standalone stories every week.')
        is NarrativeStructure.EPISODIC
    )

    # Unclassified fallback returns UNKNOWN (neither penalized nor boosted)
    assert resolve_narrative_structure(frozenset(), synopsis='A continuous epic journey.') is NarrativeStructure.UNKNOWN


def test_narrative_structure_policy_multipliers() -> None:
    policy = NarrativeStructurePolicy()

    # Anthology to Anthology: strong boost (1.15x)
    assert policy.multiplier(NarrativeStructure.ANTHOLOGY, NarrativeStructure.ANTHOLOGY) == 1.15

    # Anthology to Episodic: soft boost (1.08x)
    assert policy.multiplier(NarrativeStructure.ANTHOLOGY, NarrativeStructure.EPISODIC) == 1.08

    # Anthology to Serialized: slight de-prioritization (0.92x)
    assert policy.multiplier(NarrativeStructure.ANTHOLOGY, NarrativeStructure.SERIALIZED) == 0.92

    # Episodic to Episodic / Anthology: soft boost (1.06x)
    assert policy.multiplier(NarrativeStructure.EPISODIC, NarrativeStructure.EPISODIC) == 1.06
    assert policy.multiplier(NarrativeStructure.EPISODIC, NarrativeStructure.ANTHOLOGY) == 1.06

    # Serialized to Anthology: de-prioritization of vignette shorts for continuous stories (0.90x)
    assert policy.multiplier(NarrativeStructure.SERIALIZED, NarrativeStructure.ANTHOLOGY) == 0.90

    # Serialized to Serialized: neutral (1.0x)
    assert policy.multiplier(NarrativeStructure.SERIALIZED, NarrativeStructure.SERIALIZED) == 1.0

    # Unknown structure: neutral (1.0x) in both directions
    assert policy.multiplier(NarrativeStructure.ANTHOLOGY, NarrativeStructure.UNKNOWN) == 1.0
    assert policy.multiplier(NarrativeStructure.UNKNOWN, NarrativeStructure.ANTHOLOGY) == 1.0
