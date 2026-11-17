import errno
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import pytest

from export import publication
from export.contracts import FrontendArtifactFile, FrontendArtifactManifest
from export.publication import create_staging_directory, publish_staged_directory, validate_staged_artifacts
from storage.hashing import sha256_file
from storage.json_io import write_json


def test_staged_directory_exchange_keeps_active_version_complete(tmp_path: Path) -> None:
    active = tmp_path / 'frontend'
    active.mkdir()
    (active / 'version.txt').write_text('old', encoding='utf-8')
    staging = create_staging_directory(active)
    (staging / 'version.txt').write_text('new', encoding='utf-8')

    publish_staged_directory(staging, active)

    assert (active / 'version.txt').read_text(encoding='utf-8') == 'new'
    assert not staging.exists()


def test_failed_staged_publication_preserves_the_active_directory(tmp_path: Path) -> None:
    active = tmp_path / 'frontend'
    active.mkdir()
    (active / 'version.txt').write_text('valid', encoding='utf-8')

    with pytest.raises(ValueError, match='does not exist'):
        publish_staged_directory(tmp_path / 'missing-stage', active)

    assert (active / 'version.txt').read_text(encoding='utf-8') == 'valid'


def test_directory_publication_is_safe_for_concurrent_readers(tmp_path: Path) -> None:
    active = tmp_path / 'frontend'
    active.mkdir()
    (active / 'version.txt').write_text('0', encoding='utf-8')
    stop = Event()
    invalid_reads: list[str] = []

    def read_active_version() -> None:
        while not stop.is_set():
            try:
                version = (active / 'version.txt').read_text(encoding='utf-8')
            except OSError as error:
                invalid_reads.append(str(error))
                continue
            if not version.isdigit():
                invalid_reads.append(version)

    with ThreadPoolExecutor(max_workers=1) as executor:
        reader = executor.submit(read_active_version)
        for version in range(1, 21):
            staging = create_staging_directory(active)
            (staging / 'version.txt').write_text(str(version), encoding='utf-8')
            publish_staged_directory(staging, active)
        stop.set()
        reader.result()

    assert invalid_reads == []


def test_validate_staged_artifacts_verifies_checksum(tmp_path: Path) -> None:
    staging = tmp_path / 'staging'
    staging.mkdir()
    artifact = staging / 'index.json'
    artifact.write_text('{"ok": true}', encoding='utf-8')
    manifest = FrontendArtifactManifest(
        schema_version='frontend-artifacts-v1',
        generated_at='2026-01-01T00:00:00Z',
        metadata_count=1,
        full_entry_count=1,
        recommendation_source_count=1,
        metadata_files=('index.json',),
        full_files=(),
        files=(FrontendArtifactFile(bytes=artifact.stat().st_size, path='index.json', sha256='0' * 64),),
        search_metadata='index.json',
        search_metadata_chunks=(),
        build_identity='build-id',
        provenance={},
    )
    write_json(staging / 'artifact-manifest.json', manifest)

    with pytest.raises(ValueError, match='invalid checksum'):
        validate_staged_artifacts(staging, 1)

    valid_manifest = FrontendArtifactManifest(
        schema_version='frontend-artifacts-v1',
        generated_at='2026-01-01T00:00:00Z',
        metadata_count=1,
        full_entry_count=1,
        recommendation_source_count=1,
        metadata_files=('index.json',),
        full_files=(),
        files=(FrontendArtifactFile(bytes=artifact.stat().st_size, path='index.json', sha256=sha256_file(artifact)),),
        search_metadata='index.json',
        search_metadata_chunks=(),
        build_identity='build-id',
        provenance={},
    )
    write_json(staging / 'artifact-manifest.json', valid_manifest)
    validate_staged_artifacts(staging, 1)


def test_publish_staged_directory_rejects_dangling_symlink(tmp_path: Path) -> None:
    active = tmp_path / 'frontend'
    active.symlink_to(tmp_path / 'missing-target')
    staging = create_staging_directory(active)
    (staging / 'version.txt').write_text('new', encoding='utf-8')

    with pytest.raises(ValueError, match='must be a directory'):
        publish_staged_directory(staging, active)


def test_publish_staged_directory_falls_back_when_renameat2_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail_exchange(_first: Path, _second: Path) -> None:
        raise OSError(errno.EINVAL, 'unsupported')

    monkeypatch.setattr(publication, '_try_linux_exchange', fail_exchange)

    active = tmp_path / 'frontend'
    active.mkdir()
    (active / 'version.txt').write_text('old', encoding='utf-8')
    staging = create_staging_directory(active)
    (staging / 'version.txt').write_text('new', encoding='utf-8')

    publish_staged_directory(staging, active)

    assert (active / 'version.txt').read_text(encoding='utf-8') == 'new'
    assert not staging.exists()
