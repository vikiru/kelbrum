"""Shared Kelbrum workspace configuration and logging."""

from config._paths import (
    canonical_dir,
    embedding_cache_dir,
    frontend_data_dir,
    huggingface_model_dir,
    intermediate_dir,
    model_cache_dir,
    results_dir,
    synopsis_embedding_dir,
    tenrai_checkpoint_path,
    tenrai_full_path,
    tenrai_parquet_path,
    tenrai_profile_full_path,
    tenrai_profile_snapshot_path,
    tenrai_r_plus_checkpoint_path,
    tenrai_r_plus_full_path,
    tenrai_r_plus_snapshot_path,
    tenrai_snapshot_path,
    workspace_root,
)
from config.events import LogEvent, emit_event, peak_memory_mb, timed_event
from config.identity import IdentityInputs, derive_identity, derive_payload_identity, derive_stage_identity
from config.logger import bind_logger, setup_logging
from config.settings import Settings

__all__ = [
    'IdentityInputs',
    'LogEvent',
    'Settings',
    'bind_logger',
    'canonical_dir',
    'derive_identity',
    'derive_payload_identity',
    'derive_stage_identity',
    'embedding_cache_dir',
    'emit_event',
    'frontend_data_dir',
    'huggingface_model_dir',
    'intermediate_dir',
    'model_cache_dir',
    'peak_memory_mb',
    'results_dir',
    'setup_logging',
    'synopsis_embedding_dir',
    'tenrai_checkpoint_path',
    'tenrai_full_path',
    'tenrai_parquet_path',
    'tenrai_profile_full_path',
    'tenrai_profile_snapshot_path',
    'tenrai_r_plus_checkpoint_path',
    'tenrai_r_plus_full_path',
    'tenrai_r_plus_snapshot_path',
    'tenrai_snapshot_path',
    'timed_event',
    'workspace_root',
]
