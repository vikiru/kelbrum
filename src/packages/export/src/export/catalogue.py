"""Build catalogue and search projections for frontend consumers."""

from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path

import msgspec

from config import derive_payload_identity
from export.artifacts import (
    write_filter_index,
    write_frontend_json,
    write_full_entries,
    write_full_entries_from_chunks,
    write_metadata_chunks,
    write_search_metadata_chunks,
)
from export.contracts import FrontendArtifactManifest, FrontendProvenance
from export.featured import to_card_metadata
from export.manifest import file_manifest, validate_full_entries, validate_full_projection, validate_id_projection
from fetch.contracts import TenraiAnimeEntry
from processing.contracts import CanonicalAnime
from processing.ratings import display_rating


class CatalogueProjections(msgspec.Struct, frozen=True):
    """Paths for fast catalogue projections prepared before slow exports."""

    metadata_paths: tuple[Path, ...]
    search_path: Path
    search_metadata_chunks: tuple[Path, ...]


def write_catalogue_artifacts(
    records: Iterable[CanonicalAnime],
    *,
    full_entries: Iterable[TenraiAnimeEntry] = (),
    recommendations: dict[int, tuple[int, ...]] | None = None,
    output_dir: Path,
    provenance: FrontendProvenance | None = None,
    recommendation_chunks: Path | None = None,
    include_full_entries: bool = True,
    featured_paths: Sequence[Path] = (),
    projections: CatalogueProjections | None = None,
) -> None:
    """Write catalogue metadata, indexes, recommendations, and full entries."""
    ordered_records = tuple(sorted(records, key=_record_id))
    _validate_unique_ids((record.mal_id for record in ordered_records), 'processed records')
    accepted_ids = {record.mal_id for record in ordered_records}
    full_entries_tuple = tuple(full_entries)
    _validate_export_inputs(
        full_entries_tuple,
        accepted_ids,
        recommendations,
        include_full_entries=include_full_entries,
    )
    _invalidate_previous_manifest(output_dir)
    active_projections = projections or write_catalogue_projections(ordered_records, output_dir=output_dir)
    validate_id_projection(output_dir / 'filter-index.json', accepted_ids, 'ids')
    validate_id_projection(active_projections.search_path, accepted_ids, 'keys')
    if include_full_entries and recommendation_chunks is not None:
        full_paths = write_full_entries_from_chunks(
            full_entries_tuple, output_dir=output_dir, recommendation_chunks=recommendation_chunks
        )
    elif include_full_entries:
        full_paths = write_full_entries(
            full_entries_tuple,
            output_dir=output_dir,
            recommendations=recommendations,
        )
    else:
        full_paths = ()
    if full_paths:
        validate_full_projection(full_paths, accepted_ids)
    files = _artifact_paths(
        featured_paths,
        active_projections.metadata_paths,
        active_projections.search_path,
        active_projections.search_metadata_chunks,
        full_paths,
        output_dir,
    )
    provenance_payload: dict[str, object] = msgspec.to_builtins(provenance) if provenance is not None else {}
    build_identity = derive_payload_identity(provenance_payload)
    recommendation_source_count = _recommendation_source_count(
        recommendations,
        recommendation_chunks,
        len(ordered_records),
    )
    manifest = FrontendArtifactManifest(
        schema_version='frontend-artifacts-v1',
        generated_at=datetime.now(UTC).isoformat(),
        metadata_count=len(ordered_records),
        full_entry_count=len(full_entries_tuple) if include_full_entries else 0,
        recommendation_source_count=recommendation_source_count,
        metadata_files=tuple(path.name for path in active_projections.metadata_paths),
        full_files=tuple(path.name for path in full_paths),
        files=tuple(file_manifest(path, output_dir) for path in files),
        search_metadata='search/anime-metadata-search.json',
        search_metadata_chunks=tuple(
            path.relative_to(output_dir).as_posix() for path in active_projections.search_metadata_chunks
        ),
        build_identity=build_identity,
        provenance=provenance_payload,
    )
    write_frontend_json('artifact-manifest.json', msgspec.to_builtins(manifest), output_dir=output_dir)


def write_catalogue_projections(records: Sequence[CanonicalAnime], *, output_dir: Path) -> CatalogueProjections:
    """Write fast catalogue projections without recommendations or full entries."""
    ordered_records = tuple(sorted(records, key=_record_id))
    metadata = tuple(msgspec.to_builtins(to_card_metadata(record)) for record in ordered_records)
    metadata_paths = write_metadata_chunks(metadata, output_dir=output_dir)
    write_filter_index(ordered_records, output_dir=output_dir)
    search_path = write_search_metadata(ordered_records, output_dir=output_dir)
    search_metadata_chunks = write_search_metadata_chunks(
        tuple(_search_metadata_payload(record) for record in ordered_records), output_dir=output_dir / 'search'
    )
    return CatalogueProjections(metadata_paths, search_path, search_metadata_chunks)


def _artifact_paths(
    featured_paths: Sequence[Path],
    metadata_paths: Sequence[Path],
    search_path: Path,
    search_metadata_chunks: Sequence[Path],
    full_paths: Sequence[Path],
    output_dir: Path,
) -> tuple[Path, ...]:
    """Return every shipped frontend file in manifest order."""
    return (
        *featured_paths,
        *metadata_paths,
        search_path,
        *search_metadata_chunks,
        *full_paths,
        output_dir / 'filter-index.json',
    )


def _recommendation_source_count(
    recommendations: Mapping[int, Sequence[int]] | None,
    recommendation_chunks: Path | None,
    record_count: int,
) -> int:
    """Return the number of recommendation sources represented by the export."""
    if recommendations is not None:
        return len(recommendations)
    return record_count if recommendation_chunks is not None else 0


def _invalidate_previous_manifest(output_dir: Path) -> None:
    """Remove the previous commit marker before beginning a new export."""
    (output_dir / 'artifact-manifest.json').unlink(missing_ok=True)


def _validate_export_inputs(
    full_entries: tuple[TenraiAnimeEntry, ...],
    accepted_ids: set[int],
    recommendations: dict[int, tuple[int, ...]] | None,
    *,
    include_full_entries: bool,
) -> None:
    """Validate that every exported projection uses the accepted catalogue IDs."""
    if include_full_entries:
        _validate_unique_ids((entry.mal_id for entry in full_entries), 'full entries')
        if {entry.mal_id for entry in full_entries} != accepted_ids:
            raise ValueError('full-entry IDs do not match accepted processed IDs')
        validate_full_entries(full_entries)
    _validate_recommendations(recommendations, accepted_ids)


def _validate_recommendations(
    recommendations: dict[int, tuple[int, ...]] | None,
    accepted_ids: set[int],
) -> None:
    """Validate recommendation source and candidate alignment."""
    recommendation_ids = set(recommendations or {})
    if recommendations is not None and recommendation_ids != accepted_ids:
        raise ValueError('recommendation IDs do not match accepted processed IDs')
    if any(candidate not in accepted_ids for values in (recommendations or {}).values() for candidate in values):
        raise ValueError('recommendations reference IDs outside the accepted processed catalogue')


def _validate_unique_ids(ids: Iterable[int], label: str) -> None:
    """Reject duplicate or non-positive IDs before building keyed projections."""
    values = tuple(ids)
    if any(anime_id <= 0 for anime_id in values):
        raise ValueError(f'{label} require positive anime IDs')
    if len(values) != len(set(values)):
        raise ValueError(f'{label} must have unique anime IDs')


def write_search_metadata(records: Iterable[CanonicalAnime], *, output_dir: Path) -> Path:
    """Write the Python-owned search projection consumed by frontend indexing."""
    payload = {str(record.mal_id): _search_metadata_payload(record) for record in sorted(records, key=_record_id)}
    return write_frontend_json('anime-metadata-search.json', payload, output_dir=output_dir / 'search')


def _search_metadata_payload(record: CanonicalAnime) -> dict[str, object]:
    """Project one processed record into the compact search index payload."""
    return {
        'malId': record.mal_id,
        'images': msgspec.to_builtins(record.images),
        'title': record.title,
        'titleEnglish': record.title_english,
        'titleJapanese': record.title_japanese,
        'year': record.year,
        'score': record.score,
        'episodes': record.episodes,
        'type': record.anime_type,
        'rating': display_rating(record.rating),
        'genres': [item.name for item in record.genres],
        'themes': [item.name for item in record.themes],
        'demographics': [item.name for item in record.demographics],
        'studios': [item.name for item in record.studios],
    }


def _record_id(record: CanonicalAnime) -> int:
    """Return the stable sort key for a processed catalogue record."""
    return record.mal_id
