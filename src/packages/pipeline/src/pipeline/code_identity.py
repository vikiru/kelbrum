"""Deterministic identity for code and dependencies that produce artifacts."""

from collections.abc import Mapping
from hashlib import sha256
from importlib import import_module
from pathlib import Path

IMPLEMENTATION_PACKAGES = (
    'anime_catalogue',
    'config',
    'export',
    'features',
    'fetch',
    'graph',
    'normalization',
    'pipeline',
    'processing',
    'recommender',
    'storage',
)


def current_implementation_identity() -> str:
    """Hash active package sources and the workspace dependency lockfile."""
    source_roots: dict[str, Path] = {}
    for package in IMPLEMENTATION_PACKAGES:
        module_file = import_module(package).__file__
        if module_file is None:
            raise ValueError(f'implementation package has no source path: {package}')
        source_roots[package] = Path(module_file).resolve().parent
    lockfile = next(
        (parent / 'uv.lock' for parent in Path(__file__).resolve().parents if (parent / 'uv.lock').is_file()),
        None,
    )
    return derive_implementation_identity(source_roots, lockfile)


def derive_implementation_identity(source_roots: Mapping[str, Path], lockfile: Path | None) -> str:
    """Hash source paths/content and a lockfile without depending on mtimes."""
    digest = sha256()
    for package, root in sorted(source_roots.items()):
        if not root.is_dir():
            raise ValueError(f'implementation source root does not exist: {package}')
        for path in sorted(root.rglob('*.py'), key=lambda item: item.relative_to(root).as_posix()):
            digest.update(f'{package}/{path.relative_to(root).as_posix()}'.encode())
            digest.update(b'\0')
            digest.update(path.read_bytes())
            digest.update(b'\0')
    if lockfile is not None:
        if not lockfile.is_file():
            raise ValueError('dependency lockfile does not exist')
        digest.update(b'dependency-lock\0')
        digest.update(lockfile.read_bytes())
    return digest.hexdigest()
