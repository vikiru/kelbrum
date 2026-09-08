"""Decoders for external and persisted model boundaries."""

import msgspec

from models.tenrai import TenraiAnimeEntry, TenraiListResponse


def decode_catalogue(payload: bytes) -> TenraiListResponse[TenraiAnimeEntry]:
    """Decode one Tenrai catalogue response and fail on malformed fields."""
    return msgspec.json.decode(payload, type=TenraiListResponse[TenraiAnimeEntry])
