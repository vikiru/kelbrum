"""Explicit, idempotent Loguru configuration for workspace packages."""

from __future__ import annotations

import sys

import loguru
from loguru import logger

from config._paths import workspace_root

_sink_ids: tuple[int, ...] = ()
_DIAGNOSTIC_FORMAT = '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | context={extra} | {message}'


def setup_logging(*, level: str = 'INFO') -> int:
    """Install or replace console and diagnostic file sinks and return the console ID."""
    global _sink_ids  # noqa: PLW0603
    if not _sink_ids:
        logger.remove(0)
    else:
        for sink_id in _sink_ids:
            logger.remove(sink_id)
    logger.configure(extra={'display_stage': 'SYSTEM'})
    logs_dir = workspace_root() / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    new_sink_ids: list[int] = []
    try:
        new_sink_ids.append(
            logger.add(
                sys.stderr,
                level=level,
                format='{time:HH:mm:ss} | {level:<8} | [{extra[display_stage]}] {message}',
            )
        )
        new_sink_ids.append(
            logger.add(logs_dir / 'debug.log', level='DEBUG', format=_DIAGNOSTIC_FORMAT, rotation='10 MB')
        )
        new_sink_ids.append(
            logger.add(logs_dir / 'info.log', level='INFO', format=_DIAGNOSTIC_FORMAT, rotation='10 MB')
        )
        new_sink_ids.append(
            logger.add(logs_dir / 'error.log', level='ERROR', format=_DIAGNOSTIC_FORMAT, rotation='10 MB')
        )
        new_sink_ids.append(
            logger.add(
                logs_dir / 'http.log',
                level='DEBUG',
                format=_DIAGNOSTIC_FORMAT,
                rotation='10 MB',
                filter=_is_fetch_record,
            )
        )
    except Exception:
        for sink_id in new_sink_ids:
            logger.remove(sink_id)
        raise
    _sink_ids = tuple(new_sink_ids)
    return new_sink_ids[0]


def _is_fetch_record(record: loguru.Record) -> bool:
    return record['extra'].get('package') == 'fetch'


def bind_logger(*, package: str, stage: str | None = None, run_id: str | None = None) -> loguru.Logger:
    """Return a logger carrying non-sensitive execution context."""
    active_stage = stage or package
    return logger.bind(
        package=package,
        stage=active_stage,
        display_stage=active_stage.replace('-', ' ').upper(),
        run_id=run_id or '-',
    )
