"""Fetch-mode selection for known refresh and new discovery."""

from collections.abc import Iterable

EARLIEST_DISCOVERY_YEAR = 1900


def refresh_ids(requested_ids: Iterable[int], known_ids: set[int]) -> tuple[int, ...]:
    """Return sorted known IDs and reject unknown refresh targets."""
    ids = tuple(sorted(set(requested_ids)))
    unknown = sorted(set(ids) - known_ids)
    if unknown:
        raise ValueError(f'refresh IDs are not in the canonical catalogue: {unknown}')
    return ids


def discovery_periods(start_year: int, end_year: int, *, overlap_years: int = 0) -> tuple[int, ...]:
    """Return bounded inclusive discovery years with explicit overlap."""
    if start_year < EARLIEST_DISCOVERY_YEAR or end_year < start_year or overlap_years < 0:
        raise ValueError('invalid discovery period or overlap')
    return tuple(range(max(EARLIEST_DISCOVERY_YEAR, start_year - overlap_years), end_year + 1))
