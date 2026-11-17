"""Narrative form belongs to policy, not shared-content similarity evidence."""

from collections.abc import Mapping

import numpy as np
import polars as pl
import pytest

from features.categorical_blocks import CategoricalEncoding, CategoricalProperty, build_categorical_blocks
from features.tags import Tag, TagAssignment, apply_tag_assignments, get_tag_salience
from recommender.guards import NON_NARRATIVE_TAGS, SPECIFIC_HOOK_AND_TONE_TAGS
from recommender.pipeline import _build_structured_indexes
from recommender.scoring import make_salience_weighted_tag_metric, score_candidates
from recommender.structure_policy import (
    DEFAULT_NARRATIVE_STRUCTURE_POLICY,
    NarrativeStructure,
    resolve_narrative_profile,
)
from recommender.union import PathEvidence, UnionCandidate

POLICY_TAGS = (Tag.ANTHOLOGY, Tag.SERIALIZED, Tag.EPISODIC, Tag.PROCEDURAL)


@pytest.mark.parametrize(
    ('tag', 'structure'),
    [
        (Tag.ANTHOLOGY, NarrativeStructure.ANTHOLOGY),
        (Tag.SERIALIZED, NarrativeStructure.SERIALIZED),
        (Tag.EPISODIC, NarrativeStructure.EPISODIC),
    ],
)
def test_procedural_is_independent_of_narrative_structure(tag: Tag, structure: NarrativeStructure) -> None:
    profile = resolve_narrative_profile((tag, Tag.PROCEDURAL))
    assert profile.structure is structure
    assert DEFAULT_NARRATIVE_STRUCTURE_POLICY.multiplier(profile, profile) == (
        DEFAULT_NARRATIVE_STRUCTURE_POLICY.multiplier(structure, structure)
    )


@pytest.mark.parametrize('tag', POLICY_TAGS)
def test_narrative_form_neither_adds_similarity_nor_dilutes_content(tag: Tag) -> None:
    idf_cases: tuple[Mapping[str, float] | None, ...] = (None, {tag: 100.0, Tag.REVENGE: 2.0})
    for idfs in idf_cases:
        metric = make_salience_weighted_tag_metric(idf_map=idfs)
        assert metric(frozenset({tag}), frozenset({tag})) == 0.0
        assert metric(frozenset({Tag.REVENGE, tag}), frozenset({Tag.REVENGE})) == 1.0
        assert metric(frozenset({Tag.REVENGE}), frozenset({Tag.REVENGE, tag})) == 1.0
    assert get_tag_salience(tag) == 0.0
    assert tag in NON_NARRATIVE_TAGS
    assert tag not in SPECIFIC_HOOK_AND_TONE_TAGS


def test_assignments_retain_policy_tags_but_feature_vectors_exclude_them() -> None:
    assignments = (TagAssignment((1,), POLICY_TAGS), TagAssignment((2,), (Tag.REVENGE,)))
    assert set(apply_tag_assignments((1, 2), assignments)[1]) == set(POLICY_TAGS)
    blocks = build_categorical_blocks(
        pl.DataFrame({'mal_id': [1, 2]}),
        np.asarray([1, 2], dtype=np.int64),
        include_studios=False,
        properties=(CategoricalProperty('tags', CategoricalEncoding.MULTI_HOT, manual_tags=True),),
        tag_assignments=assignments,
    )
    assert blocks[0].column_names == (Tag.REVENGE,)
    assert not blocks[0].dense_row(0).any()
    assert blocks[0].dense_row(1).tolist() == [1.0]


def test_shared_narrative_form_does_not_retrieve_candidates() -> None:
    indexes, _ = _build_structured_indexes(
        (1, 2, 3),
        pl.DataFrame({'mal_id': [1, 2, 3]}),
        ((), (), ()),
        ((), (), ()),
        ((), (), ()),
        (POLICY_TAGS, POLICY_TAGS, (Tag.REVENGE,)),
        ('tags',),
    )
    assert indexes['tags'].rank_many((0,), limit=10) == ((),)


def test_policy_tags_do_not_change_content_score_but_still_drive_narrative_policy() -> None:
    candidate = UnionCandidate(2, (PathEvidence('embedding', 1, 0.7),))

    def score(tags: Mapping[int, tuple[str, ...]], *, narrative_policy: bool = False) -> float:
        return score_candidates(
            1,
            (candidate,),
            genres_by_id={},
            themes_by_id={},
            tags_by_id=tags,
            demographics_by_id={},
            structure_policy=DEFAULT_NARRATIVE_STRUCTURE_POLICY if narrative_policy else None,
        )[0].score

    baseline = score({1: (Tag.REVENGE,), 2: (Tag.REVENGE,)})
    policy_tags = {1: (Tag.REVENGE, Tag.ANTHOLOGY), 2: (Tag.REVENGE, Tag.SERIALIZED)}
    assert score(policy_tags) == baseline
    assert score(policy_tags, narrative_policy=True) == pytest.approx(baseline * 0.92)
