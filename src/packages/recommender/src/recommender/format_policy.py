"""Format and duration-aware affinity policies for recommendation candidates."""

import math
from enum import StrEnum
from typing import Final

import msgspec

from normalization.metadata import AnimeType


class FormatCohort(StrEnum):
    TV = 'TV'
    MOVIE = 'MOVIE'
    ONA_SERIES = 'ONA_SERIES'
    ONA_MOVIE = 'ONA_MOVIE'
    ONA_SHORT = 'ONA_SHORT'


def classify_format_cohort(
    anime_type: str | None,
    duration_minutes: float | None,
    episodes: int | None,
) -> FormatCohort:
    normalized_type = (anime_type or '').strip().upper()
    duration = duration_minutes or 24.0
    episode_count = episodes or 1

    if normalized_type == AnimeType.TV:
        return FormatCohort.TV
    if normalized_type == AnimeType.MOVIE:
        return FormatCohort.MOVIE
    if normalized_type == AnimeType.ONA:
        if episode_count == 1 and duration >= 30.0:
            return FormatCohort.ONA_MOVIE
        if duration < 15.0 or (episode_count <= 3 and duration < 30.0):
            return FormatCohort.ONA_SHORT
        return FormatCohort.ONA_SERIES
    return FormatCohort.TV


class FormatAffinityPolicy(msgspec.Struct, frozen=True):
    series_movie_bridge: float = 0.95
    short_damping: float = 0.88
    deadband_delta: float = 1.5
    penalty_lambda: float = 0.02
    peer_long_runner_boost: float = 1.03

    def compute_format_multiplier(
        self,
        source_cohort: FormatCohort,
        candidate_cohort: FormatCohort,
    ) -> float:
        if source_cohort == candidate_cohort:
            return 1.0

        if (source_cohort == FormatCohort.TV and candidate_cohort == FormatCohort.ONA_SERIES) or (
            source_cohort == FormatCohort.ONA_SERIES and candidate_cohort == FormatCohort.TV
        ):
            return 0.99

        if (source_cohort == FormatCohort.MOVIE and candidate_cohort == FormatCohort.ONA_MOVIE) or (
            source_cohort == FormatCohort.ONA_MOVIE and candidate_cohort == FormatCohort.MOVIE
        ):
            return 0.99

        if candidate_cohort == FormatCohort.ONA_SHORT or source_cohort == FormatCohort.ONA_SHORT:
            return self.short_damping

        is_source_series = source_cohort in (FormatCohort.TV, FormatCohort.ONA_SERIES)
        is_candidate_film = candidate_cohort in (FormatCohort.MOVIE, FormatCohort.ONA_MOVIE)
        is_source_film = source_cohort in (FormatCohort.MOVIE, FormatCohort.ONA_MOVIE)
        is_candidate_series = candidate_cohort in (FormatCohort.TV, FormatCohort.ONA_SERIES)

        if (is_source_series and is_candidate_film) or (is_source_film and is_candidate_series):
            return self.series_movie_bridge

        return 1.0

    def compute_volume_commitment_multiplier(
        self,
        source_episodes: int | None,
        candidate_episodes: int | None,
    ) -> float:
        source_count = max(1, source_episodes or 12)
        candidate_count = max(1, candidate_episodes or 12)

        log_gap = abs(math.log2((source_count + 6) / (candidate_count + 6)))
        excess_gap = max(0.0, log_gap - self.deadband_delta)
        penalty = math.exp(-self.penalty_lambda * (excess_gap**2))

        if source_count >= 75 and candidate_count >= 75:
            return round(penalty * self.peer_long_runner_boost, 4)

        return round(penalty, 4)


DEFAULT_FORMAT_POLICY: Final[FormatAffinityPolicy] = FormatAffinityPolicy()
