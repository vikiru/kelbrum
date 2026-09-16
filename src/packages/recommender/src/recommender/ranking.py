"""Deterministic ordering policies for scored recommendation candidates."""

from collections.abc import Sequence
from typing import Protocol

ScoredCandidate = tuple[int, int, float, tuple[str, ...]]


class RankingPolicy(Protocol):
    """Policy for ordering already-scored candidates."""

    name: str
    identity: str

    def rank(self, candidates: Sequence[ScoredCandidate]) -> tuple[ScoredCandidate, ...]: ...


class ScoreDescending:
    """Rank by descending score, then canonical ID for deterministic ties."""

    name = 'score-descending'
    identity = 'score-descending-v1'

    def rank(self, candidates: Sequence[ScoredCandidate]) -> tuple[ScoredCandidate, ...]:
        return tuple(sorted(candidates, key=_score_key))


def _score_key(item: ScoredCandidate) -> tuple[float, int]:
    return -item[2], item[0]
