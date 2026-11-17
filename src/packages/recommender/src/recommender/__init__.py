"""Kelbrum recommender package."""

from recommender.inputs import RecommenderInputs
from recommender.metrics import Distance, Similarity, tversky
from recommender.paths import SynopsisPathIndex, build_synopsis_path_index
from recommender.pipeline import Recommender
from recommender.plan import RecommenderPlan
from recommender.properties import SimilarityProperty
from recommender.ranking import RankingPolicy, ScoreDescending
from recommender.rating_policy import RatingClass, RatingDecision, RatingPolicy, RatingPolicyMode
from recommender.scoring import (
    PropertyValues,
    ScoringProperty,
    anime_type_piecewise_affinity,
    demographic_piecewise_affinity,
)
from recommender.union import (
    PathEvidence,
    UnionCandidate,
    build_union,
    build_union_from_results,
)
from recommender.weighted_v2 import WeightedV2Index
from recommender.weighted_v2 import weighted_similarity as v2_weighted_similarity

__all__ = [
    'Distance',
    'PathEvidence',
    'PropertyValues',
    'RankingPolicy',
    'RatingClass',
    'RatingDecision',
    'RatingPolicy',
    'RatingPolicyMode',
    'Recommender',
    'RecommenderInputs',
    'RecommenderPlan',
    'ScoreDescending',
    'ScoringProperty',
    'Similarity',
    'SimilarityProperty',
    'SynopsisPathIndex',
    'UnionCandidate',
    'WeightedV2Index',
    'anime_type_piecewise_affinity',
    'build_synopsis_path_index',
    'build_union',
    'build_union_from_results',
    'demographic_piecewise_affinity',
    'tversky',
    'v2_weighted_similarity',
]
