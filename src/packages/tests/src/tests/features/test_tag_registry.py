import pytest

from features.tag_assignment import (
    TAG_ASSIGNMENT_REGISTRY,
    TagAssignmentRegistry,
    tag_assignment_registry_identity,
)
from features.tags import Tag, TagAssignment, TagRegistry, tag_registry_identity


def test_tag_assignment_registry_has_a_stable_identity() -> None:
    assert TAG_ASSIGNMENT_REGISTRY.identity() == TAG_ASSIGNMENT_REGISTRY.identity()
    assert tag_assignment_registry_identity() == tag_assignment_registry_identity()
    assert tag_assignment_registry_identity.cache_info().hits >= 1


def test_tag_assignment_rejects_invalid_ids() -> None:
    with pytest.raises(ValueError, match='positive'):
        TagAssignment((0,), ('tag',))


def test_tag_assignment_registry_requires_a_version() -> None:
    with pytest.raises(ValueError, match='version'):
        TagAssignmentRegistry('', ())


def test_tag_assignment_registry_rejects_unknown_vocabulary_ids() -> None:
    with pytest.raises(ValueError, match='unknown tag IDs'):
        TagAssignmentRegistry('v1', (TagAssignment((1,), ('not-a-tag',)),))


def test_tag_registry_rejects_duplicate_definitions() -> None:
    with pytest.raises(ValueError, match='unique'):
        TagRegistry('v1', (Tag('duplicate', 'One'), Tag('duplicate', 'Two')))


def test_tag_registry_identity_changes_with_definitions() -> None:
    first = TagRegistry('v1', (Tag('one', 'One'),))
    second = TagRegistry('v1', (Tag('two', 'Two'),))

    assert first.identity() != second.identity()
    assert tag_registry_identity() == tag_registry_identity()
    assert tag_registry_identity.cache_info().hits >= 1
