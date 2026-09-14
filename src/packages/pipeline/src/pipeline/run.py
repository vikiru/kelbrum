"""Thin orchestration for feature and recommendation artifacts."""

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from gc import collect
from hashlib import sha256
from pathlib import Path

import msgspec
import numpy as np
import polars as pl

from anime_catalogue import order_catalogue_frame
from config import (
    bind_logger,
    canonical_dir,
    embedding_cache_dir,
    frontend_data_dir,
    intermediate_dir,
    tenrai_checkpoint_path,
    tenrai_full_path,
    tenrai_profile_full_path,
    tenrai_profile_snapshot_path,
    tenrai_r_plus_checkpoint_path,
    tenrai_r_plus_full_path,
    tenrai_r_plus_snapshot_path,
    tenrai_snapshot_path,
)
from export.frontend import write_catalogue_artifacts, write_featured_artifacts
from features.assemble import assemble_features
from features.blocks import FeatureBundle
from features.config import FeatureConfig
from features.manual_theme_corrections import MANUAL_THEME_ADDITIONS
from features.synopsis import LatentConfig, TfidfConfig
from features.tag_assignment import MANUAL_TAG_ASSIGNMENTS
from fetch.client import TenraiClient
from fetch.filters import CatalogueFilters
from models.contracts import (
    PipelineManifest,
    RecommendationConfig,
    RecommendationItem,
    RecommendationResult,
)
from models.tenrai import CanonicalAnime, TenraiAnimeEntry
from pipeline.input_stages import load_or_enrich, load_or_fetch, validate_entrypoint_pair
from pipeline.recommendation_chunks import DEFAULT_BATCH_SIZE, write_recommendation_chunks
from pipeline.recommendation_export import export_catalogue_stage
from pipeline.relationship_cache import load_or_build_relationship_graph
from processing.build import canonical_frame, load_canonical_parquet, process_snapshot
from processing.constants import PROCESSING_AUDIT_SCHEMA_VERSION
from processing.eligibility import EligibilityPolicy
from recommender.frozen_pipeline import RECOMMENDER_POLICY_VERSION, Recommender
from recommender.relationship_graph import RelationshipIndex
from storage.arrays import read_array
from storage.json_io import read_json, write_json

DEFAULT_RECOMMENDATION_BATCH_SIZE = DEFAULT_BATCH_SIZE
DEFAULT_CATALOGUE_BATCH_SIZE = 1_000
log = bind_logger(package='pipeline')


class CatalogueProfilePaths(msgspec.Struct, frozen=True):
    """Resolved source paths and request filters for one catalogue profile."""

    snapshot: Path
    checkpoint: Path
    full_artifact: Path
    filters: CatalogueFilters


class PipelineRun(msgspec.Struct, frozen=True):
    features: FeatureBundle
    recommender: Recommender
    manifest: PipelineManifest
    same_story_relations: Mapping[int, Sequence[tuple[int, str]]]

    def recommend(
        self,
        source_anime_id: int,
        *,
        config: RecommendationConfig,
        fetched_date: str,
    ) -> RecommendationResult:
        return RecommendationResult(
            source_anime_id,
            self.recommender.recommend(source_anime_id, limit=config.limit),
            fetched_date,
        )

    def search_recommendations(
        self, source_anime_id: int, query: int | str, *, limit: int = 10
    ) -> tuple[RecommendationItem, ...]:
        """Search one source's ranked recommendations by ID or title."""
        return self.recommender.search_recommendations(source_anime_id, query, limit=limit)


def _load_aligned_embedding_cache(
    cache_path: Path | None,
    row_count: int,
    ordered_ids: Sequence[int] | None = None,
) -> np.ndarray | None:
    """Load an existing embedding artifact without invoking the model encoder."""
    if cache_path is None or not cache_path.is_file():
        return None
    manifest_path = cache_path.with_suffix(cache_path.suffix + '.manifest.json')
    if not manifest_path.is_file():
        return None
    manifest = read_json(manifest_path, dict[str, object])
    if manifest.get('row_count') != row_count:
        return None
    if ordered_ids is not None:
        expected_ids_hash = sha256(msgspec.json.encode([int(value) for value in ordered_ids])).hexdigest()
        if manifest.get('ordered_mal_ids_hash') != expected_ids_hash:
            return None
    values = np.asarray(read_array(cache_path), dtype=np.float32)
    if values.ndim != 2 or values.shape[0] != row_count:
        raise ValueError(f'embedding cache is not aligned with the catalogue: {cache_path}')
    return values


def _find_aligned_embedding_cache(snapshot_id: str, ordered_ids: Sequence[int]) -> Path | None:
    """Find a derived embedding cache whose manifest matches the current catalogue order."""
    candidates = [embedding_cache_dir() / f'{snapshot_id}.npy']
    candidates.extend(sorted(path for path in embedding_cache_dir().glob('*.npy') if path not in candidates))
    for candidate in candidates:
        if _load_aligned_embedding_cache(candidate, len(ordered_ids), ordered_ids) is not None:
            return candidate
    return None


def build_pipeline(
    frame: pl.DataFrame,
    *,
    feature_config: FeatureConfig,
    fetched_date: str,
    same_story_relations: Mapping[int, Sequence[tuple[int, str]]] | None = None,
    embedding_cache: Path | None = None,
    relationship_index: RelationshipIndex | None = None,
    source_artifact_sha256: str | None = None,
) -> PipelineRun:
    """Build all in-memory downstream artifacts from one canonical frame."""
    log.info('Building features and recommendation indexes for {} records.', frame.height)
    ordered_frame = order_catalogue_frame(frame)
    ordered_ids = tuple(int(value) for value in ordered_frame.get_column('mal_id').to_list())
    cached_embeddings = _load_aligned_embedding_cache(embedding_cache, len(ordered_frame), ordered_ids)
    bundle = assemble_features(
        ordered_frame,
        config=feature_config,
        embedding_cache=embedding_cache,
        synopsis_embedding_matrix=cached_embeddings,
        source_artifact_sha256=source_artifact_sha256,
    )
    manifest = PipelineManifest(
        schema_version='kelbrum-pipeline-v1',
        fetched_date=fetched_date,
        anime_count=bundle.anime_ids.size,
        feature_block_names=tuple(block.name for block in bundle.blocks),
        status='complete',
    )
    synopsis_tfidf_config, synopsis_latent_config = _synopsis_configs(feature_config)
    recommender = Recommender(
        ordered_frame,
        bundle,
        relationship_index=relationship_index,
        include_bm25=feature_config.include_bm25,
        include_lsa=feature_config.include_lsa,
        include_embedding=True,
        synopsis_tfidf_config=synopsis_tfidf_config,
        synopsis_latent_config=synopsis_latent_config,
    )
    log.info('Built {} feature blocks and the recommendation indexes.', len(bundle.blocks))
    return PipelineRun(bundle, recommender, manifest, same_story_relations or {})


def write_manifest(run: PipelineRun, path: str) -> None:
    """Write the completed pipeline manifest as minified JSON."""
    write_json(Path(path), run.manifest)


def build_from_snapshot(
    snapshot_path: Path,
    parquet_path: Path,
    audit_path: Path,
    *,
    snapshot_id: str,
    feature_config: FeatureConfig,
    fetched_date: str | None = None,
    full_artifact: Path | None = None,
    entrypoint_snapshot: Path | None = None,
    embedding_cache: Path | None = None,
    processing_policy: EligibilityPolicy | None = None,
) -> tuple[PipelineRun, tuple[CanonicalAnime, ...], RelationshipIndex | None]:
    """Process one accepted snapshot and build downstream in-memory indexes."""
    generated_at = fetched_date or datetime.now(UTC).isoformat()
    if full_artifact is not None:
        validate_entrypoint_pair(entrypoint_snapshot or snapshot_path, full_artifact)
    active_policy = processing_policy or EligibilityPolicy()
    log.info('Processing catalogue snapshot {}.', snapshot_id)
    records = _load_or_process_records(
        snapshot_path,
        parquet_path,
        audit_path,
        snapshot_id=snapshot_id,
        policy=active_policy,
    )
    frame = canonical_frame(records)
    log.info('Processed {} eligible catalogue records.', len(records))
    graph = None
    relations: Mapping[int, Sequence[tuple[int, str]]] = {}
    if full_artifact is not None:
        graph_artifacts = load_or_build_relationship_graph(
            full_artifact,
            canonical_dir() / f'{snapshot_id}-relationship-graph.json',
            tuple(record.mal_id for record in records),
            {record.mal_id: record.anime_type for record in records},
        )
        graph = graph_artifacts.index
        relations = graph_artifacts.relations
        log.info('Loaded the relationship graph for {} records.', len(records))
    run = build_pipeline(
        frame,
        feature_config=feature_config,
        fetched_date=generated_at,
        same_story_relations=relations,
        embedding_cache=embedding_cache
        or (
            _find_aligned_embedding_cache(snapshot_id, tuple(int(value) for value in frame['mal_id'].to_list()))
            if feature_config.embedding_model is not None
            else None
        ),
        relationship_index=graph,
        source_artifact_sha256=_sha256_file(parquet_path),
    )
    return run, records, graph


def _feature_config_identity(config: FeatureConfig) -> str:
    return msgspec.json.encode(config).decode('utf-8')


def _synopsis_configs(config: FeatureConfig) -> tuple[TfidfConfig, LatentConfig]:
    """Translate feature settings into the synopsis index configuration types."""
    return (
        TfidfConfig(
            ngram_range=config.synopsis_ngram_range,
            sublinear_tf=config.synopsis_sublinear_tf,
            stop_words=config.synopsis_stop_words,
            min_df=config.synopsis_min_df,
            max_df=config.synopsis_max_df,
            max_features=config.synopsis_max_features,
        ),
        LatentConfig(
            dimensions=config.latent_dimensions,
            max_iter=config.latent_max_iter,
        ),
    )


def _load_or_process_records(
    snapshot_path: Path,
    parquet_path: Path,
    audit_path: Path,
    *,
    snapshot_id: str,
    policy: EligibilityPolicy,
) -> tuple[CanonicalAnime, ...]:
    if parquet_path.is_file() and audit_path.is_file() and _processed_cache_matches(audit_path, snapshot_path, policy):
        return load_canonical_parquet(parquet_path)
    return process_snapshot(
        snapshot_path,
        parquet_path,
        audit_path,
        snapshot_id=snapshot_id,
        policy=policy,
        theme_additions=_theme_additions(),
        tagged_anime_ids=_tagged_anime_ids(),
    ).records


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _processed_cache_matches(audit_path: Path, source_path: Path, policy: EligibilityPolicy) -> bool:
    try:
        audit = read_json(audit_path, dict[str, object])
        return (
            audit.get('source_sha256') == _sha256_file(source_path)
            and audit.get('policy_identity')
            == msgspec.json.encode(
                {
                    'policy': policy,
                    'theme_additions': _theme_additions(),
                    'tagged_anime_ids': sorted(_tagged_anime_ids()),
                }
            ).decode('utf-8')
            and audit.get('schema_version') == PROCESSING_AUDIT_SCHEMA_VERSION
        )
    except (OSError, TypeError, ValueError):
        return False


def _theme_additions() -> dict[int, tuple[str, ...]]:
    additions: dict[int, tuple[str, ...]] = {}
    for anime_ids, themes in MANUAL_THEME_ADDITIONS:
        for anime_id in anime_ids:
            additions[anime_id] = (*additions.get(anime_id, ()), *themes)
    return additions


def _tagged_anime_ids() -> frozenset[int]:
    return frozenset(anime_id for assignment in MANUAL_TAG_ASSIGNMENTS for anime_id in assignment.anime_ids)


def write_recommendation_artifacts(
    run: PipelineRun,
    records: Sequence[CanonicalAnime],
    full_entries: Sequence[TenraiAnimeEntry],
    *,
    output_dir: Path,
    frontend_output_dir: Path,
    recommendation_config: RecommendationConfig,
    provenance: Mapping[str, object] | None = None,
    recommendation_batch_size: int = DEFAULT_RECOMMENDATION_BATCH_SIZE,
) -> None:
    """Rank the processed catalogue and write frontend-owned artifacts."""
    log.info('Generating recommendations for {} records.', len(records))
    recommendation_path = intermediate_dir() / f'{output_dir.name}-recommendations'
    resolved_provenance = dict(provenance or {})
    resolved_provenance['catalogue_fingerprint'] = sha256(
        msgspec.json.encode([msgspec.to_builtins(record) for record in records])
    ).hexdigest()
    resolved_provenance['relationship_graph_fingerprint'] = run.recommender.relationship_fingerprint
    write_recommendation_chunks(
        run.recommender,
        records,
        output_path=recommendation_path,
        recommendation_config=recommendation_config,
        source_identity=msgspec.json.encode(resolved_provenance).decode('utf-8'),
        batch_size=recommendation_batch_size,
    )
    log.info('Recommendation chunks are complete. Exporting frontend catalogue artifacts.')
    export_catalogue_stage(
        records,
        full_entries,
        recommendation_path=recommendation_path,
        output_dir=frontend_output_dir,
        provenance=resolved_provenance,
    )


def run_catalogue_pipeline(
    *,
    profile: str = 'r-plus',
    feature_config: FeatureConfig,
    recommendation_config: RecommendationConfig,
    output_dir: Path,
    snapshot_path: Path | None = None,
    checkpoint_path: Path | None = None,
    full_artifact: Path | None = None,
    overwrite_fetch: bool = False,
    recommendation_batch_size: int = DEFAULT_CATALOGUE_BATCH_SIZE,
) -> PipelineRun:
    """Run one selected catalogue profile through enrichment and artifact generation."""
    log.info('Starting the {} catalogue pipeline.', profile)
    profile_paths = _catalogue_profile_paths(profile)
    active_snapshot = snapshot_path or profile_paths.snapshot
    active_checkpoint = checkpoint_path or profile_paths.checkpoint
    active_full = full_artifact or profile_paths.full_artifact
    with TenraiClient() as client:
        log.info('Loading the catalogue snapshot and enrichment data.')
        entries = load_or_fetch(client, active_snapshot, active_checkpoint, profile_paths.filters, overwrite_fetch)
        load_or_enrich(client, entries, active_full, overwrite_fetch, profile)
        log.info('Catalogue input loading is complete.')
    del entries
    collect()
    parquet_path = output_dir / 'canonical.parquet'
    audit_path = output_dir / 'processing-audit.json'
    run, records, graph = build_from_snapshot(
        active_full,
        parquet_path,
        audit_path,
        snapshot_id=active_snapshot.stem,
        feature_config=feature_config,
        full_artifact=active_full,
        entrypoint_snapshot=active_snapshot,
    )
    output_entries = read_json(active_full, list[TenraiAnimeEntry])
    accepted_ids = {record.mal_id for record in records}
    output_entries = [entry for entry in output_entries if entry.mal_id in accepted_ids]
    processing_audit = read_json(audit_path, dict[str, object])
    write_manifest(run, str(output_dir / 'pipeline-manifest.json'))
    frontend_output_dir = frontend_data_dir()
    write_featured_artifacts(records, output_dir=frontend_output_dir, relationship_index=graph)
    log.info('Exported homepage and Top 100 artifacts.')
    write_catalogue_artifacts(
        records, full_entries=output_entries, output_dir=frontend_output_dir, include_full_entries=False
    )
    write_recommendation_artifacts(
        run,
        records,
        output_entries,
        output_dir=output_dir,
        frontend_output_dir=frontend_output_dir,
        recommendation_config=recommendation_config,
        recommendation_batch_size=recommendation_batch_size,
        provenance={
            'profile': profile,
            'source_snapshot': active_snapshot.name,
            'enrichment_snapshot': active_full.name,
            'snapshot_sha256': _sha256_file(active_snapshot),
            'enrichment_sha256': _sha256_file(active_full),
            'processed_count': len(records),
            'accepted_count': processing_audit.get('accepted_count', len(records)),
            'rejected_count': processing_audit.get('rejected_count', 0),
            'feature_config_identity': _feature_config_identity(feature_config),
            'recommendation_config_identity': msgspec.json.encode(recommendation_config).decode('utf-8'),
            'retrieval_identity': run.recommender.retrieval_identity,
            'recommender_policy_version': RECOMMENDER_POLICY_VERSION,
        },
    )
    del output_entries
    collect()
    log.info('The {} catalogue pipeline completed successfully.', profile)
    return run


def _catalogue_profile_paths(profile: str) -> CatalogueProfilePaths:
    if profile == 'r-plus':
        snapshot = tenrai_r_plus_snapshot_path()
        return CatalogueProfilePaths(
            snapshot=snapshot,
            checkpoint=tenrai_r_plus_checkpoint_path(),
            full_artifact=tenrai_r_plus_full_path(),
            filters=CatalogueFilters.r_plus_catalogue(),
        )
    if profile == 'sfw':
        snapshot = tenrai_profile_snapshot_path('sfw')
        return CatalogueProfilePaths(
            snapshot=snapshot,
            checkpoint=snapshot.with_suffix('.checkpoint.json'),
            full_artifact=tenrai_profile_full_path('sfw'),
            filters=CatalogueFilters.sfw_catalogue(),
        )
    if profile == 'default':
        return CatalogueProfilePaths(
            snapshot=tenrai_snapshot_path(),
            checkpoint=tenrai_checkpoint_path(),
            full_artifact=tenrai_full_path(),
            filters=CatalogueFilters.sfw_catalogue(),
        )
    if profile == 'all':
        snapshot = tenrai_profile_snapshot_path('all')
        return CatalogueProfilePaths(
            snapshot=snapshot,
            checkpoint=snapshot.with_suffix('.checkpoint.json'),
            full_artifact=tenrai_profile_full_path('all'),
            filters=CatalogueFilters.all_anime(),
        )
    raise ValueError(f'unsupported catalogue profile: {profile}')
