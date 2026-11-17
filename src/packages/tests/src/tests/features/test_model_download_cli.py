from pathlib import Path

import pytest

import features.model_download as model_download


def _ignore_logging_setup(**_options: object) -> int:
    return 0


def test_model_download_cli_passes_model_and_destination(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: list[tuple[str, Path | None]] = []

    def _fake_download(*, model_name: str, destination: Path | None) -> Path:
        captured.append((model_name, destination))
        return destination or tmp_path / 'downloaded'

    monkeypatch.setattr(model_download, 'setup_logging', _ignore_logging_setup)
    monkeypatch.setattr(model_download, 'download_embedding_model', _fake_download)

    destination = tmp_path / 'minilm'
    exit_code = model_download.main(
        ['--model', 'sentence-transformers/all-MiniLM-L6-v2', '--destination', str(destination)]
    )

    assert exit_code == 0
    assert captured == [('sentence-transformers/all-MiniLM-L6-v2', destination)]
