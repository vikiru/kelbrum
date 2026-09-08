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
from config.logger import bind_logger, setup_logging
from config.settings import Settings

__all__ = [
    'Settings',
    'bind_logger',
    'canonical_dir',
    'embedding_cache_dir',
    'frontend_data_dir',
    'huggingface_model_dir',
    'intermediate_dir',
    'model_cache_dir',
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
    'workspace_root',
]
