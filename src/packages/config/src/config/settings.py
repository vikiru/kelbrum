"""Validated immutable defaults shared by workspace packages."""

from typing import Literal

import msgspec


class Settings(msgspec.Struct, frozen=True):
    """Validated runtime settings that do not depend on process environment."""

    log_level: Literal['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO'
    tenrai_base_url: str = 'https://api.tenrai.org/v1'
    timeout_seconds: float = 30.0
    requests_per_second: float = 3.0
    max_retries: int = 4

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0 or self.requests_per_second <= 0 or self.max_retries < 0:
            raise ValueError('invalid runtime settings')
