"""Explicit MiniLM model acquisition for the production feature cache."""

from pathlib import Path

from huggingface_hub import snapshot_download

from config import bind_logger, model_cache_dir, setup_logging
from features.constants import DEFAULT_EMBEDDING_MODEL


def _validate_model_directory(path: Path) -> Path:
    required_files = ('config.json', 'modules.json', 'tokenizer.json')
    weight_files = ('model.safetensors', 'pytorch_model.bin')
    missing = [name for name in required_files if not (path / name).is_file()]
    if not any((path / name).is_file() for name in weight_files):
        missing.append('model.safetensors or pytorch_model.bin')
    if missing:
        raise RuntimeError(f'Embedding model is incomplete at {path}: missing {", ".join(missing)}')
    return path


def download_minilm(destination: Path | None = None) -> Path:
    """Download MiniLM into the shared cache when explicitly requested."""
    target = destination or model_cache_dir() / 'all-MiniLM-L6-v2'
    downloaded = snapshot_download(
        repo_id=DEFAULT_EMBEDDING_MODEL,
        local_dir=target,
        allow_patterns=['*.json', '*.safetensors', '*.bin', '*.txt', '*.model'],
    )
    return _validate_model_directory(Path(downloaded))


def main() -> None:
    """Provide the root task entrypoint for explicit model acquisition."""
    setup_logging()
    bind_logger(package='features', stage='model-download').info('Embedding model available at {}', download_minilm())


if __name__ == '__main__':
    main()
