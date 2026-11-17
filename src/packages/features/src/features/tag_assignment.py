"""Load curated tag assignments from the local manual-tag CSV."""

import csv
from collections import defaultdict
from collections.abc import Collection
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import msgspec

from config import derive_payload_identity
from config.manual_data import MANUAL_TAGS_CSV_PATH
from features.tags import Tag, TagAssignment

TAG_ASSIGNMENTS_VERSION = 'manual-tag-csv-v1'
MANUAL_TAG_CSV_PATH = MANUAL_TAGS_CSV_PATH


def manual_tag_csv_hash(path: Path = MANUAL_TAG_CSV_PATH) -> str:
    """Return a content fingerprint for the optional tag CSV."""
    return sha256(path.read_bytes()).hexdigest() if path.is_file() else ''


class TagAssignmentRegistry(msgspec.Struct, frozen=True):
    """Versioned assignment resource consumed by feature assembly."""

    version: str
    assignments: tuple[TagAssignment, ...]

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError('tag assignment registry version cannot be empty')
        known_tag_ids = {tag_id.value for tag_id in Tag}
        unknown_tag_ids = {
            tag_id for assignment in self.assignments for tag_id in assignment.tag_ids if tag_id not in known_tag_ids
        }
        if unknown_tag_ids:
            raise ValueError(f'unknown tag IDs: {sorted(unknown_tag_ids)}')
        for assignment in self.assignments:
            if not assignment.anime_ids:
                raise ValueError('tag assignments must contain at least one anime ID')

    def identity(self) -> str:
        """Return the deterministic identity of this curated resource."""
        return derive_payload_identity(self)


def load_manual_tag_assignments(
    path: Path = MANUAL_TAG_CSV_PATH,
    *,
    known_anime_ids: Collection[int] | None = None,
) -> tuple[TagAssignment, ...]:
    """Read reviewed tag assignments and fail with the row number on invalid values."""
    if not path.is_file():
        return ()

    known_tag_ids = {tag_id.value for tag_id in Tag}
    tags_by_anime_id: dict[int, set[str]] = defaultdict(set)
    with path.open(newline='', encoding='utf-8-sig') as source:
        reader = csv.DictReader(source)
        if not {'source id', 'tags'}.issubset(reader.fieldnames or ()):
            raise ValueError(f'manual tag CSV must contain source id and tags columns: {path}')
        if len(set(reader.fieldnames or ())) != len(reader.fieldnames or ()):
            raise ValueError(f'manual tag CSV contains duplicate column names: {path}')
        for row_number, row in enumerate(reader, 2):
            anime_id = _parse_anime_id(row.get('source id'), row_number)
            if known_anime_ids is not None and anime_id not in known_anime_ids:
                raise ValueError(f'unknown source anime ID {anime_id} on row {row_number}')
            raw_tag_ids = [value.strip() for value in (row.get('tags') or '').split(',') if value.strip()]
            if not raw_tag_ids:
                continue
            tag_ids = set(raw_tag_ids)
            if len(tag_ids) != len(raw_tag_ids):
                raise ValueError(f'duplicate tag IDs on row {row_number}: {path}')
            unknown_tags = tag_ids - known_tag_ids
            if unknown_tags:
                raise ValueError(f'unknown tag IDs on row {row_number}: {sorted(unknown_tags)}')
            duplicate_tags = tag_ids & tags_by_anime_id[anime_id]
            if duplicate_tags:
                raise ValueError(
                    f'duplicate tag assignments for source anime ID {anime_id} on row {row_number}: '
                    f'{sorted(duplicate_tags)}'
                )
            tags_by_anime_id[anime_id].update(tag_ids)

    grouped_anime_ids: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for anime_id, tag_ids in tags_by_anime_id.items():
        if tag_ids:
            grouped_anime_ids[tuple(sorted(tag_ids))].append(anime_id)
    return tuple(
        TagAssignment(anime_ids=tuple(sorted(anime_ids)), tag_ids=tag_ids)
        for tag_ids, anime_ids in sorted(grouped_anime_ids.items())
    )


def _parse_anime_id(value: str | None, row_number: int) -> int:
    try:
        anime_id = int(value or '')
    except ValueError as error:
        raise ValueError(f'invalid source anime ID on row {row_number}: {value!r}') from error
    if anime_id <= 0:
        raise ValueError(f'invalid source anime ID on row {row_number}: {value!r}')
    return anime_id


@lru_cache(maxsize=1)
def get_manual_tag_assignments() -> tuple[TagAssignment, ...]:
    """Lazily load and cache the default manual tag assignments."""
    return load_manual_tag_assignments()


@lru_cache(maxsize=1)
def get_tag_assignment_registry() -> TagAssignmentRegistry:
    """Lazily build and cache the validated tag-assignment registry."""
    return TagAssignmentRegistry(TAG_ASSIGNMENTS_VERSION, get_manual_tag_assignments())


@lru_cache(maxsize=1)
def tag_assignment_registry_identity() -> str:
    """Return the cached identity of the CSV-backed tag assignments."""
    return derive_payload_identity((get_tag_assignment_registry().identity(), manual_tag_csv_hash()))
