"""Product-level identity exclusions kept separate from similarity scoring."""

from collections import deque
from collections.abc import Mapping, Sequence

STRONG_SAME_STORY_RELATIONS = frozenset(
    {'Sequel', 'Prequel', 'Summary', 'Full Story', 'Alternative Version', 'Parent Story'}
)


def bounded_same_story_exclusions(
    anime_id: int,
    relations: Mapping[int, Sequence[tuple[int, str]]],
    *,
    max_depth: int = 2,
) -> frozenset[int]:
    """Return bounded transitive same-story IDs, including the anchor."""
    if max_depth < 0:
        raise ValueError('max_depth must be non-negative')
    seen = {anime_id}
    queue = deque([(anime_id, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for target, relation in relations.get(current, ()):
            if relation not in STRONG_SAME_STORY_RELATIONS or target in seen:
                continue
            seen.add(target)
            queue.append((target, depth + 1))
    return frozenset(seen)
