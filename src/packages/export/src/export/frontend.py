"""Build compact frontend metadata artifacts from canonical records."""

from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from hashlib import sha256
from operator import attrgetter, itemgetter
from pathlib import Path

import msgspec

from config import frontend_data_dir
from export.artifacts import (
    write_filter_index,
    write_frontend_json,
    write_full_entries,
    write_full_entries_from_chunks,
    write_metadata_chunks,
    write_search_metadata_chunks,
)
from export.constants import DEFAULT_FEATURED_LIMIT, MINIMUM_HOMEPAGE_SCORE
from models.contracts import AnimeCardMetadata, RecommendationScore
from models.tenrai import CanonicalAnime, TenraiAnimeEntry
from processing.ratings import display_rating
from recommender.relationship_graph import RelationshipIndex

SUPPORTED_FRANCHISE_TYPES = frozenset({'tv', 'movie', 'ona'})


def to_card_metadata(record: CanonicalAnime) -> AnimeCardMetadata:
    """Convert one canonical record to the card-sized frontend contract."""
    return AnimeCardMetadata(
        mal_id=record.mal_id,
        title=record.title,
        title_english=record.title_english,
        images=record.images,
        year=record.year,
        score=record.score,
    )


def top_anime(
    records: Iterable[CanonicalAnime],
    *,
    limit: int = DEFAULT_FEATURED_LIMIT,
    relationship_index: RelationshipIndex | None = None,
) -> tuple[AnimeCardMetadata, ...]:
    """Return the highest-scoring distinct franchise groups."""
    _validate_limit(limit)
    return _rank_franchise_groups(tuple(records), relationship_index=relationship_index)[:limit]


def homepage_candidates(
    records: Iterable[CanonicalAnime],
    *,
    limit: int = DEFAULT_FEATURED_LIMIT,
    relationship_index: RelationshipIndex | None = None,
) -> tuple[AnimeCardMetadata, ...]:
    """Return eligible records scoring at least eight for the homepage."""
    _validate_limit(limit)
    return tuple(
        item
        for item in top_anime(records, limit=limit, relationship_index=relationship_index)
        if item.score is not None and item.score >= MINIMUM_HOMEPAGE_SCORE
    )


def write_featured_artifacts(
    records: Iterable[CanonicalAnime],
    output_dir: Path | None = None,
    *,
    relationship_index: RelationshipIndex | None = None,
) -> None:
    """Write card-only homepage and top-100 artifacts as minified UTF-8 JSON."""
    destination = output_dir or frontend_data_dir()
    available_records = tuple(records)
    homepage = [
        msgspec.to_builtins(item)
        for item in homepage_candidates(available_records, relationship_index=relationship_index)
    ]
    top_100 = [
        msgspec.to_builtins(item) for item in top_anime(available_records, relationship_index=relationship_index)
    ]
    write_frontend_json('homepage.json', homepage, output_dir=destination)
    write_frontend_json('top-100.json', top_100, output_dir=destination)


def _rank_franchise_groups(
    records: tuple[CanonicalAnime, ...], *, relationship_index: RelationshipIndex | None
) -> tuple[AnimeCardMetadata, ...]:
    records_by_id = {record.mal_id: record for record in records}
    supported_ids = {
        record.mal_id for record in records if (record.anime_type or '').strip().casefold() in SUPPORTED_FRANCHISE_TYPES
    }
    groups: dict[frozenset[int], list[CanonicalAnime]] = {}
    for record in records:
        is_supported_type = (record.anime_type or '').strip().casefold() in SUPPORTED_FRANCHISE_TYPES
        eligible_family = frozenset({record.mal_id})
        if is_supported_type and relationship_index is not None:
            eligible_family = frozenset(records_by_id).intersection(relationship_index.excluded_ids(record.mal_id))
            eligible_family &= supported_ids
        groups.setdefault(frozenset(eligible_family), []).append(record)

    ranked: list[tuple[float, int, AnimeCardMetadata]] = []
    for member_ids, members in groups.items():
        scored_members = [member for member in members if member.score is not None]
        scores = [member.score for member in scored_members if member.score is not None]
        if not scores:
            continue
        franchise_score = max(scores)
        display_score = round(franchise_score, 2)
        representative = _select_representative(
            scored_members,
            member_ids=member_ids,
            relationship_index=relationship_index,
        )
        ranked.append(
            (
                franchise_score,
                representative.mal_id,
                AnimeCardMetadata(
                    mal_id=representative.mal_id,
                    title=representative.title,
                    title_english=representative.title_english,
                    images=representative.images,
                    year=representative.year,
                    score=display_score,
                ),
            )
        )
    ranked.sort(key=itemgetter(1))
    ranked.sort(key=itemgetter(0), reverse=True)
    return tuple(item[2] for item in ranked)


def _select_representative(
    members: Sequence[CanonicalAnime],
    *,
    member_ids: frozenset[int],
    relationship_index: RelationshipIndex | None,
) -> CanonicalAnime:
    """Select the graph canonical origin, falling back to the lowest stable ID."""
    records_by_id = {member.mal_id: member for member in members}
    if relationship_index is not None:
        canonical_id = relationship_index.canonical_id(min(member_ids))
        canonical = records_by_id.get(canonical_id)
        if canonical is not None:
            return canonical
    return min(members, key=attrgetter('mal_id'))


def write_catalogue_artifacts(
    records: Iterable[CanonicalAnime],
    *,
    full_entries: Iterable[TenraiAnimeEntry] = (),
    recommendations: dict[int, tuple[int, ...]] | None = None,
    recommendation_scores: dict[int, tuple[RecommendationScore, ...]] | None = None,
    output_dir: Path | None = None,
    provenance: Mapping[str, object] | None = None,
    recommendation_chunks: Path | None = None,
    include_full_entries: bool = True,
) -> None:
    """Write frontend metadata, indexes, recommendations, and separate full entries."""
    destination = output_dir or frontend_data_dir()
    ordered_records = tuple(sorted(records, key=_record_id))
    accepted_ids = {record.mal_id for record in ordered_records}
    full_entries_tuple = tuple(full_entries)
    full_ids = {entry.mal_id for entry in full_entries_tuple}
    if full_ids != accepted_ids:
        raise ValueError('full-entry IDs do not match accepted processed IDs')
    _validate_full_entries(full_entries_tuple)
    recommendation_ids = set(recommendations or {})
    if recommendations is not None and recommendation_ids != accepted_ids:
        raise ValueError('recommendation IDs do not match accepted processed IDs')
    if any(candidate not in accepted_ids for values in (recommendations or {}).values() for candidate in values):
        raise ValueError('recommendations reference IDs outside the accepted processed catalogue')
    score_source_ids = set(recommendation_scores or {})
    if recommendation_scores is not None and score_source_ids != accepted_ids:
        raise ValueError('recommendation score IDs do not match accepted processed IDs')
    if any(score.anime_id not in accepted_ids for values in (recommendation_scores or {}).values() for score in values):
        raise ValueError('recommendation scores reference IDs outside the accepted processed catalogue')
    if recommendations is not None and recommendation_scores is not None:
        for source_id in accepted_ids:
            recommendation_ids_for_source = set(recommendations[source_id])
            score_ids_for_source = {score.anime_id for score in recommendation_scores[source_id]}
            if recommendation_ids_for_source != score_ids_for_source:
                raise ValueError(f'recommendation IDs and scores disagree for source {source_id}')
    metadata = tuple(msgspec.to_builtins(to_card_metadata(record)) for record in ordered_records)
    metadata_paths = write_metadata_chunks(metadata, output_dir=destination)
    write_filter_index(ordered_records, output_dir=destination)
    search_path = write_search_metadata(ordered_records, output_dir=destination)
    search_metadata_chunks = write_search_metadata_chunks(
        tuple(_search_metadata_payload(record) for record in ordered_records), output_dir=destination / 'search'
    )
    _validate_id_projection(destination / 'filter-index.json', accepted_ids, 'ids')
    _validate_id_projection(search_path, accepted_ids, 'keys')
    if include_full_entries and recommendation_chunks is not None:
        full_paths = write_full_entries_from_chunks(
            full_entries_tuple, output_dir=destination, recommendation_chunks=recommendation_chunks
        )
    elif include_full_entries:
        full_paths = write_full_entries(
            full_entries_tuple,
            output_dir=destination,
            recommendations=recommendations,
            recommendation_scores=recommendation_scores,
        )
    else:
        full_paths = ()
    if full_paths:
        _validate_full_projection(full_paths, accepted_ids)
    files = (*metadata_paths, search_path, *search_metadata_chunks, *full_paths, destination / 'filter-index.json')
    provenance_payload = dict(provenance or {})
    build_identity = sha256(msgspec.json.encode(provenance_payload)).hexdigest()
    recommendation_source_count = (
        len(recommendations)
        if recommendations is not None
        else len(ordered_records)
        if recommendation_chunks is not None
        else 0
    )
    write_frontend_json(
        'artifact-manifest.json',
        {
            'schema_version': 'frontend-artifacts-v1',
            'generated_at': datetime.now(UTC).isoformat(),
            'metadata_count': len(metadata),
            'full_entry_count': len(full_entries_tuple),
            'recommendation_source_count': recommendation_source_count,
            'metadata_files': [path.name for path in metadata_paths],
            'full_files': [path.name for path in full_paths],
            'files': [_file_manifest(path, destination) for path in files],
            'search_metadata': 'search/anime-metadata-search.json',
            'search_metadata_chunks': [path.relative_to(destination).as_posix() for path in search_metadata_chunks],
            'build_identity': build_identity,
            'provenance': provenance_payload,
        },
        output_dir=destination,
    )


def write_search_metadata(records: Iterable[CanonicalAnime], *, output_dir: Path) -> Path:
    """Write the Python-owned search/filter projection consumed by frontend indexing."""
    payload = {str(record.mal_id): _search_metadata_payload(record) for record in sorted(records, key=_record_id)}
    return write_frontend_json('anime-metadata-search.json', payload, output_dir=output_dir / 'search')


def _search_metadata_payload(record: CanonicalAnime) -> dict[str, object]:
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


def _file_manifest(path: Path, root: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        'path': path.relative_to(root).as_posix(),
        'bytes': len(data),
        'sha256': sha256(data).hexdigest(),
    }


def _validate_id_projection(path: Path, expected_ids: set[int], mode: str) -> None:
    payload = msgspec.json.decode(path.read_bytes())
    if not isinstance(payload, dict):
        raise TypeError(f'{path.name} must contain an object')
    if mode == 'ids':
        values = payload.get('ids')
        actual_ids = {int(value) for value in values} if isinstance(values, list) else set()
    else:
        actual_ids = {int(value) for value in payload}
    if actual_ids != expected_ids:
        raise ValueError(f'{path.name} IDs do not match accepted processed IDs')


def _validate_full_projection(paths: Sequence[Path], expected_ids: set[int]) -> None:
    actual_ids: set[int] = set()
    for path in paths:
        payload = msgspec.json.decode(path.read_bytes())
        if not isinstance(payload, dict):
            raise TypeError(f'{path.name} must contain an object')
        actual_ids.update(int(anime_id) for anime_id in payload)
    if actual_ids != expected_ids:
        missing_ids = sorted(expected_ids - actual_ids)
        extra_ids = sorted(actual_ids - expected_ids)
        raise ValueError(
            f'full-entry IDs do not match accepted processed IDs; missing={missing_ids[:10]}, extra={extra_ids[:10]}'
        )


def _validate_full_entries(entries: Sequence[TenraiAnimeEntry]) -> None:
    if any(not entry.title.strip() or entry.mal_id <= 0 for entry in entries):
        raise ValueError('full entries contain invalid identity fields')
    if any(entry.type is None or entry.genres is None or entry.themes is None for entry in entries):
        raise ValueError('full entries are missing required Tenrai fields')


def _record_id(record: CanonicalAnime) -> int:
    return record.mal_id


def _validate_limit(limit: int) -> None:
    if limit < 1:
        raise ValueError('limit must be positive')
