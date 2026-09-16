"""Pipeline-owned run and artifact contracts."""

from collections.abc import Sequence
from pathlib import Path
from typing import Literal, Protocol

import msgspec

from features.config import EmbeddingModel
from fetch.contracts import TenraiAnimeEntry
from fetch.filters import CatalogueFilters
from pipeline.plan import PipelinePlan
from processing.eligibility import EligibilityPolicy
from recommender.contracts import RecommendationConfig


class CatalogueProfilePaths(msgspec.Struct, frozen=True):
    """Explicit source paths and filters for one catalogue profile."""

    snapshot: Path
    checkpoint: Path
    full_artifact: Path
    filters: CatalogueFilters


class CatalogueClient(Protocol):
    """Minimal fetch port required by pipeline input orchestration."""

    def catalogue(
        self,
        *,
        filters: CatalogueFilters,
        checkpoint_path: Path,
        entries_path: Path,
        overwrite: bool,
    ) -> list[TenraiAnimeEntry]: ...

    def enrich(
        self,
        anime_ids: Sequence[int],
        output_path: Path,
        *,
        overwrite: bool,
        profile: str | None,
    ) -> Sequence[TenraiAnimeEntry]: ...


class PipelineRunRequest(msgspec.Struct, frozen=True):
    """Group operational inputs for one complete catalogue pipeline run."""

    client: CatalogueClient
    profile: str
    profile_paths: CatalogueProfilePaths
    pipeline_plan: PipelinePlan
    recommendation_config: RecommendationConfig
    output_dir: Path
    frontend_output_dir: Path
    embedding_cache: Path | None
    relationship_graph_path: Path | None
    recommendation_path: Path
    processing_policy: EligibilityPolicy | None = None
    overwrite_fetch: bool = False
    recommendation_batch_size: int = 1_000
    run_id: str | None = None


class PipelineManifest(msgspec.Struct, frozen=True):
    schema_version: str
    fetched_date: str
    anime_count: int
    feature_block_names: tuple[str, ...]
    status: Literal['complete']


class EmbeddingCacheManifest(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Typed identity and alignment contract for one embedding matrix."""

    schema_version: str
    model: EmbeddingModel
    row_count: int
    text_hash: str
    ordered_ids_hash: str
    source_snapshot_id: str | None
    source_artifact_sha256: str | None
    row_keys: tuple[str, ...]
    generated_at: str = ''
