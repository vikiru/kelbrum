from pathlib import Path

import pytest

from features.tag_assignment import load_manual_tag_assignments


def test_manual_tag_loader_preserves_multirow_assignments(tmp_path: Path) -> None:
    path = tmp_path / 'manual-tags.csv'
    path.write_text('source id,tags\n10,immortality\n10,revenge\n11,\n', encoding='utf-8')

    assignments = load_manual_tag_assignments(path, known_anime_ids={10, 11})

    assert [(item.anime_ids, item.tag_ids) for item in assignments] == [((10,), ('immortality', 'revenge'))]


@pytest.mark.parametrize(
    'rows',
    ['10,"immortality,immortality"\n', '10,immortality\n10,immortality\n'],
)
def test_manual_tag_loader_rejects_duplicate_tag_assignments(tmp_path: Path, rows: str) -> None:
    path = tmp_path / 'manual-tags.csv'
    path.write_text(f'source id,tags\n{rows}', encoding='utf-8')

    with pytest.raises(ValueError, match='duplicate tag'):
        load_manual_tag_assignments(path, known_anime_ids={10})


@pytest.mark.parametrize(
    ('row', 'known_ids', 'error'),
    [
        ('oops,immortality', {10}, 'invalid source anime ID'),
        ('-1,immortality', {-1}, 'invalid source anime ID'),
        ('10,unknown-tag', {10}, 'unknown tag IDs'),
        ('11,immortality', {10}, 'unknown source anime ID'),
    ],
)
def test_manual_tag_loader_rejects_invalid_rows(tmp_path: Path, row: str, known_ids: set[int], error: str) -> None:
    path = tmp_path / 'manual-tags.csv'
    path.write_text(f'source id,tags\n{row}\n', encoding='utf-8')

    with pytest.raises(ValueError, match=error):
        load_manual_tag_assignments(path, known_anime_ids=known_ids)
