"""Composable similarity-property specifications for recommendation indexes."""

from collections.abc import Mapping
from math import isfinite

import msgspec

from recommender.metrics import Similarity, SimilarityName


class SimilarityProperty(msgspec.Struct, frozen=True):
    """Describe one feature block's weight, metric, and content role."""

    name: str
    weight: float
    metric: SimilarityName = Similarity.COSINE
    contributes_to_content: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError('similarity property name cannot be empty')
        if not isfinite(self.weight) or self.weight < 0.0:
            raise ValueError('similarity property weight must be finite and non-negative')
        try:
            metric = Similarity(self.metric)
        except ValueError as error:
            raise ValueError(f'unsupported similarity metric: {self.metric}') from error
        object.__setattr__(self, 'metric', metric)


def default_similarity_properties(
    weights: Mapping[str, float],
    metrics: Mapping[str, SimilarityName],
    content_names: frozenset[str],
) -> tuple[SimilarityProperty, ...]:
    """Translate configured maps into ordered property specifications."""
    return tuple(
        SimilarityProperty(name, weight, metrics.get(name, 'cosine'), name in content_names)
        for name, weight in weights.items()
    )
