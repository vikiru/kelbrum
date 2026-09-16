"""Pure deterministic snapshot-to-canonical transformation."""

from collections.abc import Collection
from typing import Annotated

import msgspec
import polars as pl

from fetch.contracts import Taxonomy, TenraiAnimeEntry
from processing.canonicalize import canonicalize
from processing.contracts import CanonicalAnime
from processing.eligibility import (
    EligibilityAudit,
    EligibilityPolicy,
    filter_entries,
    filter_non_recommendable_content,
)
from processing.labels import normalize_label
from processing.ona import cleanup_ona
from processing.ratings import normalize_rating


class ProcessingResult(msgspec.Struct, frozen=True):
    records: tuple[CanonicalAnime, ...]
    audit: EligibilityAudit
    duplicate_ids: tuple[int, ...]
    profile: str = 'tenrai-catalog'


CanonicalFrame = Annotated[pl.DataFrame, 'canonical catalogue frame']


def canonical_frame(records: tuple[CanonicalAnime, ...]) -> CanonicalFrame:
    """Create the canonical Parquet frame from ordered records."""
    return pl.DataFrame(
        {
            'mal_id': [record.mal_id for record in records],
            'title': [record.title for record in records],
            'url': [record.url for record in records],
            'title_english': [record.title_english for record in records],
            'title_japanese': [record.title_japanese for record in records],
            'images_json': [
                msgspec.json.encode(record.images).decode('utf-8') if record.images else None for record in records
            ],
            'title_synonyms_json': [_encode_json(record.title_synonyms) for record in records],
            'trailer_json': [_encode_optional_json(record.trailer) for record in records],
            'external_json': [_encode_json(record.external) for record in records],
            'studios_json': [_encode_json(record.studios) for record in records],
            'producers_json': [_encode_json(record.producers) for record in records],
            'licensors_json': [_encode_json(record.licensors) for record in records],
            'genres_json': [_encode_json(record.genres) for record in records],
            'themes_json': [_encode_json(record.themes) for record in records],
            'demographics_json': [_encode_json(record.demographics) for record in records],
            'relations_json': [_encode_json(record.relations) for record in records],
            'anime_type': [record.anime_type for record in records],
            'source': [record.source for record in records],
            'season': [record.season for record in records],
            'year': [record.year for record in records],
            'episodes': [record.episodes for record in records],
            'duration_minutes': [record.duration_minutes for record in records],
            'status': [record.status for record in records],
            'background': [record.background for record in records],
            'moreinfo': [record.moreinfo for record in records],
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
        schema={
            'mal_id': pl.Int64,
            'title': pl.String,
            'url': pl.String,
            'title_english': pl.String,
            'title_japanese': pl.String,
            'images_json': pl.String,
            'title_synonyms_json': pl.String,
            'trailer_json': pl.String,
            'external_json': pl.String,
            'studios_json': pl.String,
            'producers_json': pl.String,
            'licensors_json': pl.String,
            'genres_json': pl.String,
            'themes_json': pl.String,
            'demographics_json': pl.String,
            'relations_json': pl.String,
            'anime_type': pl.String,
            'source': pl.String,
            'season': pl.String,
            'year': pl.Int64,
            'episodes': pl.Int64,
            'duration_minutes': pl.Int64,
            'status': pl.String,
            'background': pl.String,
            'moreinfo': pl.String,
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
        },
    )


def _encode_json(value: object) -> str:
    return msgspec.json.encode(value).decode('utf-8')


def _encode_optional_json(value: object | None) -> str | None:
    return None if value is None else _encode_json(value)


def build_canonical(
    entries: list[TenraiAnimeEntry],
    policy: EligibilityPolicy | None = None,
    *,
    tagged_anime_ids: Collection[int] = (),
    theme_additions: dict[int, tuple[str, ...]] | None = None,
    theme_removals: dict[int, tuple[str, ...]] | None = None,
) -> ProcessingResult:
    """Filter, deduplicate, canonicalize, and order a snapshot without I/O."""
    eligible, audit = filter_entries(entries, policy, tagged_anime_ids=tagged_anime_ids)
    eligible, content_rejections = filter_non_recommendable_content(eligible)
    eligible, ona_audit = cleanup_ona(eligible)
    if theme_additions or theme_removals:
        eligible = [
            _apply_theme_corrections(
                entry,
                theme_additions.get(entry.mal_id, ()) if theme_additions else (),
                theme_removals.get(entry.mal_id, ()) if theme_removals else (),
            )
            for entry in eligible
        ]
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
        policy_identity=audit.policy_identity,
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


def _apply_theme_corrections(
    entry: TenraiAnimeEntry, additions: tuple[str, ...], removals: tuple[str, ...]
) -> TenraiAnimeEntry:
    """Apply curated theme additions and removals without mutating source data."""
    normalized_removals = {normalize_label(theme) for theme in removals}
    existing_themes = [theme for theme in entry.themes if normalize_label(theme.name) not in normalized_removals]
    existing = {normalize_label(theme.name) for theme in existing_themes}
    additions_to_apply = (
        Taxonomy(0, normalize_label(name)) for name in additions if normalize_label(name) not in existing
    )
    themes = [*existing_themes, *additions_to_apply]
    return msgspec.structs.replace(entry, themes=themes)
