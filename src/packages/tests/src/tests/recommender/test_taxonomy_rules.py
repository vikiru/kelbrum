"""Policy taxonomy sets cannot reintroduce unvalidated label literals or field mixups."""

import ast
import inspect

import recommender.conflicts as conflicts
import recommender.guards as guards
import recommender.pipeline as pipeline
import recommender.post_ranking as post_ranking
import recommender.structure_policy as structure_policy
from anime_catalogue.taxonomy import Genre, Theme
from features.tags import Tag


def test_taxonomy_sets_contain_only_their_enum_members() -> None:
    for module in (conflicts, guards, post_ranking):
        for name, values in vars(module).items():
            if name.endswith('_GENRES'):
                assert isinstance(values, frozenset)
                assert all(isinstance(value, Genre) for value in values), name
            if name.endswith('_THEMES'):
                assert isinstance(values, frozenset)
                assert all(isinstance(value, Theme) for value in values), name
            if name.endswith('_TAGS') and isinstance(values, frozenset):
                assert all(isinstance(value, Tag) for value in values), name


def test_policy_modules_use_enum_members_for_all_known_labels() -> None:
    labels = {member.value for enum in (Genre, Theme, Tag) for member in enum}
    for module in (conflicts, guards, pipeline, post_ranking):
        for node in ast.walk(ast.parse(inspect.getsource(module))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert node.value not in labels, f'{module.__name__}:{node.lineno}: {node.value}'


def _taxonomy_expression(node: ast.AST) -> bool:
    if isinstance(node, ast.Name):
        name = node.id.casefold()
        return name.endswith(('_genres', '_themes', '_tags')) or name in {'genres', 'themes', 'tags', 'tag_set'}
    if isinstance(node, ast.Attribute):
        return node.attr.endswith(('_genres', '_themes', '_tags')) or node.attr in {'genres', 'themes', 'tags'}
    if isinstance(node, ast.BinOp):
        return _taxonomy_expression(node.left) or _taxonomy_expression(node.right)
    return False


def _has_string_labels(node: ast.AST) -> bool:
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {'set', 'frozenset'}:
        return any(_has_string_labels(arg) for arg in node.args)
    return isinstance(node, ast.Set) and any(
        isinstance(x, ast.Constant) and isinstance(x.value, str) for x in node.elts
    )


def test_policy_predicates_cannot_reintroduce_raw_taxonomy_strings() -> None:
    for module in (conflicts, guards, pipeline, post_ranking, structure_policy):
        for node in ast.walk(ast.parse(inspect.getsource(module))):
            if isinstance(node, ast.Compare) and any(_taxonomy_expression(x) for x in node.comparators):
                assert not (isinstance(node.left, ast.Constant) and isinstance(node.left.value, str)), node.lineno
            if isinstance(node, ast.BinOp) and _taxonomy_expression(node.left):
                assert not _has_string_labels(node.right), node.lineno
            if isinstance(node, ast.Compare) and _taxonomy_expression(node.left):
                assert not any(_has_string_labels(x) for x in node.comparators), node.lineno
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and _taxonomy_expression(node.func.value)
            ):
                assert not any(_has_string_labels(x) for x in node.args), node.lineno
