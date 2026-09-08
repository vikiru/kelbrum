"""Sequential request pacing."""

import time


class RequestPacer:
    """Keep requests at or below a configured rate."""

    def __init__(self, requests_per_second: float) -> None:
        if requests_per_second <= 0:
            raise ValueError('requests_per_second must be positive')
        self._interval = 1.0 / requests_per_second
        self._last_request = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self._interval:
            time.sleep(self._interval - elapsed)
        self._last_request = time.monotonic()
