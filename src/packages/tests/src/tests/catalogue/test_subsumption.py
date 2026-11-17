"""Tests for taxonomy subsumption DAG and pruning."""

from anime_catalogue.subsumption import (
    ANCESTORS_BY_TOKEN,
    SIBLING_TRANSFER_FACTOR,
    SIBLINGS_BY_TOKEN,
    compute_sibling_hypernym,
    prune_ancestor_tokens,
)
from anime_catalogue.tags import Tag
from anime_catalogue.taxonomy import Genre, Theme


def test_ancestor_lookup_contains_transitive_parents() -> None:
    # Tag.BASEBALL -> Theme.TEAM_SPORTS -> Genre.SPORTS
    baseball_ancestors = ANCESTORS_BY_TOKEN.get(Tag.BASEBALL, frozenset())
    assert Theme.TEAM_SPORTS in baseball_ancestors
    assert Genre.SPORTS in baseball_ancestors


def test_prune_ancestor_tokens_removes_redundant_hypernyms() -> None:
    # When baseball, team_sports, and sports are all present, keep only baseball
    tokens = {Tag.BASEBALL, Theme.TEAM_SPORTS, Genre.SPORTS}
    pruned = prune_ancestor_tokens(tokens)
    assert pruned == {Tag.BASEBALL}


def test_prune_ancestor_tokens_preserves_orthogonal_tokens() -> None:
    # Baseball and Romance have no ancestor relationship
    tokens = {Tag.BASEBALL, Genre.ROMANCE}
    pruned = prune_ancestor_tokens(tokens)
    assert pruned == {Tag.BASEBALL, Genre.ROMANCE}


def test_compute_sibling_hypernym_for_sports() -> None:
    # Baseball and Volleyball share Theme.TEAM_SPORTS
    lca = compute_sibling_hypernym(Tag.BASEBALL, Tag.VOLLEYBALL)
    assert lca == Theme.TEAM_SPORTS


def test_compute_sibling_hypernym_for_unrelated_tokens() -> None:
    lca = compute_sibling_hypernym(Tag.BASEBALL, Theme.GORE)
    assert lca is None


def test_sibling_transfer_factor_is_valid() -> None:
    assert 0.0 < SIBLING_TRANSFER_FACTOR < 1.0


def test_cross_enum_tokens_do_not_collide_in_subsumption_lookups() -> None:
    assert ANCESTORS_BY_TOKEN.get(Genre.GOURMET) is None
    assert Genre.GOURMET in prune_ancestor_tokens((Genre.GOURMET, Tag.COOKING))
    assert Theme.GOURMET not in prune_ancestor_tokens((Theme.GOURMET, Tag.COOKING))
    assert compute_sibling_hypernym(Genre.GOURMET, Tag.COOKING) is None
    assert compute_sibling_hypernym(Genre.DETECTIVE, Theme.DETECTIVE) == Genre.MYSTERY
    assert SIBLINGS_BY_TOKEN[Genre.DETECTIVE][Theme.DETECTIVE] == Genre.MYSTERY
