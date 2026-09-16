"""Snapshot processing workflow composed from pure processing and adapters."""

from collections.abc import Collection
from pathlib import Path

from config import bind_logger, derive_payload_identity, timed_event
from fetch.contracts import TenraiAnimeEntry
from processing.build import ProcessingResult, build_canonical
from processing.eligibility import EligibilityPolicy
from processing.identity import processing_artifact_identity
from processing.persistence import write_processing_outputs
from storage.hashing import sha256_file
from storage.json_io import read_json

log = bind_logger(package='processing', stage='canonicalization')


def process_snapshot(
    snapshot_path: Path,
    parquet_path: Path,
    audit_path: Path,
    *,
    snapshot_id: str,
    policy: EligibilityPolicy | None = None,
    theme_additions: dict[int, tuple[str, ...]] | None = None,
    theme_removals: dict[int, tuple[str, ...]] | None = None,
    tagged_anime_ids: Collection[int] = (),
    curation_identity: str | None = None,
    run_id: str = '-',
) -> ProcessingResult:
    """Run the snapshot workflow through pure transformation and persistence adapters."""
    active_policy = policy or EligibilityPolicy()
    active_theme_additions = theme_additions or {}
    active_theme_removals = theme_removals or {}
    entries = read_json(snapshot_path, list[TenraiAnimeEntry])
    log.info('Loaded {} entries from the catalogue snapshot.', len(entries))
    with timed_event(
        log,
        event_name='stage.completed',
        package='processing',
        stage='canonicalization',
        run_id=run_id,
        row_count=len(entries),
    ):
        result = build_canonical(
            entries,
            active_policy,
            tagged_anime_ids=tagged_anime_ids,
            theme_additions=active_theme_additions,
            theme_removals=active_theme_removals,
        )
    source_sha256 = sha256_file(snapshot_path)
    write_processing_outputs(
        result,
        parquet_path,
        audit_path,
        snapshot_id=snapshot_id,
        source_sha256=source_sha256,
        policy_identity=processing_artifact_identity(
            source_sha256=source_sha256,
            policy=active_policy,
            theme_additions=active_theme_additions,
            theme_removals=active_theme_removals,
            tagged_anime_ids=tagged_anime_ids,
            policy_identity=derive_payload_identity(active_policy),
            curation_identity=curation_identity,
        ),
    )
    log.info('Canonicalization completed with {} accepted records.', len(result.records))
    return result
