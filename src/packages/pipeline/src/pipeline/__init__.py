"""Kelbrum pipeline package."""

from pipeline.cache_metadata import (
    CacheCompatibilityError,
    CacheMetadata,
    build_cache_metadata,
    validate_cache_metadata,
)
from pipeline.contracts import CatalogueClient, CatalogueProfilePaths, PipelineRunRequest
from pipeline.plan import PipelineInputs, PipelinePlan
from pipeline.recommendation_chunks import write_recommendation_chunks
from pipeline.recommendation_export import export_catalogue_stage
from pipeline.run import (
    PipelineRun,
    build_from_snapshot,
    build_pipeline,
    run_catalogue_pipeline,
    write_manifest,
    write_recommendation_artifacts,
)

__all__ = [
    'CacheCompatibilityError',
    'CacheMetadata',
    'CatalogueClient',
    'CatalogueProfilePaths',
    'PipelineInputs',
    'PipelinePlan',
    'PipelineRun',
    'PipelineRunRequest',
    'build_cache_metadata',
    'build_from_snapshot',
    'build_pipeline',
    'export_catalogue_stage',
    'run_catalogue_pipeline',
    'validate_cache_metadata',
    'write_manifest',
    'write_recommendation_artifacts',
    'write_recommendation_chunks',
]
