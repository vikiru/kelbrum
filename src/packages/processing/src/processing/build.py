"""Pure deterministic snapshot-to-canonical transformation."""

from collections.abc import Collection
from typing import Annotated

import msgspec
import polars as pl

from features.origin_language import infer_origin_language
from features.origin_language_overrides import get_manual_origin_languages
from features.tag_assignment import get_tag_assignment_registry
from features.tags import apply_tag_assignments
from fetch.contracts import Taxonomy, TenraiAnimeEntry
from processing.canonicalize import canonicalize, duration_to_minutes
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
            'manual_tags': [list(record.manual_tags) for record in records],
            'origin_language': [record.origin_language for record in records],
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
            'synopsis_state': [record.synopsis_state.value for record in records],
            'genres_state': [record.genres_state.value for record in records],
            'themes_state': [record.themes_state.value for record in records],
            'tags_state': [record.tags_state.value for record in records],
            'type_state': [record.type_state.value for record in records],
            'demographics_state': [record.demographics_state.value for record in records],
            'rating_state': [record.rating_state.value for record in records],
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
            'manual_tags': pl.List(pl.String),
            'origin_language': pl.String,
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
            'synopsis_state': pl.String,
            'genres_state': pl.String,
            'themes_state': pl.String,
            'tags_state': pl.String,
            'type_state': pl.String,
            'demographics_state': pl.String,
            'rating_state': pl.String,
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
    genre_additions: dict[int, tuple[str, ...]] | None = None,
) -> ProcessingResult:
    """Filter, deduplicate, canonicalize, and order a snapshot without I/O."""
    prepared_entries = (
        [
            _apply_theme_corrections(
                entry,
                theme_additions.get(entry.mal_id, ()) if theme_additions else (),
                theme_removals.get(entry.mal_id, ()) if theme_removals else (),
            )
            for entry in entries
        ]
        if theme_additions or theme_removals
        else entries
    )
    if genre_additions:
        prepared_entries = [
            _apply_genre_corrections(entry, genre_additions.get(entry.mal_id, ())) for entry in prepared_entries
        ]
    eligible, audit = filter_entries(prepared_entries, policy, tagged_anime_ids=tagged_anime_ids)
    eligible, content_rejections = filter_non_recommendable_content(eligible)
    eligible, ona_audit = cleanup_ona(eligible, tagged_anime_ids=tagged_anime_ids)
    removed_ids = set(audit.rejected_ids) | set(content_rejections) | set(ona_audit.removed_ids)
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
        missing_duration_ids=tuple(
            sorted({entry.mal_id for entry in prepared_entries if duration_to_minutes(entry.duration) is None})
        ),
    )
    unique: dict[int, TenraiAnimeEntry] = {}
    duplicate_ids: set[int] = set()
    for entry in eligible:
        if entry.mal_id in unique:
            duplicate_ids.add(entry.mal_id)
            continue
        unique[entry.mal_id] = entry

    synopses_by_id = {anime_id: entry.synopsis for anime_id, entry in unique.items() if entry.synopsis}
    parent_synopsis_by_id: dict[int, str] = {}
    for anime_id, entry in unique.items():
        if entry.synopsis and len(entry.synopsis.strip()) >= 90:
            continue
        for relation in getattr(entry, 'relations', ()) or ():
            relation_name = getattr(relation, 'relation', '').strip().title()
            if relation_name in ('Prequel', 'Parent Story', 'Full Story'):
                for target in getattr(relation, 'entry', ()) or ():
                    target_id = getattr(target, 'mal_id', None)
                    if target_id and target_id in synopses_by_id:
                        parent_synopsis = synopses_by_id[target_id]
                        if parent_synopsis and len(parent_synopsis.strip()) >= 90:
                            parent_synopsis_by_id[anime_id] = parent_synopsis
                            break
            if anime_id in parent_synopsis_by_id:
                break

    ordered_ids = sorted(unique)
    tags_by_id = apply_tag_assignments(ordered_ids, get_tag_assignment_registry().assignments)
    manual_origin_languages = get_manual_origin_languages()
    records = tuple(
        msgspec.structs.replace(
            canonicalize(unique[anime_id], parent_synopsis_fallback=parent_synopsis_by_id.get(anime_id)),
            manual_tags=tags_by_id.get(anime_id, ()),
            origin_language=(
                lang.value
                if (lang := infer_origin_language(unique[anime_id], manual_origin_languages).language) is not None
                else None
            ),
        )
        for anime_id in ordered_ids
    )
    return ProcessingResult(records, audit, tuple(sorted(duplicate_ids)))


def _apply_theme_corrections(
    entry: TenraiAnimeEntry, additions: tuple[str, ...], removals: tuple[str, ...]
) -> TenraiAnimeEntry:
    """Apply curated theme additions and removals without mutating source data."""
    normalized_removals = {normalize_label(theme) for theme in removals}
    source_themes = entry.themes or ()
    existing_themes = [theme for theme in source_themes if normalize_label(theme.name) not in normalized_removals]
    existing = {normalize_label(theme.name) for theme in existing_themes}
    additions_to_apply = (
        Taxonomy(0, normalize_label(name)) for name in additions if normalize_label(name) not in existing
    )
    themes = [*existing_themes, *additions_to_apply]
    return msgspec.structs.replace(entry, themes=themes)


def _apply_genre_corrections(entry: TenraiAnimeEntry, additions: tuple[str, ...]) -> TenraiAnimeEntry:
    """Add reviewed genres without mutating the source entry."""
    existing_genres = list(entry.genres or ())
    existing = {normalize_label(genre.name) for genre in existing_genres}
    additions_to_apply = (
        Taxonomy(0, normalize_label(name)) for name in additions if normalize_label(name) not in existing
    )
    return msgspec.structs.replace(entry, genres=[*existing_genres, *additions_to_apply])
