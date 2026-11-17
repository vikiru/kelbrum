from pathlib import Path

from pipeline.code_identity import IMPLEMENTATION_PACKAGES, derive_implementation_identity


def test_catalogue_taxonomy_participates_in_implementation_identity() -> None:
    assert 'anime_catalogue' in IMPLEMENTATION_PACKAGES
    assert 'fetch' in IMPLEMENTATION_PACKAGES


def test_implementation_identity_tracks_sources_and_dependency_lockfile(tmp_path: Path) -> None:
    source_root = tmp_path / 'recommender'
    source_root.mkdir()
    source_file = source_root / 'ranker.py'
    source_file.write_text('score = 1\n', encoding='utf-8')
    lockfile = tmp_path / 'uv.lock'
    lockfile.write_text('version = 1\n', encoding='utf-8')

    initial = derive_implementation_identity({'recommender': source_root}, lockfile)
    assert derive_implementation_identity({'recommender': source_root}, lockfile) == initial

    source_file.write_text('score = 2\n', encoding='utf-8')
    source_changed = derive_implementation_identity({'recommender': source_root}, lockfile)
    assert source_changed != initial

    lockfile.write_text('version = 2\n', encoding='utf-8')
    assert derive_implementation_identity({'recommender': source_root}, lockfile) != source_changed
