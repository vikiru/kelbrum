from recommender.language_policy import (
    LanguageCompatibilityPolicy,
    OriginLanguage,
)


def test_origin_language_policy_same_language() -> None:
    policy = LanguageCompatibilityPolicy()
    assert policy.multiplier(OriginLanguage.JAPANESE, OriginLanguage.JAPANESE) == 1.02
    assert policy.multiplier('Japanese', 'Japanese') == 1.02
    assert policy.multiplier(OriginLanguage.CHINESE, OriginLanguage.CHINESE) == 1.02
    assert policy.multiplier(OriginLanguage.KOREAN, OriginLanguage.KOREAN) == 1.02


def test_origin_language_policy_cross_language_dampening() -> None:
    policy = LanguageCompatibilityPolicy()
    # Cross language with low/moderate semantic similarity is dampened
    assert policy.multiplier(OriginLanguage.JAPANESE, OriginLanguage.CHINESE, dense_similarity=0.30) == 0.40
    assert policy.multiplier('Japanese', 'Korean', dense_similarity=0.45) == 0.40
    assert policy.multiplier(OriginLanguage.CHINESE, OriginLanguage.JAPANESE, dense_similarity=0.20) == 0.40


def test_origin_language_policy_high_semantic_override() -> None:
    policy = LanguageCompatibilityPolicy()
    # Very high semantic similarity (>= 0.68) exempts from cross-language dampening
    assert policy.multiplier(OriginLanguage.JAPANESE, OriginLanguage.CHINESE, dense_similarity=0.70) == 1.00
    assert policy.multiplier('Japanese', 'Korean', dense_similarity=0.68) == 1.00
    assert policy.multiplier(OriginLanguage.JAPANESE, OriginLanguage.CHINESE, dense_similarity=0.62) == 0.40


def test_origin_language_policy_unknown_or_empty() -> None:
    policy = LanguageCompatibilityPolicy()
    assert policy.multiplier(OriginLanguage.UNKNOWN, OriginLanguage.JAPANESE) == 1.00
    assert policy.multiplier(OriginLanguage.JAPANESE, OriginLanguage.UNKNOWN) == 1.00
    assert policy.multiplier(None, 'Japanese') == 1.00
    assert policy.multiplier('', '') == 1.00
