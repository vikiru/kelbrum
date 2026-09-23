from pathlib import Path

from pipeline.__main__ import _profile_paths


def test_default_profile_uses_generic_local_snapshot_pair() -> None:
    paths = _profile_paths('default')

    assert paths.snapshot.name == 'tenrai-anime.full.json'
    assert paths.checkpoint.name == 'tenrai-anime.full.checkpoint.json'
    assert paths.full_artifact.name == 'tenrai-anime.full.json'


def test_all_profile_uses_generic_local_snapshot_pair() -> None:
    paths = _profile_paths('all')

    assert paths.snapshot.name == 'tenrai-anime.full.json'
    assert paths.checkpoint.name == 'tenrai-anime.full.checkpoint.json'
    assert paths.full_artifact.name == 'tenrai-anime.full.json'
    assert isinstance(paths.snapshot, Path)
