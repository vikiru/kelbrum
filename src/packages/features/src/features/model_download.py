"""Explicit embedding model acquisition for the production feature cache."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from huggingface_hub import snapshot_download

from config import Settings, bind_logger, huggingface_model_path, setup_logging
from features.constants import DEFAULT_EMBEDDING_MODEL

if TYPE_CHECKING:
    from collections.abc import Sequence


def _validate_model_directory(path: Path) -> Path:
    required_files = ('config.json', 'modules.json', 'tokenizer.json')
    weight_files = ('model.safetensors', 'pytorch_model.bin')
    missing = [name for name in required_files if not (path / name).is_file()]
    if not any((path / name).is_file() for name in weight_files):
        missing.append('model.safetensors or pytorch_model.bin')
    if missing:
        raise RuntimeError(f'Embedding model is incomplete at {path}: missing {", ".join(missing)}')
    return path


def download_embedding_model(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    destination: Path | None = None,
) -> Path:
    """Download the production embedding model into the shared cache."""
    target = destination or huggingface_model_path(model_name)
    downloaded = snapshot_download(
        repo_id=model_name,
        local_dir=target,
        allow_patterns=['*.json', '*.safetensors', '*.bin', '*.txt', '*.model'],
    )
    return _validate_model_directory(Path(downloaded))


def download_minilm(destination: Path | None = None) -> Path:
    """Download MiniLM into the shared cache for lightweight local testing."""
    return download_embedding_model('sentence-transformers/all-MiniLM-L6-v2', destination)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for explicit embedding model acquisition."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--model',
        type=str,
        default=DEFAULT_EMBEDDING_MODEL,
        help=f'Hugging Face model repo ID to download (default: {DEFAULT_EMBEDDING_MODEL}).',
    )
    parser.add_argument(
        '--destination',
        type=Path,
        default=None,
        help='Optional target directory; defaults to the managed Hugging Face model cache path.',
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Provide the root task entrypoint for explicit model acquisition."""
    args = build_parser().parse_args(argv)
    setup_logging(level=Settings().log_level)
    log = bind_logger(package='features', stage='model-download')
    try:
        path = download_embedding_model(model_name=args.model, destination=args.destination)
    except (OSError, RuntimeError, ValueError) as error:
        log.log('ERROR', 'Embedding model download failed: {}', error)
        return 1
    log.info('Embedding model available at {}', path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
