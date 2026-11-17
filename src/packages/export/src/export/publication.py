"""Version staging and atomic directory activation for exported frontend artifacts."""

import ctypes
import errno
import os
import shutil
import sys
import tempfile
from pathlib import Path

from export.contracts import FrontendArtifactManifest
from storage.hashing import sha256_file
from storage.json_io import read_json


def create_staging_directory(destination: Path) -> Path:
    """Create a private staging directory beside the active artifact directory."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=f'.{destination.name}.staging-', dir=destination.parent))


def publish_staged_directory(staging: Path, destination: Path) -> None:
    """Atomically activate a complete directory, exchanging an existing version when present."""
    if staging.parent.resolve() != destination.parent.resolve():
        raise ValueError('staging and destination directories must share a filesystem parent')
    if not staging.is_dir():
        raise ValueError(f'staging directory does not exist: {staging}')
    if destination.is_symlink():
        raise ValueError('active artifact path must be a directory')
    if not destination.exists():
        staging.replace(destination)
        return
    if not destination.is_dir():
        raise ValueError('active artifact path must be a directory')
    _exchange_directories(staging, destination)
    shutil.rmtree(staging, ignore_errors=True)


def validate_staged_artifacts(staging: Path, expected_count: int) -> None:
    """Verify the completion manifest and every immutable file before publication."""
    manifest_path = staging / 'artifact-manifest.json'
    manifest = read_json(manifest_path, FrontendArtifactManifest)
    if manifest.schema_version != 'frontend-artifacts-v1' or manifest.metadata_count != expected_count:
        raise ValueError('staged frontend manifest has an incompatible schema or catalogue count')
    root = staging.resolve()
    paths: set[str] = set()
    for item in manifest.files:
        relative_path = Path(item.path)
        artifact_path = (root / relative_path).resolve()
        if relative_path.is_absolute() or not artifact_path.is_relative_to(root) or item.path in paths:
            raise ValueError(f'staged frontend manifest contains an invalid path: {item.path}')
        if not artifact_path.is_file() or artifact_path.stat().st_size != item.bytes:
            raise ValueError(f'staged frontend artifact is missing or has an invalid size: {item.path}')
        if sha256_file(artifact_path) != item.sha256:
            raise ValueError(f'staged frontend artifact has an invalid checksum: {item.path}')
        paths.add(item.path)
    if not paths:
        raise ValueError('staged frontend manifest contains no artifacts')


def _exchange_directories(first: Path, second: Path) -> None:
    if sys.platform == 'linux':
        try:
            _try_linux_exchange(first, second)
        except OSError:
            _fallback_exchange_directories(first, second)
        return
    _fallback_exchange_directories(first, second)


def _try_linux_exchange(first: Path, second: Path) -> None:
    renameat2 = getattr(ctypes.CDLL(None, use_errno=True), 'renameat2', None)
    if renameat2 is None:
        raise OSError(errno.ENOSYS, 'atomic directory exchange is unavailable on this platform')
    renameat2.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    renameat2.restype = ctypes.c_int
    result = renameat2(-100, os.fsencode(first), -100, os.fsencode(second), 2)
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, 'atomic artifact directory exchange failed', str(second))


def _fallback_exchange_directories(first: Path, second: Path) -> None:
    """Swap two directories via a temporary backup when renameat2 is unavailable."""
    backup = Path(tempfile.mkdtemp(prefix=f'.{second.name}.backup-', dir=second.parent))
    try:
        second.replace(backup)
    except OSError:
        shutil.rmtree(backup, ignore_errors=True)
        raise
    try:
        first.replace(second)
    except OSError:
        backup.replace(second)
        raise
    backup.replace(first)
