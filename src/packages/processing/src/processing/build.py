"""Deterministic snapshot-to-canonical build orchestration."""

from collections.abc import Collection
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import cast

import msgspec
import polars as pl

from anime_catalogue import order_catalogue_frame
from models.labels import normalize_label
from models.tenrai import CanonicalAnime, Images, Taxonomy, TenraiAnimeEntry
from processing.canonicalize import canonicalize
from processing.constants import PROCESSING_AUDIT_SCHEMA_VERSION
from processing.eligibility import (
    EligibilityAudit,
    EligibilityPolicy,
    filter_entries,
    filter_non_recommendable_content,
)
from processing.ona import cleanup_ona
from processing.ratings import normalize_rating
from storage.json_io import read_json, write_json
from storage.tabular import read_parquet, write_parquet


class ProcessingResult(msgspec.Struct, frozen=True):
    records: tuple[CanonicalAnime, ...]
    audit: EligibilityAudit
    duplicate_ids: tuple[int, ...]
    profile: str = 'tenrai-catalog'


CANONICAL_SCHEMA = {
    'mal_id': pl.Int64,
    'title': pl.String,
    'title_english': pl.String,
    'title_japanese': pl.String,
    'images_json': pl.String,
    'anime_type': pl.String,
    'source': pl.String,
    'year': pl.Int64,
    'episodes': pl.Int64,
    'duration_minutes': pl.Int64,
    'status': pl.String,
    'rating': pl.String,
    'rating_class': pl.String,
    'demographics': pl.List(pl.String),
    'score': pl.Float64,
    'synopsis': pl.String,
    'synopsis_features': pl.String,
    'genres': pl.List(pl.String),
    'themes': pl.List(pl.String),
    'studios': pl.List(pl.String),
    'studio_ids': pl.List(pl.Int64),
    'relation_anime_ids': pl.List(pl.Int64),
}


def canonical_frame(records: tuple[CanonicalAnime, ...]) -> pl.DataFrame:
    """Create the canonical Parquet frame from ordered records."""
    return pl.DataFrame(
        {
            'mal_id': [record.mal_id for record in records],
            'title': [record.title for record in records],
            'title_english': [record.title_english for record in records],
            'title_japanese': [record.title_japanese for record in records],
            'images_json': [
                msgspec.json.encode(record.images).decode('utf-8') if record.images else None for record in records
            ],
            'anime_type': [record.anime_type for record in records],
            'source': [record.source for record in records],
            'year': [record.year for record in records],
            'episodes': [record.episodes for record in records],
            'duration_minutes': [record.duration_minutes for record in records],
            'status': [record.status for record in records],
            'rating': [record.rating for record in records],
            'rating_class': [normalize_rating(record.rating).value for record in records],
            'demographics': [[item.name for item in record.demographics] for record in records],
            'score': [record.score for record in records],
            'synopsis': [record.synopsis for record in records],
            'synopsis_features': [record.synopsis_features for record in records],
            'genres': [[item.name for item in record.genres] for record in records],
            'themes': [[item.name for item in record.themes] for record in records],
            'studios': [[item.name for item in record.studios] for record in records],
            'studio_ids': [[item.mal_id for item in record.studios] for record in records],
            'relation_anime_ids': [
                sorted(
                    {
                        target.mal_id
                        for relation in record.relations
                        for target in relation.entry
                        if target.type and target.type.lower() == 'anime'
                    }
                )
                for record in records
            ],
        },
        schema=CANONICAL_SCHEMA,
    )


def build_canonical(
    entries: list[TenraiAnimeEntry],
    policy: EligibilityPolicy | None = None,
    *,
    tagged_anime_ids: Collection[int] = (),
    theme_additions: dict[int, tuple[str, ...]] | None = None,
) -> ProcessingResult:
    """Filter, deduplicate, canonicalize, and order a snapshot without I/O."""
    eligible, audit = filter_entries(entries, policy, tagged_anime_ids=tagged_anime_ids)
    eligible, content_rejections = filter_non_recommendable_content(eligible)
    eligible, ona_audit = cleanup_ona(eligible)
    if theme_additions:
        eligible = [_add_themes(entry, theme_additions.get(entry.mal_id, ())) for entry in eligible]
    removed_ids = set(audit.rejected_ids) | set(ona_audit.removed_ids)
    reason_counts = dict(audit.reasons_by_rule)
    reasons_by_id = dict(audit.reasons_by_id)
    for anime_id, reason in content_rejections.items():
        reason_value = reason.value
        reason_counts[reason_value] = reason_counts.get(reason_value, 0) + 1
        reasons_by_id[anime_id] = (*reasons_by_id.get(anime_id, ()), reason_value)
    for reason, ids in (
        ('short_form_ona', ona_audit.short_form_ids),
        ('promotional_ona', ona_audit.promotional_ids),
        ('missing_semantic_evidence', ona_audit.missing_metadata_ids),
    ):
        reason_counts[reason] = reason_counts.get(reason, 0) + len(ids)
        for anime_id in ids:
            reasons_by_id[anime_id] = (*reasons_by_id.get(anime_id, ()), reason)
    audit = EligibilityAudit(
        accepted_count=len(eligible),
        rejected_count=len(removed_ids),
        rejected_ids=tuple(sorted(removed_ids)),
        reasons_by_rule=tuple(sorted(reason_counts.items())),
        reasons_by_id=tuple(
            sorted((anime_id, tuple(sorted(set(reasons)))) for anime_id, reasons in reasons_by_id.items())
        ),
        policy_version=audit.policy_version,
    )
    unique: dict[int, TenraiAnimeEntry] = {}
    duplicate_ids: set[int] = set()
    for entry in eligible:
        if entry.mal_id in unique:
            duplicate_ids.add(entry.mal_id)
            continue
        unique[entry.mal_id] = entry
    records = tuple(canonicalize(unique[anime_id]) for anime_id in sorted(unique))
    return ProcessingResult(records, audit, tuple(sorted(duplicate_ids)))


def _add_themes(entry: TenraiAnimeEntry, additions: tuple[str, ...]) -> TenraiAnimeEntry:
    """Apply curated theme additions without mutating the source entry."""
    existing = {normalize_label(theme.name) for theme in entry.themes}
    additions_to_apply = (
        Taxonomy(0, normalize_label(name)) for name in additions if normalize_label(name) not in existing
    )
    themes = [*entry.themes, *additions_to_apply]
    return msgspec.structs.replace(entry, themes=themes)


def process_snapshot(
    snapshot_path: Path,
    parquet_path: Path,
    audit_path: Path,
    *,
    snapshot_id: str,
    policy: EligibilityPolicy | None = None,
    theme_additions: dict[int, tuple[str, ...]] | None = None,
    tagged_anime_ids: Collection[int] = (),
) -> ProcessingResult:
    """Run the complete accepted-snapshot processing workflow."""
    entries = read_json(snapshot_path, list[TenraiAnimeEntry])
    result = build_canonical(
        entries,
        policy,
        tagged_anime_ids=tagged_anime_ids,
        theme_additions=theme_additions,
    )
    write_processing_outputs(
        result,
        parquet_path,
        audit_path,
        snapshot_id=snapshot_id,
        source_sha256=sha256(snapshot_path.read_bytes()).hexdigest(),
        policy_identity=msgspec.json.encode(
            {
                'policy': policy or EligibilityPolicy(),
                'theme_additions': theme_additions or {},
                'tagged_anime_ids': sorted(tagged_anime_ids),
            }
        ).decode('utf-8'),
    )
    return result


def load_canonical_parquet(path: Path) -> tuple[CanonicalAnime, ...]:
    """Load the compact canonical handoff without reparsing the enriched JSON."""
    frame = order_catalogue_frame(read_parquet(path))
    return tuple(_canonical_from_row(row) for row in frame.iter_rows(named=True))


def _canonical_from_row(row: dict[str, object]) -> CanonicalAnime:
    def names(field: str) -> tuple[Taxonomy, ...]:
        values = cast('list[object] | None', row[field]) or []
        return tuple(Taxonomy(0, str(value)) for value in values)

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

    images_json = optional_str('images_json')
    return CanonicalAnime(
        mal_id=int(mal_id),
        url=None,
        title=str(row['title']),
        title_english=optional_str('title_english'),
        title_japanese=optional_str('title_japanese'),
        title_synonyms=(),
        anime_type=optional_str('anime_type'),
        source=optional_str('source'),
        rating=optional_str('rating'),
        season=None,
        episodes=optional_int('episodes'),
        duration_minutes=optional_int('duration_minutes'),
        year=optional_int('year'),
        status=optional_str('status'),
        score=optional_float('score'),
        synopsis=optional_str('synopsis'),
        synopsis_features=optional_str('synopsis_features'),
        background=None,
        moreinfo=None,
        images=_decode_images(images_json),
        trailer=None,
        external=(),
        streaming=(),
        theme=None,
        studios=(),
        producers=(),
        licensors=(),
        genres=names('genres'),
        themes=names('themes'),
        demographics=names('demographics'),
        relations=(),
    )


def _decode_images(images_json: str | None) -> Images | None:
    if images_json is None:
        return None
    return msgspec.json.decode(images_json.encode('utf-8'), type=Images)


def write_canonical_parquet(result: ProcessingResult, destination: Path) -> int:
    """Write the accepted canonical records to Parquet."""
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
    fetched_date = datetime.now(UTC).isoformat()
    write_json(
        audit_path,
        {
            'schema_version': PROCESSING_AUDIT_SCHEMA_VERSION,
            'profile': result.profile,
            'snapshot_id': snapshot_id,
            'source_sha256': source_sha256,
            'policy_identity': policy_identity,
            'fetched_date': fetched_date,
            'accepted_count': result.audit.accepted_count,
            'rejected_count': result.audit.rejected_count,
            'rejected_ids': result.audit.rejected_ids,
            'reasons_by_rule': result.audit.reasons_by_rule,
            'reasons_by_id': result.audit.reasons_by_id,
            'duplicate_ids': result.duplicate_ids,
        },
    )
