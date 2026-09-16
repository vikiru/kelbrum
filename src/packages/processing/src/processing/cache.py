"""Reusable canonical processing artifacts and their cache identity."""

from collections.abc import Collection, Mapping
from pathlib import Path

from config import derive_payload_identity
from processing.constants import PROCESSING_AUDIT_SCHEMA_VERSION
from processing.contracts import CanonicalAnime
from processing.eligibility import EligibilityPolicy
from processing.identity import processing_artifact_identity
from processing.persistence import load_canonical_parquet
from processing.workflow import process_snapshot
from storage.errors import StorageError
from storage.hashing import sha256_file
from storage.json_io import read_json


def load_or_process_records(
    snapshot_path: Path,
    parquet_path: Path,
    audit_path: Path,
    *,
    snapshot_id: str,
    policy: EligibilityPolicy,
    theme_additions: Mapping[int, tuple[str, ...]],
    theme_removals: Mapping[int, tuple[str, ...]],
    tagged_anime_ids: Collection[int],
    curation_identity: str | None = None,
    run_id: str = '-',
) -> tuple[CanonicalAnime, ...]:
    """Reuse a valid canonical artifact or build and persist a fresh one."""
    if (
        parquet_path.is_file()
        and audit_path.is_file()
        and processed_cache_matches(
            audit_path,
            snapshot_path,
            policy,
            theme_additions=theme_additions,
            theme_removals=theme_removals,
            tagged_anime_ids=tagged_anime_ids,
            curation_identity=curation_identity,
        )
    ):
        return load_canonical_parquet(parquet_path)
    return process_snapshot(
        snapshot_path,
        parquet_path,
        audit_path,
        snapshot_id=snapshot_id,
        policy=policy,
        theme_additions=dict(theme_additions),
        theme_removals=dict(theme_removals),
        tagged_anime_ids=tagged_anime_ids,
        curation_identity=curation_identity,
        run_id=run_id,
    ).records


def processed_cache_matches(
    audit_path: Path,
    source_path: Path,
    policy: EligibilityPolicy,
    *,
    theme_additions: Mapping[int, tuple[str, ...]],
    theme_removals: Mapping[int, tuple[str, ...]],
    tagged_anime_ids: Collection[int],
    curation_identity: str | None = None,
) -> bool:
    """Return whether the audit proves that the canonical artifact is current."""
    try:
        audit = read_json(audit_path, dict[str, object])
        policy_identity = audit.get('policy_identity')
        if not isinstance(policy_identity, str):
            return False
        source_sha256 = sha256_file(source_path)
        expected_identity = processing_artifact_identity(
            source_sha256=source_sha256,
            policy=policy,
            theme_additions=theme_additions,
            theme_removals=theme_removals,
            tagged_anime_ids=tagged_anime_ids,
            policy_identity=derive_payload_identity(policy),
            curation_identity=curation_identity,
        )
        return (
            audit.get('source_sha256') == source_sha256
            and policy_identity == expected_identity
            and audit.get('schema_version') == PROCESSING_AUDIT_SCHEMA_VERSION
        )
    except (OSError, StorageError, TypeError, ValueError):
        return False
