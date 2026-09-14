"""Shared persisted, analysis, and frontend-facing contracts."""

from typing import Literal

import msgspec

from models.tenrai import Images

MAX_RECOMMENDATIONS = 100


class FeatureFamilyAvailability(msgspec.Struct, frozen=True):
    name: str
    status: Literal['available', 'unavailable-from-source', 'disabled']


class DatasetProvenance(msgspec.Struct, frozen=True):
    profile: Literal['csv-baseline', 'tenrai-catalog', 'jikan-enriched']
    fetched_date: str
    snapshot_id: str | None = None
    schema_version: str = 'kelbrum-v2'


class RecommendationExplanation(msgspec.Struct, frozen=True):
    retrieval_paths: tuple[str, ...]
    synopsis_score: float
    tag_score: float
    theme_score: float
    genre_score: float
    demographic_score: float
    qualification_reason: Literal['evidence-consensus', 'standalone-tag']
    canonical_id: int


class RecommendationItem(msgspec.Struct, frozen=True):
    anime_id: int
    score: float
    contributions: tuple[tuple[str, float], ...]
    explanation: RecommendationExplanation | None = None


class RawRecommendation(msgspec.Struct, frozen=True):
    """Ranked candidate evidence before display or qualification policy."""

    anime_id: int
    winning_alias_id: int
    score: float
    retrieval_paths: tuple[str, ...]
    semantic_available: bool
    categorical_available: bool


class RecommendationScore(msgspec.Struct, frozen=True):
    """Frontend-safe score projection for one surfaced recommendation."""

    anime_id: int = msgspec.field(name='animeId')
    score: float


class RecommendationResult(msgspec.Struct, frozen=True):
    source_anime_id: int
    items: tuple[RecommendationItem, ...]
    fetched_date: str


class PipelineManifest(msgspec.Struct, frozen=True):
    schema_version: str
    fetched_date: str
    anime_count: int
    feature_block_names: tuple[str, ...]
    status: Literal['complete']


class RecommendationConfig(msgspec.Struct, frozen=True):
    limit: int = 100

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= MAX_RECOMMENDATIONS:
            raise ValueError('recommendation limit must be between 1 and 100')


class LegacySimilarityConfig(msgspec.Struct, frozen=True):
    """Controls the deprecated combined-vector similarity index."""

    limit: int = 100
    minimum_score: float = 0.20
    backend: Literal['exact', 'knn'] = 'knn'
    require_semantic: bool = True

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= MAX_RECOMMENDATIONS:
            raise ValueError('recommendation limit must be between 1 and 100')
        if not 0.0 <= self.minimum_score <= 1.0:
            raise ValueError('minimum_score must be between 0 and 1')


class AnimeMetadata(msgspec.Struct, frozen=True):
    mal_id: int = msgspec.field(name='malId')
    title: str
    title_english: str | None = msgspec.field(name='titleEnglish', default=None)
    title_japanese: str | None = msgspec.field(name='titleJapanese', default=None)
    images: Images | None = None
    year: int | None = None
    score: float | None = None

    def __post_init__(self) -> None:
        if self.mal_id <= 0:
            raise ValueError('mal_id must be positive')


class AnimeCardMetadata(msgspec.Struct, frozen=True):
    mal_id: int = msgspec.field(name='malId')
    title: str
    title_english: str | None = msgspec.field(name='titleEnglish', default=None)
    title_japanese: str | None = msgspec.field(name='titleJapanese', default=None)
    images: Images | None = None
    year: int | None = None
    score: float | None = None

    def __post_init__(self) -> None:
        if self.mal_id <= 0:
            raise ValueError('mal_id must be positive')


class AnimeDetail(msgspec.Struct, frozen=True):
    mal_id: int = msgspec.field(name='malId')
    title: str
    title_english: str | None = msgspec.field(name='titleEnglish', default=None)
    images: Images | None = None
    year: int | None = None
    score: float | None = None
    synopsis: str | None = None
    episodes: int | None = None
    duration_minutes: int | None = msgspec.field(name='durationMinutes', default=None)
    cluster_num: int | None = msgspec.field(name='clusterNum', default=None)
    recommendations: tuple[int, ...] = ()
    recommendation_scores: tuple[RecommendationScore, ...] = msgspec.field(name='recommendationScores', default=())

    def __post_init__(self) -> None:
        if self.mal_id <= 0:
            raise ValueError('mal_id must be positive')
        if len(self.recommendations) > MAX_RECOMMENDATIONS:
            raise ValueError('recommendations cannot exceed 100 IDs')
        if len(self.recommendation_scores) > MAX_RECOMMENDATIONS:
            raise ValueError('recommendationScores cannot exceed 100 items')
