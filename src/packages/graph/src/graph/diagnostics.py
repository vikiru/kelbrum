"""Bounded graph diagnostics and stable identity generation."""

from collections.abc import Mapping, Sequence
from hashlib import sha256

import orjson

from graph.contracts import GraphRelation


def render_graph(
    canonical_by_id: Mapping[int, int],
    family_by_id: Mapping[int, frozenset[int]],
    relations_by_id: Mapping[int, Sequence[GraphRelation]],
    anime_id: int | None = None,
) -> str:
    """Render one node or the complete graph for bounded diagnostics."""
    ids = (anime_id,) if anime_id is not None else tuple(sorted(canonical_by_id))
    lines: list[str] = []
    for current_id in ids:
        relations = (
            ', '.join(f'{relation.target_id} [{relation.relation}]' for relation in relations_by_id.get(current_id, ()))
            or 'none'
        )
        family = ', '.join(str(member) for member in sorted(family_by_id.get(current_id, {current_id})))
        lines.append(
            f'{current_id} → canonical {canonical_by_id.get(current_id, current_id)}; '
            f'family {{{family}}}; relations: {relations}'
        )
    return '\n'.join(lines)


def graph_fingerprint(
    family_by_id: Mapping[int, frozenset[int]],
    canonical_by_id: Mapping[int, int],
    relations_by_id: Mapping[int, Sequence[GraphRelation]],
    franchise_by_id: Mapping[int, frozenset[int]] | None = None,
    media_type_by_id: Mapping[int, str | None] | None = None,
) -> str:
    """Return a stable identity for graph families and retained edges."""
    payload = {
        'canonical_by_id': sorted(canonical_by_id.items()),
        'family_by_id': sorted((key, sorted(family)) for key, family in family_by_id.items()),
        'relations_by_id': sorted(
            (key, sorted((relation.target_id, relation.relation) for relation in values))
            for key, values in relations_by_id.items()
        ),
        'franchise_by_id': sorted((key, sorted(family)) for key, family in (franchise_by_id or {}).items()),
        'media_type_by_id': sorted((key, value) for key, value in (media_type_by_id or {}).items()),
    }
    return sha256(orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)).hexdigest()
