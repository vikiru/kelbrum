"""Bounded graph diagnostics and stable identity generation."""

from collections.abc import Mapping, Sequence
from hashlib import sha256

import msgspec
import orjson

from graph.contracts import EdgeAssertion, GraphRelation, IdentityEquivalenceAssertion


def render_graph(
    identity_by_id: Mapping[int, int],
    members_by_id: Mapping[int, frozenset[int]],
    relations_by_id: Mapping[int, Sequence[GraphRelation]],
    anime_id: int | None = None,
) -> str:
    """Render one node or the complete graph for bounded diagnostics."""
    ids = (anime_id,) if anime_id is not None else tuple(sorted(identity_by_id))
    lines: list[str] = []
    for current_id in ids:
        relations = (
            ', '.join(f'{relation.target_id} [{relation.relation}]' for relation in relations_by_id.get(current_id, ()))
            or 'none'
        )
        members = ', '.join(str(member) for member in sorted(members_by_id.get(current_id, {current_id})))
        lines.append(
            f'{current_id} → recommendation entity {identity_by_id.get(current_id, current_id)}; '
            f'identity members {{{members}}}; relations: {relations}'
        )
    return '\n'.join(lines)


def graph_fingerprint(
    identity_by_id: Mapping[int, int],
    identity_members_by_id: Mapping[int, frozenset[int]],
    exclusions_by_id: Mapping[int, frozenset[int]],
    exclusion_paths_by_pair: Mapping[tuple[int, int], tuple[EdgeAssertion, ...]],
    relations_by_id: Mapping[int, Sequence[GraphRelation]],
    franchise_by_id: Mapping[int, frozenset[int]],
    media_type_by_id: Mapping[int, str | None],
    edge_assertions: Sequence[EdgeAssertion],
    identity_assertions: Sequence[IdentityEquivalenceAssertion],
    raw_version: str,
    identity_policy_version: str,
    same_story_policy_version: str,
    franchise_policy_version: str,
    story_line_entrypoint_by_id: Mapping[int, int] | None = None,
    story_line_members_by_id: Mapping[int, frozenset[int]] | None = None,
) -> str:
    """Return a stable identity for relationship evidence and independent policies."""
    payload = {
        'recommendation_entity_by_id': sorted(identity_by_id.items()),
        'recommendation_members_by_id': sorted(
            (key, sorted(members)) for key, members in identity_members_by_id.items()
        ),
        'story_line_entrypoint_by_id': sorted((story_line_entrypoint_by_id or {}).items()),
        'story_line_members_by_id': sorted(
            (key, sorted(members)) for key, members in (story_line_members_by_id or {}).items()
        ),
        'exclusions_by_id': sorted((key, sorted(members)) for key, members in exclusions_by_id.items()),
        'exclusion_paths_by_pair': sorted(
            (source, target, [edge.source_record_id for edge in path])
            for (source, target), path in exclusion_paths_by_pair.items()
        ),
        'relations_by_id': sorted(
            (key, sorted((relation.target_id, relation.relation) for relation in values))
            for key, values in relations_by_id.items()
        ),
        'franchise_by_id': sorted((key, sorted(family)) for key, family in franchise_by_id.items()),
        'media_type_by_id': sorted(media_type_by_id.items()),
        'edge_assertions': [msgspec.to_builtins(edge) for edge in edge_assertions],
        'identity_assertions': [msgspec.to_builtins(edge) for edge in identity_assertions],
        'raw_relationship_version': raw_version,
        'identity_policy_version': identity_policy_version,
        'same_story_policy_version': same_story_policy_version,
        'franchise_policy_version': franchise_policy_version,
    }
    return sha256(orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)).hexdigest()
