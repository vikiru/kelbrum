"""Kelbrum recommender package."""

from recommender.frozen_pipeline import Recommender
from recommender.inputs import RecommenderInputs
from recommender.metrics import Distance, Similarity, tversky
from recommender.paths import SynopsisPathIndex, build_synopsis_path_index
from recommender.plan import RecommenderPlan
from recommender.properties import SimilarityProperty
from recommender.ranking import RankingPolicy, ScoreDescending
from recommender.rating_policy import RatingClass, RatingPolicy
from recommender.scoring import PropertyValues, ScoringProperty
from recommender.union import (
    EvidenceUnion,
    NoUnion,
    PathEvidence,
    UnionCandidate,
    build_union,
    build_union_from_results,
)
from recommender.weighted_v2 import WeightedV2Index
from recommender.weighted_v2 import weighted_similarity as v2_weighted_similarity

__all__ = [
    'Distance',
    'EvidenceUnion',
    'NoUnion',
    'PathEvidence',
    'PropertyValues',
    'RankingPolicy',
    'RatingClass',
    'RatingPolicy',
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
    'build_synopsis_path_index',
    'build_union',
    'build_union_from_results',
    'tversky',
    'v2_weighted_similarity',
]
