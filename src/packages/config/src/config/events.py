"""Bounded structured events shared by pipeline applications."""

from __future__ import annotations

import resource
import sys
from collections.abc import Generator  # noqa: TC003
from contextlib import contextmanager
from time import perf_counter

import loguru  # noqa: TC002
import msgspec


class LogEvent(msgspec.Struct, frozen=True):
    """Small machine-readable event payload with no source-record data."""

    event_name: str
    package: str
    stage: str
    run_id: str = '-'
    entry_point: str = '-'
    duration_ms: float | None = None
    row_count: int | None = None
    cache_decision: str | None = None
    cache_reason: str | None = None
    artifact_identity: str | None = None
    memory_mb: float | None = None
    artifact_bytes: int | None = None
    error_code: str | None = None


def emit_event(log: loguru.Logger, event: LogEvent) -> None:
    """Emit one bounded event through the configured structured logger."""
    bound = log.bind(
        display_stage=event.stage.replace('-', ' ').upper(),
        event=event.event_name,
        event_package=event.package,
        event_stage=event.stage,
        event_run_id=event.run_id,
        entry_point=event.entry_point,
        duration_ms=event.duration_ms,
        row_count=event.row_count,
        cache_decision=event.cache_decision,
        cache_reason=event.cache_reason,
        artifact_identity=event.artifact_identity,
        memory_mb=event.memory_mb,
        artifact_bytes=event.artifact_bytes,
        error_code=event.error_code,
    )
    bound.debug('structured event')


def peak_memory_mb() -> float:
    """Return the process peak resident set size in megabytes."""
    divisor = 1_048_576 if sys.platform == 'darwin' else 1_024
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / divisor


@contextmanager
def timed_event(
    log: loguru.Logger,
    *,
    event_name: str,
    package: str,
    stage: str,
    run_id: str = '-',
    entry_point: str = '-',
    row_count: int | None = None,
) -> Generator[None]:
    """Emit one bounded completion or failure event around a stage."""
    started = perf_counter()

    def emit_completion(error_code: str | None = None) -> None:
        emit_event(
            log,
            LogEvent(
                event_name=event_name,
                package=package,
                stage=stage,
                run_id=run_id,
                entry_point=entry_point,
                duration_ms=(perf_counter() - started) * 1_000,
                row_count=row_count,
                memory_mb=peak_memory_mb(),
                error_code=error_code,
            ),
        )

    try:
        yield
    except Exception as error:
        emit_completion(type(error).__name__)
        raise
    else:
        emit_completion()
