from fetch.contracts import Taxonomy, TenraiAnimeEntry
from processing.build import _apply_theme_corrections


def test_theme_corrections_remove_before_adding() -> None:
    entry = TenraiAnimeEntry(
        mal_id=1,
        title='Example',
        themes=[Taxonomy(mal_id=1, name='School', type='anime')],
    )

    corrected = _apply_theme_corrections(entry, ('Workplace',), ('School',))

    assert [theme.name for theme in corrected.themes] == ['workplace']
