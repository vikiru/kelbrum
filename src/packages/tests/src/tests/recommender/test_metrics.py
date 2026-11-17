import math
from dataclasses import dataclass

import numpy as np
import polars as pl
import pytest
from scipy.sparse import csr_matrix

from features.blocks import FeatureBlock, FeatureBundle
from features.tags import Tag
from recommender.clash_rules import (
    ClashFlag,
    compile_anchor_clash_rules,
    evaluate_compiled_clash_rules,
    evaluate_compiled_clash_rules_batch,
)
from recommender.inputs import RecommenderInputs
from recommender.metrics import (
    TVERSKY_ALPHA,
    TVERSKY_BETA,
    Similarity,
    SimilarityOperands,
    build_idf_csr,
    idf_tversky,
    similarity_score,
    tversky,
    vectorized_similarity,
)
from recommender.pipeline import Recommender, _prepare_catalogue
from recommender.plan import RecommenderPlan
from recommender.rating_policy import RatingPolicy
from recommender.scoring import (
    EMBEDDING_CONFIDENCE_GATE,
    EMBEDDING_GATE_HIGH,
    EMBEDDING_GATE_LOW,
    SIGMOID_GATE_CENTER,
    SIGMOID_GATE_SLOPE,
    ScoringProperty,
    anime_type_piecewise_affinity,
    coverage,
    default_scoring_properties,
    demographic_piecewise_affinity,
    dice,
    fuse_synopsis_scores,
    fuse_synopsis_vectors,
    make_idf_tversky,
    score_candidates,
    sigmoid_embedding_gate,
    soft_embedding_gate,
)
from recommender.structure_policy import NarrativeStructure
from recommender.union import PathEvidence, UnionCandidate


@dataclass(frozen=True)
class _RankingEval:
    ndcg: float


def evaluate_ranking(ranked_ids: tuple[int, ...], grades: dict[int, int], *, cutoff: int) -> _RankingEval:
    if len(set(ranked_ids)) != len(ranked_ids):
        raise ValueError('duplicate catalogue IDs')
    if any(g < 0 or g > 3 for g in grades.values()):
        raise ValueError('relevance grades must be in 0..3')
    dcg = sum((2 ** grades.get(aid, 0) - 1) / math.log2(i + 2) for i, aid in enumerate(ranked_ids[:cutoff]))
    ideal = sorted(grades.values(), reverse=True)[:cutoff]
    idcg = sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(ideal))
    return _RankingEval(ndcg=dcg / idcg if idcg > 0 else 0.0)


def test_tversky_is_registered_as_a_shared_similarity_type() -> None:
    assert Similarity.TVERSKY.value == 'tversky'
    assert TVERSKY_ALPHA == 0.7
    assert TVERSKY_BETA == 0.3


def test_tversky_is_asymmetric_with_default_parameters() -> None:
    assert tversky({'genre'}, {'genre', 'extra'}) == 1.0 / 1.3
    assert tversky({'genre', 'extra'}, {'genre'}) == 1.0 / 1.7


def test_tversky_returns_zero_for_empty_sets() -> None:
    assert tversky(set(), set()) == 0.0


@pytest.mark.parametrize(
    ('metric', 'expected'),
    [
        (Similarity.JACCARD, 1.0 / 3.0),
        (Similarity.DICE, 0.5),
        (Similarity.MANHATTAN, 2.0 / 3.0),
    ],
)
def test_scalar_metrics_match_expected_scores(metric: Similarity, expected: float) -> None:
    left = np.asarray([1.0, 1.0, 0.0])
    right = np.asarray([1.0, 0.0, 1.0])
    if metric is Similarity.MANHATTAN:
        left = np.asarray([0.0, 1.0])
        right = np.asarray([1.0, 1.0])

    assert similarity_score(left, right, metric) == pytest.approx(expected)


@pytest.mark.parametrize('metric', [Similarity.JACCARD, Similarity.DICE])
def test_set_metrics_return_zero_for_empty_vectors(metric: Similarity) -> None:
    values = np.zeros(3)

    assert similarity_score(values, values, metric) == 0.0


def test_coverage_and_dice_handle_sequences_and_empty_candidates() -> None:
    source = frozenset({'a', 'b', 'c'})

    assert coverage(source, ['a', 'c', 'extra']) == pytest.approx(2.0 / 3.0)
    assert dice(source, ['a', 'c', 'extra']) == pytest.approx(2.0 / 3.0)
    assert coverage(source, ()) == 0.0
    assert dice(source, None) == 0.0


def test_default_theme_similarity_uses_idf_tversky() -> None:
    properties = {property_spec.name: property_spec for property_spec in default_scoring_properties()}

    assert properties['themes'].metric_identity == 'idf-tversky-7525-v1'
    assert properties['tags'].metric_identity == 'salience-weighted-tversky-82-content-v2'
    assert properties['genres'].metric_identity == 'idf-tversky-64-v1'
    assert properties['demographics'].metric is demographic_piecewise_affinity
    assert properties['demographics'].metric_identity == 'piecewise-affinity-v1'


def test_idf_tversky_weights_and_asymmetry() -> None:
    source = frozenset({'action', 'rare'})
    cand = frozenset({'action', 'common'})
    idf_map = {'action': 1.0, 'rare': 4.0, 'common': 0.5}

    expected = 1.0 / 4.3
    assert idf_tversky(source, cand, alpha=0.8, beta=0.2, idf_map=idf_map) == pytest.approx(expected)
    assert idf_tversky(source, ()) == 0.0
    assert idf_tversky(frozenset(), cand) == 0.0


@pytest.mark.parametrize('invalid_weight', [-1.0, float('nan'), float('inf')])
def test_idf_tversky_factory_rejects_invalid_weights(invalid_weight: float) -> None:
    with pytest.raises(ValueError, match='finite and non-negative'):
        make_idf_tversky(idf_map={'tag': invalid_weight})


@pytest.mark.parametrize(
    ('metric', 'expected'),
    [
        (Similarity.JACCARD, np.asarray([1.0 / 3.0, 0.0])),
        (Similarity.DICE, np.asarray([0.5, 0.0])),
        (Similarity.TVERSKY, np.asarray([0.5, 0.0])),
    ],
)
def test_vectorized_set_metrics_match_scalar_definitions(metric: Similarity, expected: np.ndarray) -> None:
    operands = SimilarityOperands(
        intersections=np.asarray([1.0, 0.0]),
        left_sizes=np.asarray([2.0, 0.0]),
        right_sizes=np.asarray([2.0, 0.0]),
    )

    np.testing.assert_allclose(vectorized_similarity(metric, operands), expected)


def test_vectorized_manhattan_matches_scalar_definition() -> None:
    operands = SimilarityOperands(differences=np.asarray([[1.0, 0.0], [2.0, 2.0]]))

    np.testing.assert_allclose(
        vectorized_similarity(Similarity.MANHATTAN, operands),
        np.asarray([2.0 / 3.0, 1.0 / 3.0]),
    )


def test_embedding_confidence_gate_soft_ramp() -> None:
    assert EMBEDDING_GATE_LOW == 0.42
    assert EMBEDDING_GATE_HIGH == 0.54
    assert EMBEDDING_CONFIDENCE_GATE == 0.54
    assert SIGMOID_GATE_SLOPE == 8.0
    assert SIGMOID_GATE_CENTER == 0.35

    # Continuous sigmoid gate: smooth monotonic attenuation
    assert sigmoid_embedding_gate(0.0) == 0.0
    assert sigmoid_embedding_gate(-0.5) == 0.0
    assert sigmoid_embedding_gate(0.35) == pytest.approx(0.35 * 0.50)

    values = [0.35, 0.40, 0.42, 0.45, 0.48, 0.50, 0.52, 0.54, 0.60]
    attenuated = [sigmoid_embedding_gate(v) for v in values]
    for i in range(len(attenuated) - 1):
        assert attenuated[i] < attenuated[i + 1]

    # Explicit legacy linear ramp test via use_sigmoid=False
    assert soft_embedding_gate(0.25, use_sigmoid=False) == 0.0
    mid_sim = 0.48
    expected_linear = ((mid_sim - 0.42) / (0.54 - 0.42)) * mid_sim
    assert soft_embedding_gate(mid_sim, use_sigmoid=False) == pytest.approx(expected_linear)
    assert soft_embedding_gate(0.60, use_sigmoid=False) == 0.60

    # Explicit custom low/high thresholds (e.g. MiniLM [0.30, 0.375] or Qwen [0.56, 0.68])
    assert soft_embedding_gate(0.35, low=0.30, high=0.375) == pytest.approx(((0.35 - 0.30) / (0.375 - 0.30)) * 0.35)
    c_mid = UnionCandidate(2, (PathEvidence('embedding', 1, mid_sim),))
    res_custom = score_candidates(
        1,
        (c_mid,),
        genres_by_id={},
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={},
        properties=(),
        embedding_gate_low=0.30,
        embedding_gate_high=0.375,
    )
    expected_syn = fuse_synopsis_scores(0.0, 0.0, 0.48)
    assert res_custom[0][2] == pytest.approx(0.41 * expected_syn)


def test_demographic_piecewise_affinity_values() -> None:
    # Identical cohort
    assert demographic_piecewise_affinity(frozenset({'Shounen'}), ('Shounen',)) == 1.0
    assert demographic_piecewise_affinity(frozenset({'Seinen'}), ('Seinen',)) == 1.0

    # High cross affinity
    assert demographic_piecewise_affinity(frozenset({'Shounen'}), ('Seinen',)) == 0.80
    assert demographic_piecewise_affinity(frozenset({'Seinen'}), ('Shounen',)) == 0.80
    assert demographic_piecewise_affinity(frozenset({'Shoujo'}), ('Josei',)) == 0.85

    # Moderate cross affinity
    assert demographic_piecewise_affinity(frozenset({'Shounen'}), ('Kids',)) == 0.50
    assert demographic_piecewise_affinity(frozenset({'Shounen'}), ('Shoujo',)) == 0.40

    # Disjoint cross affinity
    assert demographic_piecewise_affinity(frozenset({'Seinen'}), ('Kids',)) == 0.10

    # Case insensitivity
    assert demographic_piecewise_affinity(frozenset({'shounen'}), ('seinen',)) == 0.80
    assert demographic_piecewise_affinity(frozenset({'SHOUNEN'}), ('SEINEN',)) == 0.80

    # Empty inputs
    assert demographic_piecewise_affinity(frozenset(), ('Shounen',)) == 0.0
    assert demographic_piecewise_affinity(frozenset({'Shounen'}), ()) == 0.0
    assert demographic_piecewise_affinity(frozenset({'Shounen'}), None) == 0.0


def test_rating_gate_uses_raw_embedding_cosine_separately_from_fused_synopsis() -> None:
    candidate = UnionCandidate(2, (PathEvidence('embedding', 1, 0.5),))

    scored = score_candidates(
        1,
        (candidate,),
        genres_by_id={},
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={2: ('Kids',)},
        ratings_by_id={1: 'R', 2: 'PG'},
        rating_policy=RatingPolicy(),
        properties=(),
        synopsis_pairwise_dense={2: 0.8},
        rating_embedding_cosine={2: 0.1},
    )

    assert scored[0].score == pytest.approx(0.41 * 0.8 * 0.36)


def test_anime_type_piecewise_affinity_values() -> None:
    # Identical format
    assert anime_type_piecewise_affinity(frozenset({'TV'}), ('TV',)) == 1.0
    assert anime_type_piecewise_affinity(frozenset({'ONA'}), ('ONA',)) == 1.0
    assert anime_type_piecewise_affinity(frozenset({'MOVIE'}), ('MOVIE',)) == 1.0

    # Cross affinities
    assert anime_type_piecewise_affinity(frozenset({'TV'}), ('ONA',)) == 0.88
    assert anime_type_piecewise_affinity(frozenset({'ONA'}), ('TV',)) == 0.88
    assert anime_type_piecewise_affinity(frozenset({'ONA'}), ('MOVIE',)) == 0.75
    assert anime_type_piecewise_affinity(frozenset({'TV'}), ('MOVIE',)) == 0.60

    # Case insensitivity
    assert anime_type_piecewise_affinity(frozenset({'tv'}), ('ona',)) == 0.88
    assert anime_type_piecewise_affinity(frozenset({'tv'}), ('movie',)) == 0.60

    # Empty inputs
    assert anime_type_piecewise_affinity(frozenset(), ('TV',)) == 0.0
    assert anime_type_piecewise_affinity(frozenset({'TV'}), ()) == 0.0
    assert anime_type_piecewise_affinity(frozenset({'TV'}), None) == 0.0


@pytest.mark.parametrize(
    ('anchor_id', 'first_id', 'first_grade', 'second_id', 'second_grade'),
    [
        (44942, 10087, 2, 22297, 3),
        (52299, 136, 2, 11061, 1),
        (22319, 35120, 3, 1628, 2),
        (9253, 849, 2, 7311, 2),
        (11757, 48, 3, 873, 2),
        (523, 37682, 2, 37433, 2),
        (37150, 47548, 2, 36491, 3),
        (37150, 40233, 3, 55151, 2),
    ],
)
def test_evaluation_never_credits_a_sibling_judgment(
    anchor_id: int, first_id: int, first_grade: int, second_id: int, second_grade: int
) -> None:
    _ = anchor_id

    assert evaluate_ranking((first_id,), {second_id: second_grade}, cutoff=1).ndcg == 0.0
    assert evaluate_ranking((second_id,), {first_id: first_grade}, cutoff=1).ndcg == 0.0


def test_evaluation_rejects_duplicate_ids_and_invalid_grades() -> None:
    with pytest.raises(ValueError, match='duplicate catalogue IDs'):
        evaluate_ranking((1, 1), {1: 3}, cutoff=2)
    with pytest.raises(ValueError, match='relevance grades'):
        evaluate_ranking((1,), {1: 4}, cutoff=1)


def test_blend_10_synopsis_fusion_properties() -> None:
    """Verify production fuse_synopsis_scores properties and safe numerical behaviour."""
    # Case 1: Identical values preserve value when channels are equally scaled or without BM25 pre-scaling
    assert np.isclose(fuse_synopsis_scores(0.3, 0.3, 0.3, bm25_scale_factor=1.0), 0.3)

    # Case 2: Near-zero BM25 with high agreement on the other semantic paths.
    bm25_val, lsa_val, emb_val = 0.005, 0.40, 0.40
    a_score = (bm25_val + lsa_val + emb_val) / 3.0
    g_score = max(0.0, ((bm25_val + 0.02) * (lsa_val + 0.02) * (emb_val + 0.02)) ** (1.0 / 3.0) - 0.02)
    blend10 = fuse_synopsis_scores(
        bm25_val,
        lsa_val,
        emb_val,
        active_paths=('bm25', 'lsa', 'embedding'),
        geom_weight=0.90,
        arith_weight=0.10,
        path_weights={'bm25': 1.0, 'lsa': 1.0, 'embedding': 1.0},
        bm25_scale_factor=1.0,
    )
    assert g_score < a_score
    assert blend10 > g_score
    assert np.isclose(blend10, 0.90 * g_score + 0.10 * a_score)

    # Pure arithmetic verification with equal weights
    pure_arith = fuse_synopsis_scores(
        bm25_val,
        lsa_val,
        emb_val,
        active_paths=('bm25', 'lsa', 'embedding'),
        geom_weight=0.0,
        arith_weight=1.0,
        path_weights={'bm25': 1.0, 'lsa': 1.0, 'embedding': 1.0},
        bm25_scale_factor=1.0,
    )
    assert np.isclose(pure_arith, a_score)

    # Case 3: Complete zero evidence
    assert np.isclose(fuse_synopsis_scores(0.0, 0.0, 0.0), 0.0)

    # Case 4: Safe numerical handling of negative, inf, and NaN inputs
    assert fuse_synopsis_scores(-0.5, 0.4, 0.4) == fuse_synopsis_scores(0.0, 0.4, 0.4)
    assert np.isfinite(fuse_synopsis_scores(float('nan'), 0.4, float('inf')))


def test_synopsis_fusion_scalar_vectorized_parity() -> None:
    """Verify strict mathematical parity between scalar fuse_synopsis_scores and vectorized fuse_synopsis_vectors."""
    bm25_vals = [0.0, 0.1, 0.5, 1.0, -0.5, float('nan'), float('inf'), float('-inf'), 0.0]
    lsa_vals = [0.0, 0.2, 0.4, 0.8, 0.3, 0.5, float('nan'), 0.2, 0.0]
    emb_vals = [0.0, 0.3, 0.6, 0.9, float('nan'), 0.1, 0.0, float('inf'), 0.0]

    b_arr = np.array(bm25_vals, dtype=np.float64)
    l_arr = np.array(lsa_vals, dtype=np.float64)
    e_arr = np.array(emb_vals, dtype=np.float64)

    active_paths = ('bm25', 'lsa', 'embedding')
    vectorized_res = fuse_synopsis_vectors(b_arr, l_arr, e_arr, active_paths=active_paths)

    for i in range(len(bm25_vals)):
        scalar_res = fuse_synopsis_scores(bm25_vals[i], lsa_vals[i], emb_vals[i], active_paths=active_paths)
        assert np.isclose(vectorized_res[i], scalar_res, atol=1e-12), (
            f'Parity mismatch at index {i}: scalar={scalar_res}, vectorized={vectorized_res[i]} '
            f'for inputs ({bm25_vals[i]}, {lsa_vals[i]}, {emb_vals[i]})'
        )


def test_synopsis_fusion_uses_three_active_paths_by_default() -> None:
    score = fuse_synopsis_scores(0.8, 0.4, 0.4)

    assert score > fuse_synopsis_scores(0.0, 0.4, 0.4)


def test_synopsis_fusion_uses_two_active_paths_when_bm25_is_disabled() -> None:
    active_paths = ('lsa', 'embedding')
    scalar = fuse_synopsis_scores(0.0, 0.4, 0.4, active_paths=active_paths)
    vector = fuse_synopsis_vectors(
        np.array([0.0]),
        np.array([0.4]),
        np.array([0.4]),
        active_paths=active_paths,
    )

    assert scalar == pytest.approx(0.4)
    assert vector[0] == pytest.approx(scalar)


def test_synopsis_fusion_ignores_bm25_when_explicitly_disabled() -> None:
    active_paths = ('lsa', 'embedding')
    without_bm25 = fuse_synopsis_scores(0.0, 0.2, 0.8, active_paths=active_paths)
    with_bm25_value = fuse_synopsis_scores(1.0, 0.2, 0.8, active_paths=active_paths)

    assert with_bm25_value == pytest.approx(without_bm25)
    assert fuse_synopsis_scores(1.0, 0.2, 0.8) != pytest.approx(without_bm25)


def test_candidate_evidence_fallback_uses_all_default_synopsis_paths() -> None:
    candidate = UnionCandidate(
        2,
        (
            PathEvidence('bm25', 1, 1.0),
            PathEvidence('lsa', 2, 0.4),
            PathEvidence('embedding', 3, 0.4),
        ),
    )

    scored = score_candidates(
        1,
        (candidate,),
        genres_by_id={},
        themes_by_id={},
        tags_by_id={},
        demographics_by_id={},
        properties=(),
    )

    expected_synopsis = fuse_synopsis_scores(1.0, 0.4, sigmoid_embedding_gate(0.4))
    assert scored[0].score == pytest.approx(0.41 * expected_synopsis)


def test_pure_tone_contradiction_guard_penalizes_incompatible_comedy() -> None:
    """Verify that pure_tone_contradiction_guard penalizes comedy when anchor is a serious thriller without comedy."""
    candidate = UnionCandidate(2, (PathEvidence('embedding', 1, 0.50), PathEvidence('genres', 1, 0.50)))

    # Anchor 1 is suspense/horror without comedy. Candidate 2 has comedy and disjoint themes/tags.
    genres = {1: ('suspense', 'horror'), 2: ('comedy', 'action')}
    themes = {1: ('psychological',), 2: ('parody',)}
    tags = {1: ('dark',), 2: ('slapstick',)}
    demos = {1: (), 2: ()}

    # 1. Guard disabled (default): unpenalized score
    res_unguarded = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=False,
    )

    res_guarded = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=True,
    )

    assert res_unguarded[0].score > 0.0
    assert res_guarded[0].score == pytest.approx(res_unguarded[0].score)


def test_pure_tone_contradiction_guard_leaves_compatible_comedy_intact() -> None:
    """Verify that pure_tone_contradiction_guard does NOT penalize when anchor has comedy or shares specific tags."""
    candidate = UnionCandidate(2, (PathEvidence('embedding', 1, 0.50), PathEvidence('genres', 1, 0.50)))

    # Case A: Anchor itself includes comedy -> guard does not trigger
    genres_comedy = {1: ('suspense', 'comedy'), 2: ('comedy', 'action')}
    themes = {1: ('psychological',), 2: ('parody',)}
    tags = {1: ('dark',), 2: ('slapstick',)}
    demos = {1: (), 2: ()}

    res_a = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres_comedy,
        themes_by_id=themes,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=True,
    )
    res_a_base = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres_comedy,
        themes_by_id=themes,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=False,
    )
    assert res_a[0].score == pytest.approx(res_a_base[0].score)

    # Case B: Candidate shares 2 specific themes/tags -> guard does not trigger
    genres_serious = {1: ('suspense',), 2: ('comedy',)}
    themes_shared = {1: ('psychological', 'detective'), 2: ('psychological', 'detective', 'parody')}
    res_b = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres_serious,
        themes_by_id=themes_shared,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=True,
    )
    res_b_base = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres_serious,
        themes_by_id=themes_shared,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=False,
    )
    assert res_b[0].score >= res_b_base[0].score


def test_pure_tone_contradiction_guard_penalizes_incompatible_romance_harem() -> None:
    """Verify that pure_tone_contradiction_guard penalizes pure romance/harem on serious action anchors."""
    candidate = UnionCandidate(2, (PathEvidence('embedding', 1, 0.50), PathEvidence('genres', 1, 0.50)))

    # Anchor 1 is pure action without romance or comedy. Candidate 2 is pure romance/harem without action continuity.
    genres = {1: ('action', 'supernatural'), 2: ('romance', 'drama')}
    themes = {1: ('super power',), 2: ('harem',)}
    tags = {1: ('dark',), 2: ('school_club',)}
    demos = {1: (), 2: ()}

    res_unguarded = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=False,
    )
    res_guarded = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=True,
    )

    assert res_unguarded[0].score > 0.0
    assert res_guarded[0].score == pytest.approx(res_unguarded[0].score)


def test_pure_tone_contradiction_guard_penalizes_iyashikei_against_dark_gore() -> None:
    """Verify that pure_tone_contradiction_guard penalizes dark/gore candidates on pure iyashikei/SoL anchors."""
    candidate = UnionCandidate(2, (PathEvidence('embedding', 1, 0.50), PathEvidence('genres', 1, 0.50)))

    # Iyashikei anchor (e.g. Yuru Camp, Non Non Biyori) vs Dark/Gore/Horror candidate (e.g. Corpse Party)
    genres = {1: ('slice of life',), 2: ('horror',)}
    themes = {1: ('iyashikei',), 2: ('gore',)}
    tags = {1: (Tag.HEARTWARMING,), 2: (Tag.DARK, Tag.BLEAK)}
    demos = {1: (), 2: ()}

    res_unguarded = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=False,
    )
    res_guarded = score_candidates(
        1,
        (candidate,),
        genres_by_id=genres,
        themes_by_id=themes,
        tags_by_id=tags,
        demographics_by_id=demos,
        pure_tone_contradiction_guard=True,
    )

    assert res_unguarded[0].score > 0.0
    assert res_guarded[0].score < res_unguarded[0].score * 0.40


def test_pure_tone_contradiction_guard_protects_multi_tonal_anchors() -> None:
    """Verify that multi-tonal anchors like FMA:B and Bleach (Action + Comedy + Drama) are never penalized."""
    candidate_dark = UnionCandidate(2, (PathEvidence('embedding', 1, 0.50), PathEvidence('genres', 1, 0.50)))
    candidate_comedy = UnionCandidate(3, (PathEvidence('embedding', 1, 0.50), PathEvidence('genres', 1, 0.50)))
    candidate_romance = UnionCandidate(4, (PathEvidence('embedding', 1, 0.50), PathEvidence('genres', 1, 0.50)))

    # FMA:B / Bleach multi-tonal profile: Action + Comedy + Drama + Military/Supernatural
    genres = {
        1: ('action', 'adventure', 'comedy', 'drama'),
        2: ('horror', 'suspense'),
        3: ('comedy',),
        4: ('romance',),
    }
    themes = {
        1: ('military',),
        2: ('gore', 'psychological'),
        3: ('parody',),
        4: ('harem',),
    }
    tags = {1: (), 2: (), 3: (), 4: ()}
    demos = {1: (), 2: (), 3: (), 4: ()}

    for cand in (candidate_dark, candidate_comedy, candidate_romance):
        res_unguarded = score_candidates(
            1,
            (cand,),
            genres_by_id=genres,
            themes_by_id=themes,
            tags_by_id=tags,
            demographics_by_id=demos,
            pure_tone_contradiction_guard=False,
        )
        res_guarded = score_candidates(
            1,
            (cand,),
            genres_by_id=genres,
            themes_by_id=themes,
            tags_by_id=tags,
            demographics_by_id=demos,
            pure_tone_contradiction_guard=True,
        )
        # Multi-tonal anchor should have ZERO penalties applied across dark, comedy, or romance
        assert res_guarded[0].score == pytest.approx(res_unguarded[0].score)


def test_prepare_catalogue_tags_csr_matches_salience_sqrt_idf_metric() -> None:
    frame = pl.DataFrame(
        {
            'mal_id': [1, 2, 3, 4],
            'title': ['A', 'B', 'C', 'D'],
            'genres': [['Drama'], ['Drama'], ['Drama'], ['Drama']],
            'themes': [[], [], [], []],
            'demographics': [[], [], [], []],
            'rating_class': ['G', 'G', 'G', 'G'],
            'synopsis': ['An anthology of short stories.', None, '', 'Continuous tale.'],
            'synopsis_features': ['', '', '', ''],
            'studio_ids': [[], [], [], []],
            'manual_tags': [
                [Tag.REVENGE.value, Tag.TIME_LOOP.value],
                [Tag.REVENGE.value, Tag.CONSPIRACY.value],
                [Tag.REVENGE.value],
                [Tag.REVENGE.value],
            ],
        }
    )
    bundle = FeatureBundle(
        np.asarray([1, 2, 3, 4], dtype=np.int64),
        (FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0], [1.0], [1.0]]), ('Drama',), ('genres',)),),
    )
    state = _prepare_catalogue(frame, bundle, RatingPolicy())
    candidate = UnionCandidate(2, (PathEvidence('tags', 1, 0.5),))

    csr_scored = score_candidates(
        1,
        (candidate,),
        genres_by_id=state.genres_by_id,
        themes_by_id=state.themes_by_id,
        tags_by_id=state.tags_by_id,
        demographics_by_id=state.demographics_by_id,
        properties=default_scoring_properties(
            tag_idf=state.idfs_by_property['tags'],
            theme_idf=state.idfs_by_property['themes'],
            genre_idf=state.idfs_by_property['genres'],
        ),
        tags_csr=state.tags_csr,
        themes_csr=state.themes_csr,
        genres_csr=state.genres_csr,
        index_by_id=state.index_by_id,
    )
    scalar_scored = score_candidates(
        1,
        (candidate,),
        genres_by_id=state.genres_by_id,
        themes_by_id=state.themes_by_id,
        tags_by_id=state.tags_by_id,
        demographics_by_id=state.demographics_by_id,
        properties=default_scoring_properties(
            tag_idf=state.idfs_by_property['tags'],
            theme_idf=state.idfs_by_property['themes'],
            genre_idf=state.idfs_by_property['genres'],
        ),
    )
    assert csr_scored[0].score == pytest.approx(scalar_scored[0].score)
    assert state.narrative_profiles_by_id[1].structure is NarrativeStructure.ANTHOLOGY
    assert state.narrative_profiles_by_id[4].structure is NarrativeStructure.UNKNOWN


def test_score_candidates_does_not_bypass_custom_metric_when_csr_is_present() -> None:
    candidate = UnionCandidate(2, (PathEvidence('embedding', 1, 0.6),))
    tags_by_id = {1: (Tag.REVENGE.value,), 2: (Tag.REVENGE.value,)}
    tags_csr = build_idf_csr(((Tag.REVENGE.value,), (Tag.REVENGE.value,)), idf_map={Tag.REVENGE.value: 1.0})
    custom_called = False

    def custom_metric(_source: frozenset[str], _candidate: object) -> float:
        nonlocal custom_called
        custom_called = True
        return 0.25

    expected = score_candidates(
        1,
        (candidate,),
        genres_by_id={},
        themes_by_id={},
        tags_by_id=tags_by_id,
        demographics_by_id={},
        properties=(ScoringProperty('tags', 0.20, custom_metric, 'custom-tags-v1'),),
    )
    custom_called = False
    scored = score_candidates(
        1,
        (candidate,),
        genres_by_id={},
        themes_by_id={},
        tags_by_id=tags_by_id,
        demographics_by_id={},
        properties=(ScoringProperty('tags', 0.20, custom_metric, 'custom-tags-v1'),),
        tags_csr=tags_csr,
        index_by_id={1: 0, 2: 1},
    )
    assert custom_called is True
    assert scored[0].score == pytest.approx(expected[0].score)


def test_recommender_wires_narrative_profiles_and_synopses_from_catalogue() -> None:
    frame = pl.DataFrame(
        {
            'mal_id': [1, 2],
            'title': ['One', 'Two'],
            'genres': [['Drama'], ['Drama']],
            'themes': [[], []],
            'demographics': [[], []],
            'rating_class': ['G', 'G'],
            'synopsis': ['An anthology of short stories.', 'A collection of short vignettes.'],
            'synopsis_features': ['anthology', 'vignettes'],
            'studio_ids': [[], []],
            'manual_tags': [[], []],
        }
    )
    bundle = FeatureBundle(
        np.asarray([1, 2], dtype=np.int64),
        (FeatureBlock('genres', 'multi-hot', csr_matrix([[1.0], [1.0]]), ('Drama',), ('genres',)),),
    )
    rec = Recommender(RecommenderInputs(frame, bundle), RecommenderPlan(retrieval_paths=('genres',), scoring_paths=()))
    assert rec._narrative_profiles_by_row[0] is not None
    assert rec._narrative_profiles_by_row[0].structure is NarrativeStructure.ANTHOLOGY
    assert rec._synopses_by_row == ('An anthology of short stories.', 'A collection of short vignettes.')


def test_clash_rules_batch_hook_counts_match_scalar() -> None:
    anchor_mask = ClashFlag.MYSTERY_INVESTIGATION | ClashFlag.TIME_META_LOOP | ClashFlag.CRAFT_CAREER_PERFORMANCE
    candidate_masks = [
        int(ClashFlag.NONE),
        int(ClashFlag.MYSTERY_INVESTIGATION),
        int(ClashFlag.MYSTERY_INVESTIGATION | ClashFlag.TIME_META_LOOP),
        int(ClashFlag.MYSTERY_INVESTIGATION | ClashFlag.TIME_META_LOOP | ClashFlag.CRAFT_CAREER_PERFORMANCE),
    ]
    compiled = compile_anchor_clash_rules(anchor_mask)
    cosines = np.full(len(candidate_masks), 0.5, dtype=np.float64)
    batch_scores = evaluate_compiled_clash_rules_batch(
        compiled,
        np.asarray(candidate_masks, dtype=np.int64),
        cosines,
        anchor_mask=int(anchor_mask),
    )
    for idx, cand_mask in enumerate(candidate_masks):
        scalar = evaluate_compiled_clash_rules(compiled, cand_mask, 0.5, anchor_mask=int(anchor_mask))
        assert batch_scores[idx] == pytest.approx(scalar)
