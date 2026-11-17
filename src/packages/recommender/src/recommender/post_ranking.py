"""Production metadata post-ranker for Kelbrum V2.

Computes bounded piecewise multipliers across 5 selected metadata groups:
- Audience: demographics + age rating
- Chronology: release year
- Type: TV, Movie, ONA only
- Franchise scope: relationship-graph-derived mainline runtime
- Quality: MAL score

Applies:
    final_score = base_score * clip(1.0 + 5.0 * delta_meta, 0.92, 1.06)
where:
    delta_meta = (
        1.0 * audience +
        0.4 * chronology +
        0.5 * type +
        0.5 * franchise +
        1.0 * quality
    )
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

import polars as pl

from anime_catalogue.demographics import Demographic, parse_demographic
from anime_catalogue.taxonomy import SETTING_BACKDROP_THEMES, Genre, Theme
from graph.contracts import RelationType, SameStoryIntent
from normalization.metadata import AnimeType
from normalization.ratings import RatingClass, normalize_rating
from recommender.format_policy import (
    DEFAULT_FORMAT_POLICY,
    classify_format_cohort,
)

DEMO_HYPOTHESIS: Final[dict[tuple[Demographic, Demographic], float]] = {
    (Demographic.KIDS, Demographic.KIDS): 0.006,
    (Demographic.KIDS, Demographic.SHOUNEN): -0.005,
    (Demographic.KIDS, Demographic.SEINEN): -0.020,
    (Demographic.KIDS, Demographic.SHOUJO): -0.005,
    (Demographic.KIDS, Demographic.JOSEI): -0.015,
    (Demographic.SHOUNEN, Demographic.KIDS): -0.018,
    (Demographic.SHOUNEN, Demographic.SHOUNEN): 0.006,
    (Demographic.SHOUNEN, Demographic.SEINEN): 0.0,
    (Demographic.SHOUNEN, Demographic.SHOUJO): -0.004,
    (Demographic.SHOUNEN, Demographic.JOSEI): -0.006,
    (Demographic.SEINEN, Demographic.KIDS): -0.025,
    (Demographic.SEINEN, Demographic.SHOUNEN): 0.0,
    (Demographic.SEINEN, Demographic.SEINEN): 0.006,
    (Demographic.SEINEN, Demographic.SHOUJO): -0.005,
    (Demographic.SEINEN, Demographic.JOSEI): 0.0,
    (Demographic.SHOUJO, Demographic.KIDS): -0.012,
    (Demographic.SHOUJO, Demographic.SHOUNEN): -0.004,
    (Demographic.SHOUJO, Demographic.SEINEN): -0.005,
    (Demographic.SHOUJO, Demographic.SHOUJO): 0.006,
    (Demographic.SHOUJO, Demographic.JOSEI): 0.0,
    (Demographic.JOSEI, Demographic.KIDS): -0.020,
    (Demographic.JOSEI, Demographic.SHOUNEN): -0.006,
    (Demographic.JOSEI, Demographic.SEINEN): 0.0,
    (Demographic.JOSEI, Demographic.SHOUJO): 0.0,
    (Demographic.JOSEI, Demographic.JOSEI): 0.006,
}

RATING_HYPOTHESIS: Final[dict[tuple[RatingClass, RatingClass], float]] = {
    (RatingClass.G, RatingClass.G): 0.004,
    (RatingClass.G, RatingClass.PG): 0.002,
    (RatingClass.G, RatingClass.PG_13): -0.008,
    (RatingClass.G, RatingClass.R): -0.012,
    (RatingClass.G, RatingClass.R_PLUS): -0.008,
    (RatingClass.PG, RatingClass.G): 0.002,
    (RatingClass.PG, RatingClass.PG): 0.004,
    (RatingClass.PG, RatingClass.PG_13): -0.006,
    (RatingClass.PG, RatingClass.R): -0.010,
    (RatingClass.PG, RatingClass.R_PLUS): -0.006,
    (RatingClass.PG_13, RatingClass.G): 0.0,
    (RatingClass.PG_13, RatingClass.PG): 0.0,
    (RatingClass.PG_13, RatingClass.PG_13): 0.004,
    (RatingClass.PG_13, RatingClass.R): 0.0,
    (RatingClass.PG_13, RatingClass.R_PLUS): 0.0,
    (RatingClass.R, RatingClass.G): -0.016,
    (RatingClass.R, RatingClass.PG): -0.012,
    (RatingClass.R, RatingClass.PG_13): 0.0,
    (RatingClass.R, RatingClass.R): 0.004,
    (RatingClass.R, RatingClass.R_PLUS): 0.0,
    (RatingClass.R_PLUS, RatingClass.G): -0.010,
    (RatingClass.R_PLUS, RatingClass.PG): -0.006,
    (RatingClass.R_PLUS, RatingClass.PG_13): 0.0,
    (RatingClass.R_PLUS, RatingClass.R): 0.0,
    (RatingClass.R_PLUS, RatingClass.R_PLUS): 0.004,
}

TYPE_COMPATIBILITY: Final[dict[tuple[str, str], float]] = {
    ('TV', 'TV'): 0.000,
    ('TV', 'MOVIE'): -0.004,
    ('TV', 'ONA'): 0.000,
    ('MOVIE', 'TV'): -0.002,
    ('MOVIE', 'MOVIE'): 0.000,
    ('MOVIE', 'ONA'): 0.000,
    ('ONA', 'TV'): 0.000,
    ('ONA', 'MOVIE'): -0.003,
    ('ONA', 'ONA'): 0.000,
}

MIN_MULTIPLIER_BOUND: Final[float] = 0.65
MAX_MULTIPLIER_BOUND: Final[float] = 1.15
MULTIPLIER_SCALE: Final[float] = 5.0

WEIGHT_AUDIENCE: Final[float] = 1.0
WEIGHT_FORMAT_COMMITMENT: Final[float] = 1.0
WEIGHT_QUALITY: Final[float] = 0.5
WEIGHT_STUDIO: Final[float] = 0.8

MAINLINE_RELATION_TYPES: Final[frozenset[str]] = frozenset(
    {
        RelationType.SEQUEL.value,
        RelationType.PARENT_STORY.value,
        RelationType.FULL_STORY.value,
        RelationType.PREQUEL.value,
    }
)
MAINLINE_CONTINUATION_INTENT: Final[str] = SameStoryIntent.CONTINUATION.value


@dataclass(slots=True, frozen=True)
class AnimePostRankingMetadata:
    """Pre-extracted metadata attributes required for post-ranking adjustments."""

    anime_id: int
    anime_type: str
    demographic: str
    rating: str
    year: int | None
    score: float | None
    mainline_runtime_minutes: float
    demographics: tuple[str, ...] = ()
    studios: frozenset[int] | frozenset[str] | tuple[str, ...] = ()
    episodes: int | None = None
    storyline_episodes: int | None = None
    duration_minutes: float | None = None
    is_award_winning: bool = False


def normalize_demographic(raw_demographics: Sequence[str] | None) -> str:
    """Map raw catalogue demographics list to discrete classification."""
    if not raw_demographics:
        return 'Missing'
    if len(raw_demographics) == 1:
        return raw_demographics[0]
    return 'Multiple'


def normalize_rating_label(raw_rating: str | None) -> str:
    """Extract rating code prefix (e.g. 'R - 17+ (violence & profanity)' -> 'R')."""
    if raw_rating is None:
        return 'Unknown'
    return raw_rating.split(' - ')[0].strip()


def compute_audience_adjustment(anchor: AnimePostRankingMetadata, candidate: AnimePostRankingMetadata) -> float:
    demographic_adjustment = 0.0
    anchor_demographics = anchor.demographics or (
        (anchor.demographic,) if anchor.demographic not in ('Missing', 'Multiple') else ()
    )
    candidate_demographics = candidate.demographics or (
        (candidate.demographic,) if candidate.demographic not in ('Missing', 'Multiple') else ()
    )
    anchor_demos = {parsed for d in anchor_demographics if (parsed := parse_demographic(d)) is not Demographic.UNKNOWN}
    candidate_demos = {
        parsed for d in candidate_demographics if (parsed := parse_demographic(d)) is not Demographic.UNKNOWN
    }

    if anchor_demos and candidate_demos:
        pairwise_compatibilities = [
            DEMO_HYPOTHESIS.get((a_demo, c_demo), 0.0) for a_demo in anchor_demos for c_demo in candidate_demos
        ]
        demographic_adjustment = max(pairwise_compatibilities) if pairwise_compatibilities else 0.0

    rating_adjustment = 0.0
    anchor_rating = normalize_rating(anchor.rating)
    candidate_rating = normalize_rating(candidate.rating)
    if anchor_rating is not RatingClass.UNKNOWN and candidate_rating is not RatingClass.UNKNOWN:
        is_anchor_mature = (
            anchor_rating in (RatingClass.R, RatingClass.R_PLUS, RatingClass.R_X) or Demographic.SEINEN in anchor_demos
        )
        is_candidate_children = (
            candidate_rating in (RatingClass.G, RatingClass.PG) or Demographic.KIDS in candidate_demos
        )
        if is_anchor_mature and is_candidate_children:
            rating_adjustment = -0.010
        elif (
            anchor_rating is RatingClass.PG_13
            and candidate_rating is RatingClass.R_PLUS
            and Demographic.SEINEN not in anchor_demos
        ):
            rating_adjustment = -0.008
        else:
            rating_adjustment = RATING_HYPOTHESIS.get((anchor_rating, candidate_rating), 0.0)

    return 0.5 * demographic_adjustment + 0.5 * rating_adjustment


def resolve_effective_anime_type(anime_type: str, duration_minutes: float | None, episodes: int | None = None) -> str:
    cohort = classify_format_cohort(anime_type, duration_minutes, episodes)
    return str(cohort.value)


def compute_format_commitment_adjustment(
    anchor: AnimePostRankingMetadata,
    candidate: AnimePostRankingMetadata,
) -> float:
    cohort_anchor = classify_format_cohort(anchor.anime_type, anchor.duration_minutes, anchor.episodes)
    cohort_candidate = classify_format_cohort(candidate.anime_type, candidate.duration_minutes, candidate.episodes)
    format_mult = DEFAULT_FORMAT_POLICY.compute_format_multiplier(cohort_anchor, cohort_candidate)

    anchor_episodes = anchor.storyline_episodes if anchor.storyline_episodes is not None else anchor.episodes
    candidate_episodes = (
        candidate.storyline_episodes if candidate.storyline_episodes is not None else candidate.episodes
    )
    volume_mult = DEFAULT_FORMAT_POLICY.compute_volume_commitment_multiplier(anchor_episodes, candidate_episodes)

    combined_mult = format_mult * volume_mult
    return round((combined_mult - 1.0) / MULTIPLIER_SCALE, 4)


def compute_bucket_distance_adjustment(
    anchor_bucket: int | None,
    candidate_bucket: int | None,
    *,
    max_penalty: float = 0.030,
    step_penalty: float = 0.010,
) -> float:
    if anchor_bucket is None or candidate_bucket is None:
        return 0.0
    distance = abs(anchor_bucket - candidate_bucket)
    if distance <= 1:
        return 0.0
    return -min(max_penalty, (distance - 1) * step_penalty)


def compute_studio_adjustment(
    anchor: AnimePostRankingMetadata,
    candidate: AnimePostRankingMetadata,
    *,
    dense_cosine: float = 0.50,
    shared_hooks_count: int = 0,
) -> float:
    if not anchor.studios or not candidate.studios:
        return 0.0
    shared = set(anchor.studios) & set(candidate.studios)
    if not shared:
        return 0.0
    if dense_cosine < 0.44 or shared_hooks_count < 2:
        return 0.0
    return 0.003


def compute_quality_adjustment(
    anchor: AnimePostRankingMetadata,
    candidate: AnimePostRankingMetadata,
    *,
    dense_cosine: float = 0.50,
) -> float:
    candidate_score = candidate.score
    if candidate_score is None:
        return -0.060 if dense_cosine < 0.55 else 0.0

    anchor_score = anchor.score or 7.0
    if anchor_score >= 7.50 and candidate_score < 6.50 and dense_cosine < 0.75:
        score_gap = anchor_score - candidate_score - 1.0
        return max(-0.200, -0.080 * score_gap)

    if candidate_score >= 8.5:
        base_quality = 0.018
    elif candidate_score >= 8.2:
        base_quality = 0.012 + (candidate_score - 8.2) / 0.3 * (0.018 - 0.012)
    elif candidate_score >= 7.8:
        base_quality = 0.006 + (candidate_score - 7.8) / 0.4 * (0.012 - 0.006)
    elif candidate_score >= 7.3:
        base_quality = 0.002 + (candidate_score - 7.3) / 0.5 * (0.006 - 0.002)
    elif candidate_score >= 7.0:
        base_quality = (candidate_score - 7.0) / 0.3 * 0.002
    else:
        if candidate_score >= 6.8:
            low_penalty = (7.0 - candidate_score) / 0.2 * -0.010
        elif candidate_score >= 6.3:
            low_penalty = -0.010 + (6.8 - candidate_score) / 0.5 * (-0.050 - -0.010)
        elif candidate_score >= 5.8:
            low_penalty = -0.050 + (6.3 - candidate_score) / 0.5 * (-0.100 - -0.050)
        else:
            low_penalty = -0.100 + max(-0.050, (5.8 - candidate_score) / 0.8 * -0.050)
        # Smooth cosine attenuation rather than a hard step cliff at 0.55
        cosine_factor = max(0.0, min(1.0, (0.55 - dense_cosine) / 0.10)) if dense_cosine >= 0.45 else 1.0
        base_quality = low_penalty * cosine_factor

    return base_quality


GENERIC_BACKDROP_THEMES: Final[frozenset[Theme]] = SETTING_BACKDROP_THEMES | frozenset({Theme.ISEKAI})


SPORTS_THEMES: Final[frozenset[Theme]] = frozenset(
    {
        Theme.TEAM_SPORTS,
        Theme.COMBAT_SPORTS,
        Theme.RACING,
    }
)


def compute_path_reliability_multiplier(
    retrieval_paths: Sequence[str] | frozenset[str],
    base_score: float,
    *,
    source_genres: frozenset[Genre] = frozenset(),
    candidate_genres: frozenset[Genre] = frozenset(),
    source_themes: frozenset[Theme] = frozenset(),
    candidate_themes: frozenset[Theme] = frozenset(),
    shared_themes: frozenset[Theme] = frozenset(),
    shared_hook_tags_count: int = 0,
    dense_cosine: float = 0.50,
    is_sparse_anchor: bool = False,
) -> float:
    paths = frozenset(retrieval_paths)
    multiplier = 1.0

    if paths == frozenset({'themes'}) or paths == frozenset({'lsa', 'themes'}):
        multiplier *= 0.85
    elif paths == frozenset({'genres'}) or paths == frozenset({'lsa'}) or paths.issubset({'themes', 'genres'}):
        multiplier *= 0.88

    if 'weighted-v2' in paths and 'embedding' in paths:
        multiplier *= 1.02
    if paths == frozenset({'embedding'}) and base_score >= 0.28:
        multiplier *= 1.05

    if (
        shared_themes
        and shared_themes.issubset(GENERIC_BACKDROP_THEMES)
        and shared_hook_tags_count == 0
        and dense_cosine < 0.38
    ):
        multiplier *= 0.80

    if source_themes and candidate_themes:
        substantive_source_themes = source_themes - GENERIC_BACKDROP_THEMES
        if (
            substantive_source_themes
            and candidate_themes.intersection(GENERIC_BACKDROP_THEMES)
            and not candidate_themes.intersection(substantive_source_themes)
            and dense_cosine < 0.72
        ):
            multiplier *= 0.70

    if Genre.SPORTS in source_genres:
        is_candidate_sports = Genre.SPORTS in candidate_genres or bool(candidate_themes.intersection(SPORTS_THEMES))
        if not is_candidate_sports and dense_cosine < 0.70:
            multiplier *= 0.80

    if shared_hook_tags_count == 0 and dense_cosine < 0.35:
        multiplier *= 0.65

    if len(paths) <= 1 and dense_cosine < 0.40 and not (is_sparse_anchor and dense_cosine >= 0.35):
        multiplier *= 0.88

    if shared_hook_tags_count >= 4:
        multiplier *= 1.08
    elif shared_hook_tags_count >= 2:
        multiplier *= 1.05

    return multiplier


def compute_metadata_multiplier(
    anchor: AnimePostRankingMetadata,
    candidate: AnimePostRankingMetadata,
    *,
    dense_cosine: float = 0.50,
    shared_hooks_count: int = 0,
) -> float:
    """Compute the combined bounded metadata multiplier with unified format commitment."""
    delta_audience = compute_audience_adjustment(anchor, candidate) * WEIGHT_AUDIENCE
    delta_commitment = compute_format_commitment_adjustment(anchor, candidate) * WEIGHT_FORMAT_COMMITMENT
    delta_studio = (
        compute_studio_adjustment(
            anchor,
            candidate,
            dense_cosine=dense_cosine,
            shared_hooks_count=shared_hooks_count,
        )
        * WEIGHT_STUDIO
    )

    raw_quality = compute_quality_adjustment(anchor, candidate, dense_cosine=dense_cosine)
    if raw_quality > 0.0:
        if dense_cosine < 0.38 and shared_hooks_count < 2:
            qual_factor = max(0.0, (dense_cosine - 0.20) / (0.38 - 0.20))
            raw_quality *= qual_factor
        elif dense_cosine < 0.46 and shared_hooks_count == 0:
            qual_factor = max(0.0, (dense_cosine - 0.38) / (0.46 - 0.38))
            raw_quality *= qual_factor

    delta_quality = raw_quality * WEIGHT_QUALITY
    if candidate.is_award_winning and dense_cosine >= 0.45:
        delta_quality += 0.005 * WEIGHT_QUALITY

    delta_meta = delta_audience + delta_commitment + delta_studio + delta_quality
    unclipped = 1.0 + MULTIPLIER_SCALE * delta_meta
    multiplier = max(MIN_MULTIPLIER_BOUND, min(MAX_MULTIPLIER_BOUND, unclipped))

    anchor_demographics = anchor.demographics or (
        (anchor.demographic,) if anchor.demographic not in ('Missing', 'Multiple') else ()
    )
    is_anchor_children = normalize_rating(anchor.rating) in (RatingClass.G, RatingClass.PG) or any(
        parse_demographic(demographic) == Demographic.KIDS for demographic in anchor_demographics
    )
    is_candidate_mature_adult = normalize_rating(candidate.rating) in (
        RatingClass.R,
        RatingClass.R_PLUS,
        RatingClass.R_X,
    )
    if is_anchor_children and is_candidate_mature_adult:
        multiplier = min(multiplier, 0.10)

    return multiplier


# Curated episode overrides for perpetual multi-decade broadcast institutions
# whose MAL episodes property is null due to their indefinite ongoing status.
KNOWN_PERPETUAL_BROADCAST_EPISODES: Final[dict[int, int]] = {
    21: 1120,  # One Piece (1999~)
    235: 1140,  # Meitantei Conan (1996~)
    966: 1250,  # Crayon Shin-chan (1992~)
    1199: 2400,  # Nintama Rantarou (1993~)
    1960: 1650,  # Sore Ike! Anpanman (1988~)
    2406: 2700,  # Sazae-san (1969~)
    4459: 2000,  # Ojarumaru (1998~)
    6149: 1450,  # Chibi Maruko-chan (1995~)
    8336: 800,  # Hanakappa (2010~)
    8687: 1350,  # Doraemon (2005~)
    18941: 650,  # Shimajirou no Wow! (2012~)
}


def estimate_catalogue_episodes(
    raw_episodes: int | None,
    anime_type: str | None,
    anime_id: int | None = None,
) -> int:
    """Accurately resolve episode count without arbitrary linear year multiplication.

    For perpetual multi-decade giants (One Piece, Detective Conan), uses curated verified
    broadcast counts. For all other titles with missing episodes, uses standard format defaults:
    - MOVIE: 1 episode
    - TV: 12 episodes (standard 1-cour seasonal broadcast)
    - ONA / OVA / Special: 1 episode
    """
    if raw_episodes is not None and raw_episodes > 0:
        return raw_episodes
    if anime_id is not None and anime_id in KNOWN_PERPETUAL_BROADCAST_EPISODES:
        return KNOWN_PERPETUAL_BROADCAST_EPISODES[anime_id]
    normalized_type = (anime_type or 'TV').strip().upper()
    if normalized_type == AnimeType.MOVIE:
        return 1
    if normalized_type == AnimeType.TV:
        return 12
    return 1


def estimate_catalogue_duration_minutes(
    raw_duration: int | None,
    anime_type: str | None,
) -> int:
    """Estimate duration minutes when raw duration is missing."""
    if raw_duration is not None and raw_duration > 0:
        return raw_duration
    normalized_type = (anime_type or 'TV').strip().upper()
    if normalized_type == AnimeType.MOVIE:
        return 90
    if normalized_type == AnimeType.TV:
        return 24
    if normalized_type == AnimeType.ONA:
        return 15
    return 24


def build_mainline_runtime_index(
    frame: pl.DataFrame,
    relations_frame: pl.DataFrame | None = None,
) -> tuple[Mapping[int, float], Mapping[int, int]]:
    """Compute total mainline continuity runtime (minutes) and episodes for each anime.

    Only traverses edges where relation_type is in ('Sequel', 'Parent Story', 'Full Story', 'Prequel')
    and same_story_intent == 'continuation'. Remakes, spin-offs, and alternative settings
    are not merged.
    """
    item_runtime: dict[int, float] = {}
    item_episodes: dict[int, int] = {}
    anime_ids = frame.get_column('mal_id').to_list()
    episodes_column = frame.get_column('episodes').to_list() if 'episodes' in frame.columns else [None] * len(anime_ids)
    types_column = (
        frame.get_column('anime_type').to_list() if 'anime_type' in frame.columns else [None] * len(anime_ids)
    )
    durations_column = (
        frame.get_column('duration_minutes').to_list()
        if 'duration_minutes' in frame.columns
        else [None] * len(anime_ids)
    )
    for anime_id, raw_episodes, raw_type, raw_duration_minutes in zip(
        anime_ids, episodes_column, types_column, durations_column, strict=True
    ):
        episodes = estimate_catalogue_episodes(
            raw_episodes,
            raw_type,
            anime_id=anime_id,
        )
        duration_minutes = estimate_catalogue_duration_minutes(
            raw_duration_minutes,
            raw_type,
        )
        item_runtime[anime_id] = float(episodes * duration_minutes)
        item_episodes[anime_id] = int(episodes)

    if relations_frame is None or relations_frame.is_empty():
        return item_runtime, item_episodes

    mainline_df = relations_frame.filter(
        pl.col('relation_type').is_in(list(MAINLINE_RELATION_TYPES))
        & (pl.col('same_story_intent') == MAINLINE_CONTINUATION_INTENT)
    )

    adjacency: dict[int, list[int]] = {anime_id: [] for anime_id in item_runtime}
    for source_id, target_id in zip(
        mainline_df.get_column('source_id').to_list(),
        mainline_df.get_column('target_id').to_list(),
        strict=True,
    ):
        if source_id in adjacency and target_id in adjacency:
            adjacency[source_id].append(target_id)
            adjacency[target_id].append(source_id)

    mainline_runtimes: dict[int, float] = {}
    mainline_episodes: dict[int, int] = {}
    visited: set[int] = set()
    for start_id in adjacency:
        if start_id in visited:
            continue
        component: list[int] = []
        stack = [start_id]
        visited.add(start_id)
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        comp_runtime = sum(item_runtime[m] for m in component)
        comp_episodes = sum(item_episodes[m] for m in component)
        for m in component:
            mainline_runtimes[m] = comp_runtime
            mainline_episodes[m] = comp_episodes

    return mainline_runtimes, mainline_episodes


def extract_post_ranking_metadata(
    frame: pl.DataFrame,
    mainline_runtimes: Mapping[int, float],
    storyline_episodes_by_id: Mapping[int, int] | None = None,
) -> Mapping[int, AnimePostRankingMetadata]:
    """Build fast metadata lookup records for all catalogue items."""
    records: dict[int, AnimePostRankingMetadata] = {}
    storyline_episodes = storyline_episodes_by_id or {}
    anime_ids = frame.get_column('mal_id').to_list()
    row_count = len(anime_ids)

    def _column_values(name: str) -> list[object]:
        return frame.get_column(name).to_list() if name in frame.columns else [None] * row_count

    for (
        anime_id,
        demographics,
        raw_studios,
        raw_rating,
        raw_type,
        year,
        score,
        raw_episodes,
        raw_duration_minutes,
        raw_genres,
    ) in zip(
        anime_ids,
        _column_values('demographics'),
        _column_values('studios'),
        _column_values('rating'),
        _column_values('anime_type'),
        _column_values('year'),
        _column_values('score'),
        _column_values('episodes'),
        _column_values('duration_minutes'),
        _column_values('genres'),
        strict=True,
    ):
        demographics_tuple = tuple(demographics) if demographics else ()
        studios_tuple = tuple(raw_studios) if raw_studios else ()
        demographic_label = normalize_demographic(demographics)
        rating_label = normalize_rating_label(raw_rating)
        anime_type = raw_type or 'TV'
        episodes = estimate_catalogue_episodes(
            raw_episodes,
            anime_type,
            anime_id=anime_id,
        )
        storyline_episode_count = storyline_episodes.get(anime_id, episodes)
        duration_minutes = estimate_catalogue_duration_minutes(raw_duration_minutes, anime_type)
        fallback_runtime_minutes = float(episodes * duration_minutes)
        mainline_runtime_minutes = mainline_runtimes.get(anime_id, fallback_runtime_minutes)
        genres_list = raw_genres or ()
        is_award = any(
            g == Genre.AWARD_WINNING or str(g).strip().lower().replace(' ', '_') == Genre.AWARD_WINNING.value
            for g in genres_list
        )

        records[anime_id] = AnimePostRankingMetadata(
            anime_id=anime_id,
            anime_type=anime_type,
            demographic=demographic_label,
            rating=rating_label,
            year=year,
            score=score,
            mainline_runtime_minutes=mainline_runtime_minutes,
            demographics=demographics_tuple,
            studios=studios_tuple,
            episodes=episodes,
            storyline_episodes=storyline_episode_count,
            duration_minutes=duration_minutes,
            is_award_winning=is_award,
        )
    return records
