"""Domain-specific frontend artifact projections."""

from collections.abc import Mapping, Sequence
from pathlib import Path

import msgspec

from export.constants import (
    DEFAULT_FULL_ENTRY_CHUNK_SIZE,
    DEFAULT_METADATA_CHUNK_SIZE,
    DEFAULT_SEARCH_METADATA_CHUNK_SIZE,
    FILTER_CATEGORICAL_FIELDS,
    FILTER_NUMERIC_FIELDS,
    MAX_FULL_ENTRY_CHUNK_SIZE,
    MIN_FULL_ENTRY_CHUNK_SIZE,
)
from models.contracts import RecommendationScore
from models.labels import display_label
from models.tenrai import CanonicalAnime, TenraiAnimeEntry
from processing.canonicalize import duration_to_minutes
from processing.ratings import display_rating
from storage.json_io import write_json


def write_frontend_json(filename: str, value: object, *, output_dir: Path) -> Path:
    """Write one frontend JSON artifact beneath the supplied data directory."""
    if not filename.endswith('.json') or Path(filename).name != filename:
        raise ValueError('frontend artifact filename must be a plain .json filename')
    destination = output_dir / filename
    write_json(destination, value)
    return destination


def write_metadata_chunks(
    metadata: Sequence[object], *, output_dir: Path, chunk_size: int = DEFAULT_METADATA_CHUNK_SIZE
) -> tuple[Path, ...]:
    """Write deterministic card/search metadata chunks for bounded frontend loading."""
    if chunk_size < 1:
        raise ValueError('chunk_size must be positive')
    return tuple(
        write_frontend_json(
            f'metadata-{bucket_start}-{bucket_start + chunk_size - 1}.json',
            {str(_metadata_id(metadata[index])): metadata[index] for index in indexes},
            output_dir=output_dir,
        )
        for bucket_start, indexes in _metadata_buckets(metadata, chunk_size)
    )


def write_search_metadata_chunks(
    metadata: Sequence[object], *, output_dir: Path, chunk_size: int = DEFAULT_SEARCH_METADATA_CHUNK_SIZE
) -> tuple[Path, ...]:
    """Write search metadata in deterministic ID-range chunks for paginated loading."""
    if chunk_size < 1:
        raise ValueError('chunk_size must be positive')
    return tuple(
        write_frontend_json(
            f'anime-metadata-{bucket_start}-{bucket_start + chunk_size - 1}.json',
            {str(_metadata_id(metadata[index])): metadata[index] for index in indexes},
            output_dir=output_dir,
        )
        for bucket_start, indexes in _metadata_buckets(metadata, chunk_size)
    )


def write_filter_index(records: Sequence[CanonicalAnime], *, output_dir: Path) -> Path:
    """Write aligned numeric arrays and categorical ID postings for frontend filters."""
    numeric: dict[str, list[object]] = {field: [] for field in FILTER_NUMERIC_FIELDS}
    categorical: dict[str, dict[str, list[int]]] = {field: {} for field in FILTER_CATEGORICAL_FIELDS}
    ordered_records = sorted(records, key=_canonical_id)
    if len({record.mal_id for record in ordered_records}) != len(ordered_records):
        raise ValueError('filter-index records must have unique MAL IDs')
    for record in ordered_records:
        for field in numeric:
            numeric[field].append(getattr(record, field))
        _add_posting(categorical['anime_type'], record.anime_type, record.mal_id)
        _add_posting(categorical['rating'], display_rating(record.rating), record.mal_id)
        for item in record.demographics:
            _add_posting(categorical['demographic'], display_label(item.name), record.mal_id)
        for item in record.genres:
            _add_posting(categorical['genre'], display_label(item.name), record.mal_id)
        for item in record.themes:
            _add_posting(categorical['theme'], display_label(item.name), record.mal_id)
    for postings in categorical.values():
        for anime_ids in postings.values():
            anime_ids.sort()
    return write_frontend_json(
        'filter-index.json',
        {'ids': [record.mal_id for record in ordered_records], 'numeric': numeric, 'categorical': categorical},
        output_dir=output_dir,
    )


def write_full_entries(
    entries: Sequence[TenraiAnimeEntry],
    *,
    output_dir: Path,
    recommendations: Mapping[int, Sequence[int]] | None = None,
    recommendation_scores: Mapping[int, Sequence[RecommendationScore]] | None = None,
    chunk_size: int = DEFAULT_FULL_ENTRY_CHUNK_SIZE,
) -> tuple[Path, ...]:
    """Write detail entries and recommendation IDs in bounded frontend data chunks."""
    _validate_full_entry_chunk_size(chunk_size)
    del recommendation_scores
    recommendation_map = recommendations or {}
    ordered_entries = sorted(entries, key=_entry_id)
    paths: list[Path] = []
    for bucket_start, indexes in _entry_buckets(ordered_entries, chunk_size):
        payload = {
            str(ordered_entries[index].mal_id): _full_entry_payload(
                ordered_entries[index], recommendation_map.get(ordered_entries[index].mal_id, ())
            )
            for index in indexes
        }
        paths.append(
            write_frontend_json(
                f'full-{bucket_start}-{bucket_start + chunk_size - 1}.json',
                payload,
                output_dir=output_dir / 'full',
            )
        )
    return tuple(paths)


def write_full_entries_from_chunks(
    entries: Sequence[TenraiAnimeEntry],
    *,
    output_dir: Path,
    recommendation_chunks: Path,
    chunk_size: int = DEFAULT_FULL_ENTRY_CHUNK_SIZE,
) -> tuple[Path, ...]:
    """Write full entries while loading one recommendation checkpoint at a time."""
    _validate_full_entry_chunk_size(chunk_size)
    ordered_entries = sorted(entries, key=_entry_id)
    manifest = msgspec.json.decode((recommendation_chunks / 'manifest.json').read_bytes(), type=dict[str, object])
    chunk_ids = manifest.get('chunk_ids')
    if not isinstance(chunk_ids, dict):
        raise TypeError('recommendation manifest is missing chunk IDs')
    entry_to_chunk = {
        int(anime_id): int(chunk_number)
        for chunk_number, anime_ids in chunk_ids.items()
        if isinstance(anime_ids, list)
        for anime_id in anime_ids
    }
    paths: list[Path] = []
    cached_chunk_number: int | None = None
    cached_recommendations: Mapping[int, Sequence[int]] = {}
    for bucket_start, indexes in _entry_buckets(ordered_entries, chunk_size):
        chunk = [ordered_entries[index] for index in indexes]
        payload: dict[str, object] = {}
        for entry in chunk:
            recommendation_chunk_number = entry_to_chunk.get(entry.mal_id)
            if recommendation_chunk_number is None:
                raise ValueError(f'entry {entry.mal_id} has no recommendation chunk')
            if recommendation_chunk_number != cached_chunk_number:
                cached_chunk_number = recommendation_chunk_number
                path = recommendation_chunks / f'chunk-{cached_chunk_number:04d}.json'
                cached_recommendations = _read_recommendation_chunk(path)
            payload[str(entry.mal_id)] = _full_entry_payload(
                entry,
                cached_recommendations.get(entry.mal_id, ()),
            )
        paths.append(
            write_frontend_json(
                f'full-{bucket_start}-{bucket_start + chunk_size - 1}.json',
                payload,
                output_dir=output_dir / 'full',
            )
        )
    return tuple(paths)


def _read_recommendation_chunk(path: Path) -> Mapping[int, Sequence[int]]:
    if not path.is_file():
        raise FileNotFoundError(f'missing recommendation chunk: {path}')
    return msgspec.json.decode(path.read_bytes(), type=dict[int, tuple[int, ...]])


def _add_posting(postings: dict[str, list[int]], value: str | None, anime_id: int) -> None:
    if value:
        postings.setdefault(value, []).append(anime_id)


def _validate_full_entry_chunk_size(chunk_size: int) -> None:
    if not MIN_FULL_ENTRY_CHUNK_SIZE <= chunk_size <= MAX_FULL_ENTRY_CHUNK_SIZE:
        raise ValueError(f'chunk_size must be between {MIN_FULL_ENTRY_CHUNK_SIZE} and {MAX_FULL_ENTRY_CHUNK_SIZE}')


def _full_entry_payload(
    entry: TenraiAnimeEntry,
    recommendations: Sequence[int],
) -> dict[str, object]:
    payload = msgspec.to_builtins(entry)
    if not isinstance(payload, dict):
        raise TypeError('Tenrai full entry did not encode as an object')
    payload['rating'] = display_rating(entry.rating)
    payload['genres'] = [{**item, 'name': display_label(item['name'])} for item in payload.get('genres', [])]
    payload['themes'] = [{**item, 'name': display_label(item['name'])} for item in payload.get('themes', [])]
    payload['durationMinutes'] = duration_to_minutes(entry.duration)
    payload['recommendations'] = list(dict.fromkeys(recommendations))
    payload.pop('recommendationScores', None)
    payload.pop('recommendationExplanations', None)
    return payload


def _entry_id(entry: TenraiAnimeEntry) -> int:
    return entry.mal_id


def _canonical_id(record: CanonicalAnime) -> int:
    return record.mal_id


def _metadata_id(metadata: object) -> int:
    if not isinstance(metadata, dict) or not isinstance(metadata.get('malId'), int):
        raise TypeError('metadata must contain an integer malId')
    return metadata['malId']


def _metadata_buckets(metadata: Sequence[object], width: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
    buckets: dict[int, list[int]] = {}
    for index, item in enumerate(metadata):
        item_id = _metadata_id(item)
        bucket_start = ((item_id - 1) // width) * width + 1
        buckets.setdefault(bucket_start, []).append(index)
    return tuple((start, tuple(indexes)) for start, indexes in sorted(buckets.items()))


def _entry_buckets(entries: Sequence[TenraiAnimeEntry], width: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
    buckets: dict[int, list[int]] = {}
    for index, entry in enumerate(entries):
        bucket_start = ((entry.mal_id - 1) // width) * width + 1
        buckets.setdefault(bucket_start, []).append(index)
    return tuple((start, tuple(indexes)) for start, indexes in sorted(buckets.items()))
