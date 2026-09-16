"""Processing-cache decisions used by the catalogue pipeline."""

from collections.abc import Mapping
from pathlib import Path

from config import LogEvent, bind_logger, emit_event
from pipeline.curation import audit_curation, load_curation_snapshot
from processing.cache import load_or_process_records as load_cached_records
from processing.cache import processed_cache_matches
from processing.contracts import CanonicalAnime
from processing.eligibility import EligibilityPolicy

log = bind_logger(package='pipeline')


def load_or_process_records(
    snapshot_path: Path,
    parquet_path: Path,
    audit_path: Path,
    *,
    snapshot_id: str,
    policy: EligibilityPolicy,
    run_id: str = '-',
) -> tuple[CanonicalAnime, ...]:
    """Reuse aligned processed records or rebuild them from the accepted snapshot."""
    curation = load_curation_snapshot()
    cache_is_current = (
        parquet_path.is_file() and audit_path.is_file() and _processed_cache_matches(audit_path, snapshot_path, policy)
    )
    records = load_cached_records(
        snapshot_path,
        parquet_path,
        audit_path,
        snapshot_id=snapshot_id,
        policy=policy,
        theme_additions=curation.theme_additions,
        theme_removals=curation.theme_removals,
        tagged_anime_ids=curation.tagged_anime_ids,
        curation_identity=curation.identity,
        run_id=run_id,
    )
    curation_audit = audit_curation(curation, {record.mal_id for record in records})
    if curation_audit.missing_count:
        log.warning(
            'Curation references {} catalogue IDs outside the active build.',
            curation_audit.missing_count,
        )
    _emit_cache_event(
        run_id,
        'reused' if cache_is_current else 'rebuilt',
        'identity-and-alignment-match' if cache_is_current else 'missing-or-invalid',
        len(records) if cache_is_current else None,
    )
    return records


def _processed_cache_matches(audit_path: Path, source_path: Path, policy: EligibilityPolicy) -> bool:
    """Check whether the processing audit proves that the Parquet cache is current."""
    curation = load_curation_snapshot()
    return processed_cache_matches(
        audit_path,
        source_path,
        policy,
        theme_additions=curation.theme_additions,
        theme_removals=curation.theme_removals,
        tagged_anime_ids=curation.tagged_anime_ids,
        curation_identity=curation.identity,
    )


def _emit_cache_event(run_id: str, decision: str, reason: str, row_count: int | None) -> None:
    """Record one processing-cache decision with an optional reused row count."""
    emit_event(
        log,
        LogEvent(
            event_name='cache.decision',
            package='pipeline',
            stage='processing',
            run_id=run_id,
            cache_decision=decision,
            cache_reason=reason,
            row_count=row_count,
        ),
    )


def audit_count(audit: Mapping[str, object], key: str, default: int) -> int:
    """Read an integer audit count while preserving a safe fallback for old audits."""
    value = audit.get(key)
    return value if isinstance(value, int) else default
