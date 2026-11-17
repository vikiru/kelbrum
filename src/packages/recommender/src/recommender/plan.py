"""Declarative recommender composition and policy identity."""

from math import isfinite

import msgspec

from config import derive_payload_identity
from features.blocks import AvailabilityPolicy
from recommender.language_policy import DEFAULT_LANGUAGE_COMPATIBILITY_POLICY, LanguageCompatibilityPolicy
from recommender.properties import SimilarityProperty
from recommender.ranking import RankingPolicy, ScoreDescending
from recommender.rating_policy import RatingPolicy
from recommender.scoring import DEFAULT_SYNOPSIS_SCORING_PATHS, ScoringProperty, default_scoring_properties
from recommender.structure_policy import DEFAULT_NARRATIVE_STRUCTURE_POLICY, NarrativeStructurePolicy
from recommender.union import (
    DEFAULT_RETRIEVAL_PATHS,
    UNION_POLICY_IDENTITY,
    RetrievalGroupBudget,
    validate_retrieval_paths,
)

SYNOPSIS_SCORING_PATHS = ('bm25', 'lsa', 'embedding')


class RecommenderPlan(msgspec.Struct, frozen=True):
    """Declare recommender policies without holding prepared runtime indexes."""

    retrieval_paths: tuple[str, ...] = DEFAULT_RETRIEVAL_PATHS
    scoring_paths: tuple[str, ...] = DEFAULT_SYNOPSIS_SCORING_PATHS
    scoring_properties: tuple[ScoringProperty, ...] = msgspec.field(default_factory=default_scoring_properties)
    ranking_policy: RankingPolicy = msgspec.field(default_factory=ScoreDescending)
    rating_policy: RatingPolicy = msgspec.field(default_factory=RatingPolicy)
    similarity_properties: tuple[SimilarityProperty, ...] | None = None
    availability_policy: AvailabilityPolicy | None = None
    availability_policy_identity: str = 'default'
    relationship_policy_identity: str = 'canonical-franchise-v1'
    retrieval_limit: int = 600
    retrieval_batch_size: int = 4096
    retrieval_group_budget: RetrievalGroupBudget | None = msgspec.field(default_factory=RetrievalGroupBudget)
    gated_synopsis_transfer: bool = True
    evidence_qualified_multiplier: bool = True
    weak_maturity_demotion: bool = False
    weak_maturity_demotion_penalty: float = 0.02
    embedding_gate_low: float = 0.42
    embedding_gate_high: float = 0.54
    pure_tone_contradiction_guard: bool = True
    metadata_post_ranking: bool = True
    generic_genre_suppression: bool = True
    hook_tag_promotion: bool = True
    structure_policy: NarrativeStructurePolicy | None = msgspec.field(
        default_factory=lambda: DEFAULT_NARRATIVE_STRUCTURE_POLICY
    )
    language_policy: LanguageCompatibilityPolicy | None = msgspec.field(
        default_factory=lambda: DEFAULT_LANGUAGE_COMPATIBILITY_POLICY
    )

    def __post_init__(self) -> None:
        """Validate plan values before expensive indexes are constructed."""
        object.__setattr__(self, 'retrieval_paths', validate_retrieval_paths(self.retrieval_paths))
        if len(set(self.scoring_paths)) != len(self.scoring_paths):
            raise ValueError('scoring paths must be unique')
        unsupported_scoring_paths = set(self.scoring_paths) - set(SYNOPSIS_SCORING_PATHS)
        if unsupported_scoring_paths:
            raise ValueError(f'unsupported synopsis scoring paths: {", ".join(sorted(unsupported_scoring_paths))}')
        if self.retrieval_limit < 1:
            raise ValueError('retrieval_limit must be positive')
        if self.retrieval_batch_size < 1:
            raise ValueError('retrieval batch size must be positive')
        if not self.availability_policy_identity.strip():
            raise ValueError('availability policy identity cannot be empty')
        if not self.relationship_policy_identity.strip():
            raise ValueError('relationship policy identity cannot be empty')
        if not isfinite(self.weak_maturity_demotion_penalty) or self.weak_maturity_demotion_penalty < 0.0:
            raise ValueError('weak maturity demotion penalty cannot be negative')
        if not isfinite(self.embedding_gate_low) or not isfinite(self.embedding_gate_high):
            raise ValueError('embedding gate thresholds must be finite')
        if self.embedding_gate_low < 0.0 or self.embedding_gate_high <= self.embedding_gate_low:
            raise ValueError('embedding_gate_low must be non-negative and strictly less than embedding_gate_high')

    @property
    def identity(self) -> str:
        """Return the stable semantic identity of this recommender composition."""
        return derive_payload_identity(
            {
                'retrieval_paths': self.retrieval_paths,
                'scoring_paths': self.scoring_paths,
                'union': UNION_POLICY_IDENTITY,
                'scoring': tuple(_scoring_identity(item) for item in self.scoring_properties),
                'ranking': self.ranking_policy.identity,
                'rating': self.rating_policy.identity,
                'similarity': self.similarity_properties,
                'availability': self.availability_policy_identity,
                'relationship': self.relationship_policy_identity,
                'retrieval_limit': self.retrieval_limit,
                'retrieval_batch_size': self.retrieval_batch_size,
                'retrieval_group_budget': self.retrieval_group_budget,
                'scoring_version': 'scoring-v3-3',
                'gated_synopsis_transfer': self.gated_synopsis_transfer,
                'evidence_qualified_multiplier': self.evidence_qualified_multiplier,
                'weak_maturity_demotion': self.weak_maturity_demotion,
                'weak_maturity_demotion_penalty': self.weak_maturity_demotion_penalty,
                'embedding_gate': (self.embedding_gate_low, self.embedding_gate_high),
                'pure_tone_contradiction_guard': self.pure_tone_contradiction_guard,
                'metadata_post_ranking': self.metadata_post_ranking,
                'generic_genre_suppression': self.generic_genre_suppression,
                'hook_tag_promotion': self.hook_tag_promotion,
                'structure_policy': self.structure_policy,
                'language_policy': self.language_policy,
            }
        )

    def has_path(self, name: str) -> bool:
        """Return whether one validated retrieval path is enabled."""
        return name in self.retrieval_paths


def _scoring_identity(property_spec: ScoringProperty) -> tuple[str, float, str]:
    """Require an explicit identity for every replaceable scoring metric."""
    if property_spec.metric_identity is None:
        raise ValueError(f'scoring property requires a metric identity: {property_spec.name}')
    return property_spec.name, property_spec.weight, property_spec.metric_identity
