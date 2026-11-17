"""Featured catalogue selection policies."""

from collections.abc import Iterable, Sequence
from operator import itemgetter

from export.constants import DEFAULT_FEATURED_LIMIT, MINIMUM_HOMEPAGE_SCORE
from export.contracts import AnimeCardMetadata
from fetch.types import MediaType
from graph import RelationshipIndex
from processing.contracts import CanonicalAnime

SUPPORTED_FRANCHISE_TYPES = frozenset({MediaType.TV, MediaType.MOVIE, MediaType.ONA})


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
    """Return eligible records scoring at least the homepage threshold."""
    _validate_limit(limit)
    return tuple(
        item
        for item in top_anime(records, limit=limit, relationship_index=relationship_index)
        if item.score is not None and item.score >= MINIMUM_HOMEPAGE_SCORE
    )


def _rank_franchise_groups(
    records: tuple[CanonicalAnime, ...], *, relationship_index: RelationshipIndex | None
) -> tuple[AnimeCardMetadata, ...]:
    """Group eligible records, retain each group's strongest score, and rank it."""
    records_by_id = {record.mal_id: record for record in records}
    supported_ids = {
        record.mal_id for record in records if (record.anime_type or '').strip().upper() in SUPPORTED_FRANCHISE_TYPES
    }
    groups: dict[frozenset[int], list[CanonicalAnime]] = {}
    for record in records:
        is_supported_type = (record.anime_type or '').strip().upper() in SUPPORTED_FRANCHISE_TYPES
        eligible_family = frozenset({record.mal_id})
        if is_supported_type and relationship_index is not None:
            eligible_family = frozenset(records_by_id).intersection(relationship_index.franchise_members(record.mal_id))
            eligible_family &= supported_ids
        groups.setdefault(frozenset(eligible_family), []).append(record)

    ranked: list[tuple[float, int, AnimeCardMetadata]] = []
    for members in groups.values():
        scored_members = [member for member in members if member.score is not None]
        scores = [member.score for member in scored_members if member.score is not None]
        if not scores:
            continue
        franchise_score = max(scores)
        representative = _select_representative(
            members,
            strongest_member=min(scored_members, key=lambda member: (-(member.score or 0.0), member.mal_id)),
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
                    score=round(franchise_score, 2),
                ),
            )
        )
    ranked.sort(key=itemgetter(1))
    ranked.sort(key=itemgetter(0), reverse=True)
    return tuple(item[2] for item in ranked)


def _select_representative(
    members: Sequence[CanonicalAnime],
    *,
    strongest_member: CanonicalAnime,
    relationship_index: RelationshipIndex | None,
) -> CanonicalAnime:
    """Select the strongest story's entrypoint, falling back to that title."""
    records_by_id = {member.mal_id: member for member in members}
    if relationship_index is not None:
        entrypoint_id = relationship_index.story_line_entrypoint(strongest_member.mal_id)
        canonical = records_by_id.get(entrypoint_id)
        if canonical is not None:
            return canonical
    return strongest_member


def _validate_limit(limit: int) -> None:
    """Reject empty featured-artifact requests."""
    if limit < 1:
        raise ValueError('limit must be positive')
