"""Validation and export of completed recommendation chunks."""

from collections.abc import Sequence
from pathlib import Path

from export.catalogue import CatalogueProjections, write_catalogue_artifacts
from export.contracts import FrontendProvenance, RecommendationChunkManifest
from export.manifest import validate_recommendation_manifest
from fetch.contracts import TenraiAnimeEntry
from processing.contracts import CanonicalAnime
from storage.json_io import read_json

MIN_RECOMMENDATION_BATCH_SIZE = 50
MAX_RECOMMENDATION_BATCH_SIZE = 1_000


def export_catalogue_stage(
    records: Sequence[CanonicalAnime],
    full_entries: Sequence[TenraiAnimeEntry],
    *,
    recommendation_path: Path,
    output_dir: Path,
    provenance: FrontendProvenance,
    featured_paths: Sequence[Path] = (),
    projections: CatalogueProjections | None = None,
) -> None:
    """Build frontend artifacts from complete, checksummed recommendation chunks."""
    manifest = read_json(recommendation_path / 'manifest.json', RecommendationChunkManifest)
    if manifest.schema_version != 'recommendation-chunks-v5':
        raise ValueError('recommendation manifest does not contain production ID chunks')
    validate_recommendation_manifest(
        manifest,
        tuple(record.mal_id for record in records),
        recommendation_path,
        min_chunk_size=MIN_RECOMMENDATION_BATCH_SIZE,
        max_chunk_size=MAX_RECOMMENDATION_BATCH_SIZE,
    )
    write_catalogue_artifacts(
        records,
        full_entries=full_entries,
        recommendation_chunks=recommendation_path,
        provenance=provenance,
        output_dir=output_dir,
        featured_paths=featured_paths,
        projections=projections,
    )
