"""Explicit, idempotent Loguru configuration for workspace packages."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger

_sink_id: int | None = None


def setup_logging(*, level: str = 'INFO') -> int:
    """Install or replace this package's stderr sink and return its ID."""
    global _sink_id  # noqa: PLW0603
    if _sink_id is None:
        logger.remove(0)
    else:
        logger.remove(_sink_id)
    _sink_id = logger.add(
        sys.stderr,
        level=level,
        format='{time:YYYY-MM-DD HH:mm:ss} | {level} | context={extra} | {message}',
    )
    return _sink_id


def bind_logger(*, package: str, stage: str | None = None, run_id: str | None = None) -> Logger:
    """Return a logger carrying non-sensitive execution context."""
    context: dict[str, str] = {
        'package': package,
        'stage': stage or '-',
        'run_id': run_id or '-',
    }
    return logger.bind(**context)
