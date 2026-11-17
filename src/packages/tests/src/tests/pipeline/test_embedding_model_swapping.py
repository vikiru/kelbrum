import pytest

from features.config import EmbeddingModel, EmbeddingSource, FeatureConfig
from features.constants import default_embedding_gate
from pipeline.build import _default_recommender_plan
from recommender.plan import RecommenderPlan
from recommender.scoring import soft_embedding_gate


def test_default_embedding_gate_calibrations() -> None:
    assert default_embedding_gate('sentence-transformers/all-mpnet-base-v2') == (0.42, 0.54)
    assert default_embedding_gate('sentence-transformers/all-MiniLM-L6-v2') == (0.30, 0.375)
    assert default_embedding_gate('BAAI/bge-base-en-v1.5') == (0.6534, 0.7179)
    assert default_embedding_gate('Qwen/Qwen3-Embedding-0.6B') == (0.56, 0.68)
    assert default_embedding_gate(None) == (0.42, 0.54)
    assert default_embedding_gate('unknown-model') == (0.42, 0.54)


def test_recommender_plan_embedding_gate_validation() -> None:
    # Valid plan
    plan = RecommenderPlan(embedding_gate_low=0.30, embedding_gate_high=0.45)
    assert plan.embedding_gate_low == 0.30
    assert plan.embedding_gate_high == 0.45

    # Identity changes when thresholds change
    plan_mpnet = RecommenderPlan(embedding_gate_low=0.42, embedding_gate_high=0.54)
    plan_minilm = RecommenderPlan(embedding_gate_low=0.30, embedding_gate_high=0.375)
    assert plan_mpnet.identity != plan_minilm.identity

    # Rejection of invalid thresholds
    with pytest.raises(ValueError, match='embedding_gate_low must be non-negative and strictly less'):
        RecommenderPlan(embedding_gate_low=0.60, embedding_gate_high=0.40)

    with pytest.raises(ValueError, match='embedding_gate_low must be non-negative and strictly less'):
        RecommenderPlan(embedding_gate_low=0.50, embedding_gate_high=0.50)

    with pytest.raises(ValueError, match='embedding_gate_low must be non-negative and strictly less'):
        RecommenderPlan(embedding_gate_low=-0.1, embedding_gate_high=0.50)


def test_default_recommender_plan_calibrates_from_feature_config() -> None:
    # MPNet feature config
    cfg_mpnet = FeatureConfig(
        embedding=EmbeddingModel(
            source=EmbeddingSource.REMOTE,
            identifier='sentence-transformers/all-mpnet-base-v2',
        )
    )
    plan_mpnet = _default_recommender_plan(cfg_mpnet)
    assert plan_mpnet.embedding_gate_low == 0.42
    assert plan_mpnet.embedding_gate_high == 0.54

    # Qwen feature config
    cfg_qwen = FeatureConfig(
        embedding=EmbeddingModel(
            source=EmbeddingSource.REMOTE,
            identifier='Qwen/Qwen3-Embedding-0.6B',
        )
    )
    plan_qwen = _default_recommender_plan(cfg_qwen)
    assert plan_qwen.embedding_gate_low == 0.56
    assert plan_qwen.embedding_gate_high == 0.68

    # BGE feature config
    cfg_bge = FeatureConfig(
        embedding=EmbeddingModel(
            source=EmbeddingSource.REMOTE,
            identifier='BAAI/bge-base-en-v1.5',
        )
    )
    plan_bge = _default_recommender_plan(cfg_bge)
    assert plan_bge.embedding_gate_low == 0.6534
    assert plan_bge.embedding_gate_high == 0.7179


def test_soft_embedding_gate_swapped_cutoffs() -> None:
    # Test Qwen soft gate over [0.56, 0.68]
    low, high = 0.56, 0.68
    assert soft_embedding_gate(0.50, low=low, high=high) == 0.0
    assert soft_embedding_gate(0.70, low=low, high=high) == 0.70

    mid = 0.62
    expected = ((mid - low) / (high - low)) * mid
    assert soft_embedding_gate(mid, low=low, high=high) == pytest.approx(expected)
