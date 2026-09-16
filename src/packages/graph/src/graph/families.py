"""Same-story family traversal algorithms."""

from collections import deque
from collections.abc import Mapping, Sequence


def bounded_family(anime_id: int, adjacency: Mapping[int, frozenset[int]], max_depth: int) -> frozenset[int]:
    """Return the nodes reachable within a configured number of hops."""
    seen = {anime_id}
    queue = deque([(anime_id, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for target in adjacency.get(current, frozenset()):
            if target not in seen:
                seen.add(target)
                queue.append((target, depth + 1))
    return frozenset(seen)


def connected_families(
    node_ids: Sequence[int],
    adjacency: Mapping[int, frozenset[int]],
) -> dict[int, frozenset[int]]:
    """Return one complete connected family for each requested node."""
    requested = set(node_ids)
    undirected: dict[int, set[int]] = {anime_id: set() for anime_id in requested}
    for source, targets in adjacency.items():
        undirected.setdefault(source, set())
        for target in targets:
            undirected.setdefault(target, set())
            undirected[source].add(target)
            undirected[target].add(source)

    families: dict[int, frozenset[int]] = {}
    unvisited = set(requested)
    while unvisited:
        root = unvisited.pop()
        component: set[int] = set()
        queue = [root]
        while queue:
            current = queue.pop()
            if current in component:
                continue
            component.add(current)
            queue.extend(target for target in undirected[current] if target not in component)
        unvisited.difference_update(component)
        family = frozenset(component.intersection(requested))
        for anime_id in family:
            families[anime_id] = family
    return families
