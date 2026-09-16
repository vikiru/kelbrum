"""Validated feature assembly configuration."""

from enum import StrEnum

import msgspec

from features.constants import (
    DEFAULT_DURATION_BOUNDARIES,
    DEFAULT_EPISODE_BOUNDARIES,
    DEFAULT_SCORE_BOUNDARIES,
    DEFAULT_YEAR_BOUNDARIES,
)
from normalization.policy import MissingPolicy

_NGRAM_RANGE_LENGTH = 2


def _default_numeric_transforms() -> dict[str, tuple[str, ...]]:
    return {
        'year': ('minmax',),
        'episodes': ('log1p', 'robust'),
        'duration_minutes': ('robust',),
        'score': ('minmax',),
    }


class EmbeddingSource(StrEnum):
    """Identify where an embedding model is resolved from."""

    LOCAL = 'local'
    REMOTE = 'remote'


class EmbeddingModel(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Describe one embedding model without ambiguous path and boolean flags."""

    source: EmbeddingSource
    identifier: str
    revision: str | None = None

    def __post_init__(self) -> None:
        """Reject empty model references and invalid revision combinations."""
        if not self.identifier.strip():
            raise ValueError('embedding model identifier cannot be empty')
        if self.source is EmbeddingSource.LOCAL and self.revision is not None:
            raise ValueError('local embedding models do not accept a remote revision')

    @property
    def local_only(self) -> bool:
        """Return whether model loading must stay on the local filesystem."""
        return self.source is EmbeddingSource.LOCAL


class FeatureConfig(msgspec.Struct, frozen=True):
    """Behavioral choices that identify a feature bundle."""

    embedding: EmbeddingModel | None = None
    source_snapshot_id: str | None = None
    include_studios: bool = False
    include_quality_features: bool = False
    include_bm25: bool = False
    include_lsa: bool = False
    include_nmf: bool = False
    synopsis_ngram_range: tuple[int, int] = (1, 2)
    synopsis_sublinear_tf: bool = True
    synopsis_stop_words: str | None = 'english'
    synopsis_min_df: int = 2
    synopsis_max_df: float = 0.95
    synopsis_max_features: int = 5_000
    latent_dimensions: int = 200
    latent_max_iter: int = 200
    numeric_missing_policy: MissingPolicy = MissingPolicy.MEDIAN
    numeric_transforms: dict[str, tuple[str, ...]] = msgspec.field(default_factory=_default_numeric_transforms)
    year_boundaries: tuple[int, ...] = DEFAULT_YEAR_BOUNDARIES
    episode_boundaries: tuple[int, ...] = DEFAULT_EPISODE_BOUNDARIES
    duration_boundaries: tuple[int, ...] = DEFAULT_DURATION_BOUNDARIES
    score_boundaries: tuple[int, ...] = DEFAULT_SCORE_BOUNDARIES

    def __post_init__(self) -> None:
        boundaries_by_property = (
            self.year_boundaries,
            self.episode_boundaries,
            self.duration_boundaries,
            self.score_boundaries,
        )
        for boundaries in boundaries_by_property:
            if not boundaries or tuple(sorted(set(boundaries))) != boundaries:
                raise ValueError('bucket boundaries must be sorted, unique, and non-empty')
        if self.synopsis_min_df < 1 or self.synopsis_max_features < 1:
            raise ValueError('synopsis limits must be positive')
        if not 0.0 < self.synopsis_max_df <= 1.0 or self.latent_dimensions < 1 or self.latent_max_iter < 1:
            raise ValueError('invalid synopsis configuration')
        self._validate_numeric_transforms(self.numeric_transforms)
        ngram_range = self.synopsis_ngram_range
        if len(ngram_range) != _NGRAM_RANGE_LENGTH or ngram_range[0] < 1 or ngram_range[0] > ngram_range[1]:
            raise ValueError('synopsis ngram range must be an ordered positive pair')

    @staticmethod
    def _validate_numeric_transforms(transforms: dict[str, tuple[str, ...]]) -> None:
        supported = {'minmax', 'standard', 'robust', 'maxabs', 'log1p'}
        numeric_columns = {'year', 'episodes', 'duration_minutes', 'score'}
        unknown_columns = set(transforms) - numeric_columns
        if unknown_columns:
            raise ValueError(f'unsupported numeric columns: {", ".join(sorted(unknown_columns))}')
        if unknown := {name for steps in transforms.values() for name in steps} - supported:
            raise ValueError(f'unsupported numeric transforms: {", ".join(sorted(unknown))}')
