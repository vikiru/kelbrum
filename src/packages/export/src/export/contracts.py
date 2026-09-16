"""Frontend-owned projections and recommendation display contracts."""

from collections.abc import Mapping

import msgspec

from fetch.contracts import Images


class RecommendationChunkManifest(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Typed checkpoint contract for resumable recommendation chunks."""

    schema_version: str
    identity: str
    configuration_fingerprint: str
    chunk_size: int
    expected_chunks: int
    chunk_ids: Mapping[str, tuple[int, ...]]
    completed_chunks: tuple[int, ...]
    checksums: Mapping[str, str]
    generated_at: str


class FrontendArtifactFile(msgspec.Struct, frozen=True):
    """Integrity metadata for one generated frontend file."""

    bytes: int
    path: str
    sha256: str


class FrontendProvenance(msgspec.Struct, frozen=True, forbid_unknown_fields=True):
    """Typed identities and counts used to explain one frontend export."""

    profile: str
    source_snapshot: str
    enrichment_snapshot: str
    snapshot_sha256: str
    enrichment_sha256: str
    processed_count: int
    accepted_count: int
    rejected_count: int
    feature_config_identity: str
    recommendation_config_identity: str
    retrieval_identity: str
    union_identity: str
    ranking_identity: str
    recommender_policy_identity: str
    catalogue_fingerprint: str = ''
    relationship_graph_fingerprint: str = ''


class FrontendArtifactManifest(msgspec.Struct, frozen=True):
    """Complete typed manifest for one frontend export."""

    schema_version: str
    generated_at: str
    metadata_count: int
    full_entry_count: int
    recommendation_source_count: int
    metadata_files: tuple[str, ...]
    full_files: tuple[str, ...]
    files: tuple[FrontendArtifactFile, ...]
    search_metadata: str
    search_metadata_chunks: tuple[str, ...]
    build_identity: str
    provenance: Mapping[str, object]


class AnimeCardMetadata(msgspec.Struct, frozen=True):
    """Card-sized metadata contract for featured frontend entries."""

    mal_id: int = msgspec.field(name='malId')
    title: str
    title_english: str | None = msgspec.field(name='titleEnglish', default=None)
    title_japanese: str | None = msgspec.field(name='titleJapanese', default=None)
    images: Images | None = None
    year: int | None = None
    score: float | None = None

    def __post_init__(self) -> None:
        """Reject frontend cards that cannot be addressed by a positive anime ID."""
        if self.mal_id <= 0:
            raise ValueError('mal_id must be positive')
