"""Relationship policy constants."""

from graph.contracts import RelationType

MANUAL_RELATION = RelationType.MANUAL

STRONG_SAME_STORY_RELATIONS = frozenset(
    {
        RelationType.ALTERNATIVE_VERSION,
        RelationType.FULL_STORY,
        RelationType.PREQUEL,
        RelationType.SEQUEL,
        RelationType.SUMMARY,
        RelationType.PARENT_STORY,
    }
)

# Franchise membership is intentionally broader than same-story canonicalization.
# A franchise can connect separate series through spin-offs, adaptations, and other
# source-defined relation types without collapsing those series into one story family.
FRANCHISE_RELATIONS = frozenset(RelationType)
