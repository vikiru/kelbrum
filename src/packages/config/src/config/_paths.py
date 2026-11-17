"""Canonical filesystem paths for the Python workspace."""

import os
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


def package_data_dir() -> Path:
    """Return the root ``data`` directory, honoring ``KELBRUM_DATA_DIR`` when set."""
    override = os.environ.get('KELBRUM_DATA_DIR')
    if override:
        stripped = override.strip()
        if stripped:
            return Path(stripped).expanduser()
    return workspace_root() / 'data'


PACKAGE_DATA_DIR = package_data_dir()
SOURCE_DATA_DIR = PACKAGE_DATA_DIR / 'source' / 'tenrai'
SOURCE_SNAPSHOT_DIR = SOURCE_DATA_DIR / 'snapshots'

PIPELINE_DIR = PACKAGE_DATA_DIR / 'pipeline'
INTERMEDIATE_DIR = PIPELINE_DIR / 'intermediate'
RESULTS_DIR = PIPELINE_DIR / 'results'
CANONICAL_DIR = PIPELINE_DIR / 'derived' / 'canonical'
MANUAL_DATA_DIR = PACKAGE_DATA_DIR / 'manual'
HUGGINGFACE_MODEL_DIR = PACKAGE_DATA_DIR / 'models' / 'huggingface'
SYNOPSIS_EMBEDDING_DIR = PACKAGE_DATA_DIR / 'embeddings' / 'synopsis'

TENRAI_SNAPSHOT_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime.json'
TENRAI_CHECKPOINT_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime.checkpoint.json'
TENRAI_FULL_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime.full.json'

TENRAI_R_PLUS_SNAPSHOT_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime-r-plus.json'
TENRAI_R_PLUS_CHECKPOINT_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime-r-plus.checkpoint.json'
TENRAI_R_PLUS_FULL_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime-r-plus.full.json'

TENRAI_SFW_SNAPSHOT_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime-sfw.json'
TENRAI_SFW_CHECKPOINT_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime-sfw.checkpoint.json'
TENRAI_SFW_FULL_PATH = SOURCE_SNAPSHOT_DIR / 'tenrai-anime-sfw.full.json'


def _validate_profile(profile: str) -> str:
    if not profile or '/' in profile or '\\' in profile:
        raise ValueError('profile must be a non-empty path-safe name')
    return profile


def source_data_dir() -> Path:
    """Return the raw and snapshot source directory under data."""
    return package_data_dir() / 'source' / 'tenrai'


def source_snapshot_dir() -> Path:
    return source_data_dir() / 'snapshots'


def tenrai_profile_snapshot_path(profile: str) -> Path:
    """Return the sole filtered snapshot input for a named catalogue profile."""
    valid_profile = _validate_profile(profile)
    return source_snapshot_dir() / f'tenrai-anime-{valid_profile}.json'


def tenrai_profile_checkpoint_path(profile: str) -> Path:
    """Return the checkpoint path for a named catalogue profile."""
    valid_profile = _validate_profile(profile)
    return source_snapshot_dir() / f'tenrai-anime-{valid_profile}.checkpoint.json'


def tenrai_profile_full_path(profile: str) -> Path:
    """Return the enriched snapshot derived from a named catalogue profile."""
    valid_profile = _validate_profile(profile)
    return source_snapshot_dir() / f'tenrai-anime-{valid_profile}.full.json'


def tenrai_snapshot_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime.json'


def tenrai_full_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime.full.json'


def tenrai_checkpoint_path() -> Path:
    return source_snapshot_dir() / 'tenrai-anime.checkpoint.json'


def tenrai_r_plus_snapshot_path() -> Path:
    return tenrai_profile_snapshot_path('r-plus')


def tenrai_r_plus_checkpoint_path() -> Path:
    return tenrai_profile_checkpoint_path('r-plus')


def tenrai_r_plus_full_path() -> Path:
    return tenrai_profile_full_path('r-plus')


def tenrai_sfw_snapshot_path() -> Path:
    return tenrai_profile_snapshot_path('sfw')


def tenrai_sfw_checkpoint_path() -> Path:
    return tenrai_profile_checkpoint_path('sfw')


def tenrai_sfw_full_path() -> Path:
    return tenrai_profile_full_path('sfw')


def pipeline_dir() -> Path:
    return package_data_dir() / 'pipeline'


def intermediate_dir() -> Path:
    return pipeline_dir() / 'intermediate'


def results_dir() -> Path:
    return pipeline_dir() / 'results'


def canonical_dir() -> Path:
    return pipeline_dir() / 'derived' / 'canonical'


def frontend_data_dir() -> Path:
    return repository_root() / 'src' / 'frontend' / 'src' / 'data'


def manual_data_dir() -> Path:
    """Return the curated manual annotations directory."""
    return package_data_dir() / 'manual'


def model_cache_dir() -> Path:
    """Return the local Hugging Face model directory."""
    return huggingface_model_dir()


def embedding_cache_dir() -> Path:
    """Return the synopsis embedding cache directory."""
    return synopsis_embedding_dir()


def huggingface_model_dir() -> Path:
    """Return the local directory for downloaded Hugging Face models."""
    return package_data_dir() / 'models' / 'huggingface'


def huggingface_model_path(model_identifier: str) -> Path:
    """Return the structured local path for a Hugging Face model repo ID or name.

    If ``model_identifier`` has the form ``<org>/<model_name>``, the path is structured as:
    ``<huggingface_model_dir>/<org>/<model_name>``.
    If a legacy single-slug directory exists at ``<huggingface_model_dir>/<model_name>``,
    that existing path is returned for backward compatibility.
    """
    clean_identifier = model_identifier.strip()
    if '/' in clean_identifier:
        org_name, model_name = clean_identifier.split('/', 1)
        structured_target = huggingface_model_dir() / org_name / model_name
        flat_target = huggingface_model_dir() / model_name
        if flat_target.is_dir() and not structured_target.is_dir():
            return flat_target
        return structured_target
    return huggingface_model_dir() / clean_identifier


def synopsis_embedding_dir() -> Path:
    """Return the directory for catalogue-aligned synopsis embeddings."""
    return package_data_dir() / 'embeddings' / 'synopsis'
