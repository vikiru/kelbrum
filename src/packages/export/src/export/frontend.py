"""Build compact frontend metadata artifacts from canonical records."""

from collections.abc import Iterable
from pathlib import Path

import msgspec

from export.artifacts import write_frontend_json
from export.featured import homepage_candidates, top_anime
from graph import RelationshipIndex
from processing.contracts import CanonicalAnime


def write_featured_artifacts(
    records: Iterable[CanonicalAnime],
    *,
    output_dir: Path,
    relationship_index: RelationshipIndex | None = None,
) -> tuple[Path, Path]:
    """Write card-only homepage and top-100 artifacts as minified UTF-8 JSON."""
    available_records = tuple(records)
    homepage = [
        msgspec.to_builtins(item)
        for item in homepage_candidates(available_records, relationship_index=relationship_index)
    ]
    top_100 = [
        msgspec.to_builtins(item) for item in top_anime(available_records, relationship_index=relationship_index)
    ]
    homepage_path = write_frontend_json('homepage.json', homepage, output_dir=output_dir)
    top_100_path = write_frontend_json('top-100.json', top_100, output_dir=output_dir)
    return homepage_path, top_100_path
