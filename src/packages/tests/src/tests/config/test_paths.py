from pathlib import Path

import pytest

from config import (
    manual_data_dir,
    package_data_dir,
    pipeline_dir,
    source_snapshot_dir,
    workspace_root,
)


def test_package_data_dir_falls_back_to_workspace_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv('KELBRUM_DATA_DIR', raising=False)
    assert package_data_dir() == workspace_root() / 'data'

    monkeypatch.setenv('KELBRUM_DATA_DIR', '   ')
    assert package_data_dir() == workspace_root() / 'data'


def test_package_data_dir_honors_kelbrum_data_dir_override(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    custom_dir = tmp_path / 'custom-data'
    monkeypatch.setenv('KELBRUM_DATA_DIR', f'  {custom_dir}  ')

    assert package_data_dir() == custom_dir
    assert manual_data_dir() == custom_dir / 'manual'
    assert source_snapshot_dir() == custom_dir / 'source' / 'tenrai' / 'snapshots'
    assert pipeline_dir() == custom_dir / 'pipeline'
