"""Deterministic ordering policies for scored recommendation candidates."""

from collections.abc import Mapping, Sequence
from typing import NamedTuple, Protocol


class ScoredCandidate(NamedTuple):
    recommendation_entity_id: int
    witness_member_id: int
    score: float
    retrieval_paths: tuple[str, ...]


class RankingPolicy(Protocol):
    """Policy for ordering already-scored candidates."""

    name: str
    identity: str

    def rank(self, candidates: Sequence[ScoredCandidate]) -> tuple[ScoredCandidate, ...]: ...


class ScoreDescending:
    """Rank by descending score, then recommendation identity for deterministic ties."""

    name = 'score-descending'
    identity = 'score-descending-v1'

    def rank(
        self,
        candidates: Sequence[ScoredCandidate],
        *,
        shared_tag_counts: Mapping[int, int] | None = None,
    ) -> tuple[ScoredCandidate, ...]:
        if shared_tag_counts is None:
            return tuple(sorted(candidates, key=_candidate_sort_key))
        return tuple(
            sorted(
                candidates,
                key=lambda item: (
                    -shared_tag_counts.get(item.recommendation_entity_id, 0),
                    -len(item.retrieval_paths),
                    -item.score,
                    item.recommendation_entity_id,
                ),
            )
        )


def _candidate_sort_key(item: ScoredCandidate) -> tuple[int, float, int]:
    return -len(item.retrieval_paths), -item.score, item.recommendation_entity_id
