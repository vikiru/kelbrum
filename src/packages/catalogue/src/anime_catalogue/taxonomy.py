"""Canonical genre and theme identities shared by catalogue consumers.

String values preserve CSV, Parquet and feature-vocabulary compatibility. Parse
external labels once at a boundary; domain rules refer to enum members.
Cross-listed labels reflect existing project curation; parsing does not move
labels between fields or change catalogue annotations.
"""

import re
from enum import StrEnum
from typing import Final


class Genre(StrEnum):
    ACTION = 'action'
    ADVENTURE = 'adventure'
    AVANT_GARDE = 'avant_garde'
    AWARD_WINNING = 'award_winning'
    BOYS_LOVE = 'boys_love'
    COMEDY = 'comedy'
    DETECTIVE = 'detective'
    DRAMA = 'drama'
    ECCHI = 'ecchi'
    EDUCATIONAL = 'educational'
    FANTASY = 'fantasy'
    GIRLS_LOVE = 'girls_love'
    GOURMET = 'gourmet'
    HORROR = 'horror'
    MYSTERY = 'mystery'
    ROMANCE = 'romance'
    SCI_FI = 'sci_fi'
    SLICE_OF_LIFE = 'slice_of_life'
    SPORTS = 'sports'
    SUPERNATURAL = 'supernatural'
    SUSPENSE = 'suspense'


class Theme(StrEnum):
    ADULT_CAST = 'adult_cast'
    ANTHROPOMORPHIC = 'anthropomorphic'
    CGDCT = 'cgdct'
    CHILDCARE = 'childcare'
    COMBAT_SPORTS = 'combat_sports'
    CROSSDRESSING = 'crossdressing'
    DELINQUENTS = 'delinquents'
    DETECTIVE = 'detective'
    EDUCATIONAL = 'educational'
    GAG_HUMOR = 'gag_humor'
    GORE = 'gore'
    GOURMET = 'gourmet'
    HAREM = 'harem'
    HIGH_STAKES_GAME = 'high_stakes_game'
    HISTORICAL = 'historical'
    IDOLS_FEMALE = 'idols_female'
    IDOLS_MALE = 'idols_male'
    ISEKAI = 'isekai'
    IYASHIKEI = 'iyashikei'
    LOVE_POLYGON = 'love_polygon'
    LOVE_STATUS_QUO = 'love_status_quo'
    MAGICAL_GENDER_SHIFT = 'magical_gender_shift'
    MAGICAL_SEX_SHIFT = 'magical_sex_shift'
    MAHOU_SHOUJO = 'mahou_shoujo'
    MARTIAL_ARTS = 'martial_arts'
    MECHA = 'mecha'
    MEDICAL = 'medical'
    MILITARY = 'military'
    MUSIC = 'music'
    MYTHOLOGY = 'mythology'
    ORGANIZED_CRIME = 'organized_crime'
    OTAKU_CULTURE = 'otaku_culture'
    PARODY = 'parody'
    PERFORMING_ARTS = 'performing_arts'
    PETS = 'pets'
    PSYCHOLOGICAL = 'psychological'
    RACING = 'racing'
    REINCARNATION = 'reincarnation'
    REVERSE_HAREM = 'reverse_harem'
    SAMURAI = 'samurai'
    SCHOOL = 'school'
    SHOWBIZ = 'showbiz'
    SLICE_OF_LIFE = 'slice_of_life'
    SPACE = 'space'
    STRATEGY_GAME = 'strategy_game'
    SUPER_POWER = 'super_power'
    SUPERNATURAL = 'supernatural'
    SURVIVAL = 'survival'
    TEAM_SPORTS = 'team_sports'
    TIME_TRAVEL = 'time_travel'
    URBAN_FANTASY = 'urban_fantasy'
    VAMPIRE = 'vampire'
    VIDEO_GAME = 'video_game'
    VILLAINESS = 'villainess'
    VISUAL_ARTS = 'visual_arts'
    WORKPLACE = 'workplace'


SETTING_BACKDROP_THEMES: Final[frozenset[Theme]] = frozenset(
    {
        Theme.SCHOOL,
        Theme.HISTORICAL,
        Theme.WORKPLACE,
        Theme.OTAKU_CULTURE,
        Theme.CHILDCARE,
        Theme.ADULT_CAST,
        Theme.IDOLS_FEMALE,
        Theme.IDOLS_MALE,
        Theme.MUSIC,
        Theme.MECHA,
    }
)


_LABEL_SEPARATOR = re.compile(r'[^a-z0-9]+')


def parse_genre(value: str | Genre) -> Genre:
    return _parse_label(value, Genre)


def parse_theme(value: str | Theme) -> Theme:
    return _parse_label(value, Theme)


def safe_parse_genre(value: str | Genre) -> Genre | None:
    try:
        return parse_genre(value)
    except (ValueError, TypeError):
        return None


def safe_parse_theme(value: str | Theme) -> Theme | None:
    try:
        return parse_theme(value)
    except (ValueError, TypeError):
        return None


def _parse_label[Label: StrEnum](value: str | Label, enum: type[Label]) -> Label:
    if isinstance(value, enum):
        return value
    if isinstance(value, StrEnum):
        raise TypeError(f'{enum.__name__.lower()} label belongs to another enum: {value!r}')
    if not isinstance(value, str):
        raise TypeError(f'{enum.__name__.lower()} labels must be strings or enum members')
    key = _LABEL_SEPARATOR.sub('_', value.strip().casefold()).strip('_')
    try:
        return enum(key)
    except ValueError as error:
        raise ValueError(f'unsupported {enum.__name__.lower()} label: {value!r}') from error
