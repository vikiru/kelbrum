"""Verification tests for production plan defaults and baseline rollback parity."""

from recommender.language_policy import LanguageCompatibilityPolicy
from recommender.plan import RecommenderPlan
from recommender.structure_policy import NarrativeStructurePolicy
from recommender.union import RetrievalGroupBudget


def test_recommender_plan_defaults_to_production_configuration() -> None:
    plan = RecommenderPlan()
    assert plan.retrieval_paths == ('embedding', 'weighted-v2', 'bm25', 'themes', 'genres', 'tags', 'lsa')
    assert plan.retrieval_group_budget == RetrievalGroupBudget(
        semantic=600, structured=600, neighbourhood=200, affinity=60
    )
    assert plan.gated_synopsis_transfer is True
    assert plan.evidence_qualified_multiplier is True
    assert plan.embedding_gate_low == 0.42
    assert plan.embedding_gate_high == 0.54
    assert plan.pure_tone_contradiction_guard is True
    assert plan.generic_genre_suppression is True
    assert plan.hook_tag_promotion is True
    assert plan.scoring_paths == ('bm25', 'lsa', 'embedding')


def test_bm25_can_remain_a_retrieval_path_without_scoring() -> None:
    plan = RecommenderPlan(retrieval_paths=('bm25', 'lsa'), scoring_paths=('bm25', 'lsa', 'embedding'))

    assert plan.has_path('bm25')
    assert plan.scoring_paths == ('bm25', 'lsa', 'embedding')


def test_recommender_plan_c0_b100_rollback_configuration() -> None:
    c0_plan = RecommenderPlan(
        retrieval_group_budget=RetrievalGroupBudget(),
        gated_synopsis_transfer=False,
        evidence_qualified_multiplier=False,
        pure_tone_contradiction_guard=False,
    )
    assert c0_plan.gated_synopsis_transfer is False
    assert c0_plan.evidence_qualified_multiplier is False
    assert c0_plan.pure_tone_contradiction_guard is False
    assert c0_plan.retrieval_group_budget == RetrievalGroupBudget()
    assert c0_plan.identity != RecommenderPlan().identity


def test_recommender_plan_pure_tone_contradiction_guard_toggle() -> None:
    unguarded_plan = RecommenderPlan(pure_tone_contradiction_guard=False)
    assert unguarded_plan.pure_tone_contradiction_guard is False
    assert unguarded_plan.identity != RecommenderPlan().identity


def test_recommender_plan_identity_includes_structure_and_language_policies() -> None:
    default_id = RecommenderPlan().identity
    assert RecommenderPlan(structure_policy=None).identity != default_id
    assert (
        RecommenderPlan(structure_policy=NarrativeStructurePolicy(anthology_to_anthology_boost=1.25)).identity
        != default_id
    )
    assert RecommenderPlan(language_policy=None).identity != default_id
    assert (
        RecommenderPlan(language_policy=LanguageCompatibilityPolicy(cross_language_dampen=0.50)).identity != default_id
    )
