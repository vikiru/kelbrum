"""Persistence adapters for processing artifacts."""

from pathlib import Path
from typing import TypeVar, cast

import msgspec

from anime_catalogue import order_catalogue_frame
from fetch.contracts import AnimeRelation, ExternalLink, Images, NamedResource, Taxonomy, Trailer
from processing.build import ProcessingResult, canonical_frame
from processing.constants import PROCESSING_AUDIT_SCHEMA_VERSION
from processing.contracts import CanonicalAnime
from storage.json_io import write_json
from storage.tabular import read_parquet, write_parquet

Decoded = TypeVar('Decoded')


def load_canonical_parquet(path: Path) -> tuple[CanonicalAnime, ...]:
    """Load the compact canonical handoff without reparsing enriched JSON."""
    frame = order_catalogue_frame(read_parquet(path))
    return tuple(_canonical_from_row(row) for row in frame.iter_rows(named=True))


def write_canonical_parquet(result: ProcessingResult, destination: Path) -> int:
    """Write accepted canonical records to Parquet."""
    frame = canonical_frame(result.records)
    write_parquet(destination, frame)
    return frame.height


def write_processing_outputs(
    result: ProcessingResult,
    parquet_path: Path,
    audit_path: Path,
    *,
    snapshot_id: str,
    source_sha256: str | None = None,
    policy_identity: str | None = None,
) -> None:
    """Persist canonical Parquet, audit data, and source provenance."""
    write_canonical_parquet(result, parquet_path)
    write_json(
        audit_path,
        {
            'schema_version': PROCESSING_AUDIT_SCHEMA_VERSION,
            'profile': result.profile,
            'snapshot_id': snapshot_id,
            'source_sha256': source_sha256,
            'policy_identity': policy_identity,
            'accepted_count': result.audit.accepted_count,
            'rejected_count': result.audit.rejected_count,
            'rejected_ids': result.audit.rejected_ids,
            'reasons_by_rule': result.audit.reasons_by_rule,
            'reasons_by_id': result.audit.reasons_by_id,
            'duplicate_ids': result.duplicate_ids,
        },
    )


def _canonical_from_row(row: dict[str, object]) -> CanonicalAnime:
    def names(field: str) -> tuple[Taxonomy, ...]:
        encoded = row.get(f'{field}_json')
        if isinstance(encoded, str):
            return msgspec.json.decode(encoded.encode(), type=tuple[Taxonomy, ...])
        values = cast('list[object] | None', row[field]) or []
        return tuple(Taxonomy(0, str(value)) for value in values)

    def decoded(field: str, target: type[Decoded], fallback: Decoded) -> Decoded:
        encoded = row.get(field)
        return msgspec.json.decode(encoded.encode(), type=target) if isinstance(encoded, str) else fallback

    def optional_int(field: str) -> int | None:
        value = row[field]
        return int(value) if isinstance(value, (int, float, str)) else None

    def optional_float(field: str) -> float | None:
        value = row[field]
        return float(value) if isinstance(value, (int, float, str)) else None

    def optional_str(field: str) -> str | None:
        value = row.get(field)
        return str(value) if value is not None else None

    mal_id = row['mal_id']
    if not isinstance(mal_id, (int, float, str)):
        raise TypeError('canonical Parquet row has an invalid mal_id')

    return CanonicalAnime(
        mal_id=int(mal_id),
        url=optional_str('url'),
        title=str(row['title']),
        title_english=optional_str('title_english'),
        title_japanese=optional_str('title_japanese'),
        title_synonyms=decoded('title_synonyms_json', tuple[str, ...], ()),
        anime_type=optional_str('anime_type'),
        source=optional_str('source'),
        rating=optional_str('rating'),
        season=optional_str('season'),
        episodes=optional_int('episodes'),
        duration_minutes=optional_int('duration_minutes'),
        year=optional_int('year'),
        status=optional_str('status'),
        score=optional_float('score'),
        synopsis=optional_str('synopsis'),
        synopsis_features=optional_str('synopsis_features'),
        background=optional_str('background'),
        moreinfo=optional_str('moreinfo'),
        images=_decode_images(optional_str('images_json')),
        trailer=decoded('trailer_json', Trailer, None),
        external=decoded('external_json', tuple[ExternalLink, ...], ()),
        studios=decoded('studios_json', tuple[NamedResource, ...], ()),
        producers=decoded('producers_json', tuple[NamedResource, ...], ()),
        licensors=decoded('licensors_json', tuple[NamedResource, ...], ()),
        genres=names('genres'),
        themes=names('themes'),
        demographics=names('demographics'),
        relations=decoded('relations_json', tuple[AnimeRelation, ...], ()),
    )


def _decode_images(images_json: str | None) -> Images | None:
    if images_json is None:
        return None
    return msgspec.json.decode(images_json.encode(), type=Images)
