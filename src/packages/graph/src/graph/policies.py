"""Relationship policy constants."""

from graph.contracts import RelationType

MANUAL_RELATION = RelationType.MANUAL

STRONG_SAME_STORY_RELATIONS = frozenset(
    {
        RelationType.ALTERNATIVE_VERSION,
        RelationType.FULL_STORY,
        RelationType.PREQUEL,
        RelationType.SEQUEL,
        RelationType.SIDE_STORY,
        RelationType.SUMMARY,
        RelationType.PARENT_STORY,
    }
)

# Character appearances and 'Other' can bridge independent franchises via crossovers.
FRANCHISE_RELATIONS = frozenset(RelationType) - {
    RelationType.CHARACTER,
    RelationType.OTHER,
}
