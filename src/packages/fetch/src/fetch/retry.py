"""Retry and backoff policy for Tenrai requests."""

import time

RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
RATE_LIMIT_STATUS = 429
MAX_BACKOFF_SECONDS = 30.0


def retry_delay(status_code: int, attempt: int, retry_after: str | None) -> float:
    """Return server guidance when valid, otherwise bounded exponential backoff."""
    if status_code == RATE_LIMIT_STATUS and retry_after and retry_after.isdigit():
        return float(retry_after)
    return min(2**attempt, MAX_BACKOFF_SECONDS)


def pause(seconds: float) -> None:
    """Pause between requests."""
    time.sleep(seconds)
