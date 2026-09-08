"""Kelbrum recommender package."""

from recommender.evaluation import (
    StrategyComparison,
    StrategyRun,
    compare_recommendations,
    compare_strategies,
    write_comparison_report,
)
from recommender.frozen_pipeline import Recommender
from recommender.index import SimilarityIndex
from recommender.paths import SynopsisPathIndex, build_synopsis_path_index, rank_categorical
from recommender.relationship_graph import add_manual_relationships, build_relationship_index
from recommender.union import PathEvidence, UnionCandidate, build_union, build_union_from_results
from recommender.weighted_v2 import WeightedV2Index
from recommender.weighted_v2 import weighted_distance as v2_weighted_distance

__all__ = [
    'PathEvidence',
    'Recommender',
    'SimilarityIndex',
    'StrategyComparison',
    'StrategyRun',
    'SynopsisPathIndex',
    'UnionCandidate',
    'WeightedV2Index',
    'add_manual_relationships',
    'build_relationship_index',
    'build_synopsis_path_index',
    'build_union',
    'build_union_from_results',
    'compare_recommendations',
    'compare_strategies',
    'rank_categorical',
    'v2_weighted_distance',
    'write_comparison_report',
]
