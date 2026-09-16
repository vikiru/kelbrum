"""Decoders for the Tenrai transport boundary."""

import msgspec

from fetch.contracts import TenraiAnimeEntry, TenraiListResponse


def decode_catalogue(payload: bytes) -> TenraiListResponse[TenraiAnimeEntry]:
    """Decode one Tenrai catalogue response and fail on malformed fields."""
    return msgspec.json.decode(payload, type=TenraiListResponse[TenraiAnimeEntry])
