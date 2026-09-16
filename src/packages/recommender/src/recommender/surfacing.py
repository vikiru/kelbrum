"""Conservative variable-length display policy for ranked recommendations."""

from collections.abc import Sequence

import msgspec

from recommender.contracts import RawRecommendation

DEFAULT_MINIMUM_SCORE = 0.20
DEFAULT_MAXIMUM_RESULTS = 100


class SurfacingPolicy(msgspec.Struct, frozen=True):
    """Apply the temporary v2 display floor without changing similarity scores."""

    name = 'minimum-score-v1'
    minimum_score: float = DEFAULT_MINIMUM_SCORE
    maximum_results: int = DEFAULT_MAXIMUM_RESULTS

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_score <= 1.0:
            raise ValueError('minimum_score must be between 0 and 1')
        if not 1 <= self.maximum_results <= DEFAULT_MAXIMUM_RESULTS:
            raise ValueError(f'maximum_results must be between 1 and {DEFAULT_MAXIMUM_RESULTS}')

    def surface(self, ranked_items: Sequence[RawRecommendation]) -> tuple[RawRecommendation, ...]:
        """Keep ranked items above the floor, up to the maximum result count."""
        surfaced = tuple(item for item in ranked_items if item.score >= self.minimum_score)
        return surfaced[: self.maximum_results]
