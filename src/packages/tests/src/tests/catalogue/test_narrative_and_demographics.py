"""Tests for narrative topology and demographic affinity."""

from anime_catalogue.demographics import (
    ContentSeverityLevel,
    compute_demographic_affinity_multiplier,
    get_content_severity_level,
    is_fatal_content_severity_mismatch,
)
from anime_catalogue.narrative_topology import (
    NarrativeTopology,
    compute_topology_scoring_multiplier,
    infer_narrative_topology,
)
from anime_catalogue.tags import Tag


def test_infer_narrative_topology() -> None:
    assert infer_narrative_topology(frozenset({Tag.SERIALIZED})) == NarrativeTopology.SERIALIZED
    assert infer_narrative_topology(frozenset({Tag.ANTHOLOGY})) == NarrativeTopology.ANTHOLOGY
    assert infer_narrative_topology(frozenset({Tag.PROCEDURAL})) == NarrativeTopology.PROCEDURAL
    assert infer_narrative_topology(frozenset({Tag.EPISODIC})) == NarrativeTopology.EPISODIC
    assert infer_narrative_topology(frozenset({'random_tag'})) is None


def test_serialized_vs_anthology_severe_penalty() -> None:
    multiplier = compute_topology_scoring_multiplier(
        NarrativeTopology.SERIALIZED,
        NarrativeTopology.ANTHOLOGY,
    )
    assert multiplier == 0.25


def test_content_severity_mapping() -> None:
    assert get_content_severity_level('G') == ContentSeverityLevel.LEVEL_0_UNIVERSAL
    assert get_content_severity_level('PG-13') == ContentSeverityLevel.LEVEL_2_TEEN
    assert get_content_severity_level('R-17+') == ContentSeverityLevel.LEVEL_3_MATURE


def test_content_severity_fatal_mismatch_rules() -> None:
    # G anchor excludes R candidate
    assert (
        is_fatal_content_severity_mismatch(
            ContentSeverityLevel.LEVEL_0_UNIVERSAL,
            ContentSeverityLevel.LEVEL_3_MATURE,
        )
        is True
    )

    # Dark R anchor excludes G candidate
    assert (
        is_fatal_content_severity_mismatch(
            ContentSeverityLevel.LEVEL_3_MATURE,
            ContentSeverityLevel.LEVEL_0_UNIVERSAL,
            anchor_is_pure_dark=True,
        )
        is True
    )

    # PG-13 anchor does NOT fatally exclude R candidate (e.g. Steins;Gate to Monster)
    assert (
        is_fatal_content_severity_mismatch(
            ContentSeverityLevel.LEVEL_2_TEEN,
            ContentSeverityLevel.LEVEL_3_MATURE,
        )
        is False
    )


def test_demographic_affinity_multiplier() -> None:
    # Shounen to Seinen high crossover
    assert compute_demographic_affinity_multiplier('shounen', 'seinen') == 0.80
    # Seinen to Kids low crossover
    assert compute_demographic_affinity_multiplier('seinen', 'kids') == 0.10
    # Aliases normalize through parse_demographic
    assert compute_demographic_affinity_multiplier('shonen', 'shojo') == 0.40
    # Unknown inputs return explicit neutral affinity
    assert compute_demographic_affinity_multiplier('unknown', 'seinen') == 1.0
    assert compute_demographic_affinity_multiplier('shounen', 'unrecognized') == 1.0
