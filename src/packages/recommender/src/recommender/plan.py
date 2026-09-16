"""Declarative recommender composition and policy identity."""

import msgspec

from config import derive_payload_identity
from features.blocks import AvailabilityPolicy
from recommender.properties import SimilarityProperty
from recommender.ranking import RankingPolicy, ScoreDescending
from recommender.rating_policy import RatingPolicy
from recommender.scoring import ScoringProperty, default_scoring_properties
from recommender.union import (
    AVAILABLE_RETRIEVAL_PATHS,
    DEFAULT_RETRIEVAL_FAMILY_BUDGET,
    EvidenceUnion,
    RetrievalFamilyBudget,
    RetrievalMode,
    UnionPolicy,
    validate_retrieval_paths,
)


class RecommenderPlan(msgspec.Struct, frozen=True):
    """Declare recommender policies without holding prepared runtime indexes."""

    retrieval_paths: tuple[str, ...] = AVAILABLE_RETRIEVAL_PATHS
    union_policy: UnionPolicy = msgspec.field(default_factory=EvidenceUnion)
    scoring_properties: tuple[ScoringProperty, ...] = msgspec.field(default_factory=default_scoring_properties)
    ranking_policy: RankingPolicy = msgspec.field(default_factory=ScoreDescending)
    rating_policy: RatingPolicy = msgspec.field(default_factory=RatingPolicy)
    similarity_properties: tuple[SimilarityProperty, ...] | None = None
    availability_policy: AvailabilityPolicy | None = None
    availability_policy_identity: str = 'default'
    relationship_policy_identity: str = 'canonical-franchise-v1'
    retrieval_limit: int = 300
    retrieval_batch_size: int = 4096
    retrieval_mode: RetrievalMode = RetrievalMode.FAMILY_REDUCED
    retrieval_family_budget: RetrievalFamilyBudget = DEFAULT_RETRIEVAL_FAMILY_BUDGET

    def __post_init__(self) -> None:
        """Validate plan values before expensive indexes are constructed."""
        object.__setattr__(self, 'retrieval_paths', validate_retrieval_paths(self.retrieval_paths))
        if self.retrieval_limit < 1:
            raise ValueError('retrieval_limit must be positive')
        if self.retrieval_batch_size < 1:
            raise ValueError('retrieval batch size must be positive')
        if not self.availability_policy_identity.strip():
            raise ValueError('availability policy identity cannot be empty')
        if not self.relationship_policy_identity.strip():
            raise ValueError('relationship policy identity cannot be empty')

    @property
    def identity(self) -> str:
        """Return the stable semantic identity of this recommender composition."""
        return derive_payload_identity(
            {
                'retrieval_paths': self.retrieval_paths,
                'union': self.union_policy.identity,
                'scoring': tuple(_scoring_identity(item) for item in self.scoring_properties),
                'ranking': self.ranking_policy.identity,
                'rating': self.rating_policy.identity,
                'similarity': self.similarity_properties,
                'availability': self.availability_policy_identity,
                'relationship': self.relationship_policy_identity,
                'retrieval_limit': self.retrieval_limit,
                'retrieval_batch_size': self.retrieval_batch_size,
                'retrieval_mode': self.retrieval_mode.value,
                'retrieval_family_budget': self.retrieval_family_budget,
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
