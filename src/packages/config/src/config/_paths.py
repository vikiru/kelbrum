"""Canonical filesystem paths for the Python workspace."""

from functools import cache
from pathlib import Path


@cache
def workspace_root() -> Path:
    """Return the ``src/packages`` directory containing the uv workspace marker."""
    current = Path(__file__).resolve().parent
    for parent in (current, *current.parents):
        marker = parent / 'pyproject.toml'
        if marker.is_file() and '[tool.uv.workspace]' in marker.read_text(encoding='utf-8'):
            return parent
    raise RuntimeError('Could not locate the Kelbrum Python workspace root')


def repository_root() -> Path:
    """Return the repository root containing ``src/packages``."""
    return workspace_root().parent.parent


def source_snapshot_dir() -> Path:
    return workspace_root() / 'data' / 'source' / 'tenrai' / 'snapshots'


def source_raw_snapshot_dir() -> Path:
    return workspace_root() / 'data' / 'source' / 'tenrai' / 'raw' / 'snapshots'


def tenrai_profile_snapshot_path(profile: str) -> Path:
    """Return the sole filtered snapshot input for a named catalogue profile."""
    if not profile or '/' in profile or '\\' in profile:
        raise ValueError('profile must be a non-empty path-safe name')
    return source_snapshot_dir() / f'tenrai-anime-{profile}.json'


def tenrai_profile_full_path(profile: str) -> Path:
    """Return the enriched snapshot derived from a named catalogue profile."""
    if not profile or '/' in profile or '\\' in profile:
        raise ValueError('profile must be a non-empty path-safe name')
    return source_snapshot_dir() / f'tenrai-anime-{profile}.full.json'


def tenrai_snapshot_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime.json'


def tenrai_full_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime.full.json'


def tenrai_checkpoint_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime.checkpoint.json'


def tenrai_r_plus_snapshot_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime-r-plus.json'


def tenrai_r_plus_checkpoint_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime-r-plus.checkpoint.json'


def tenrai_r_plus_full_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime-r-plus.full.json'


def intermediate_dir() -> Path:
    return workspace_root() / 'data' / 'pipeline' / 'intermediate'


def results_dir() -> Path:
    return workspace_root() / 'data' / 'pipeline' / 'results'


def canonical_dir() -> Path:
    return workspace_root() / 'data' / 'pipeline' / 'derived' / 'canonical'


def parquet_dir() -> Path:
    return workspace_root() / 'data' / 'pipeline' / 'derived' / 'parquet'


def tenrai_parquet_path() -> Path:
    return parquet_dir() / 'tenrai-anime.parquet'


def frontend_data_dir() -> Path:
    return repository_root() / 'src' / 'frontend' / 'src' / 'data'


def model_cache_dir() -> Path:
    """Return the local Hugging Face model directory."""
    return huggingface_model_dir()


def embedding_cache_dir() -> Path:
    """Return the synopsis embedding cache directory."""
    return synopsis_embedding_dir()


def huggingface_model_dir() -> Path:
    """Return the local directory for downloaded Hugging Face models."""
    return workspace_root() / 'data' / 'models' / 'huggingface'


def synopsis_embedding_dir() -> Path:
    """Return the directory for catalogue-aligned synopsis embeddings."""
    return workspace_root() / 'data' / 'embeddings' / 'synopsis'
