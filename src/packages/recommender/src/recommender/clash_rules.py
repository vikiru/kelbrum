from collections.abc import Iterable
from enum import IntFlag, auto

import msgspec
import numpy as np

from anime_catalogue.taxonomy import Genre, Theme
from features.tags import Tag


class ClashFlag(IntFlag):
    NONE = 0

    KIDS_FAMILY_PROTAG = auto()
    TEEN_PROTAG = auto()
    ADULT_WORKING_PROTAG = auto()
    ANTIHERO_VILLAIN_PROTAG = auto()
    CGDCT_IDOL_CAST = auto()
    NON_HUMAN_PROTAG = auto()
    ENSEMBLE_CAST = auto()
    GENIUS_STRATEGIST_PROTAG = auto()

    MUNDANE_CONTEMPORARY = auto()
    URBAN_METROPOLITAN = auto()
    COUNTRYSIDE_RURAL = auto()
    HISTORICAL_FEUDAL = auto()
    STEAMPUNK_ALTERNATE = auto()
    FUTURISTIC_SCIFI = auto()
    SPACE_OPERA_MECHA = auto()
    POST_APOCALYPTIC = auto()
    HIGH_FANTASY = auto()
    ISEKAI = auto()
    REVERSE_ISEKAI = auto()
    GAME_VR_TRAPPED = auto()
    URBAN_FANTASY = auto()
    PRISON_CLOSED = auto()

    BLEAK_NOIR = auto()
    PSYCHOLOGICAL_THRILLER = auto()
    HEAVY_TRAUMA_DRAMA = auto()
    HIGH_STAKES_SURVIVAL = auto()
    MELODRAMA_TRAGEDY = auto()
    COZY_IYASHIKEI = auto()
    PURE_COMEDY = auto()
    SLAPSTICK_PARODY = auto()
    WHIMSICAL_LIGHT = auto()

    VISCERAL_HORROR_GORE = auto()
    ECCHI_FANSERVICE = auto()

    HAREM_POLY = auto()
    BL_GL = auto()
    FOUND_FAMILY_PLATONIC = auto()
    ROMANCE_CENTERED = auto()

    PURE_SLICE_OF_LIFE = auto()
    BATTLE_ACTION = auto()
    SPORTS_COMPETITION = auto()
    CREATURE_TOY_BATTLER = auto()
    MYSTERY_INVESTIGATION = auto()
    MILITARY_POLITICAL = auto()
    AVANT_GARDE_EXPERIMENTAL = auto()
    MONSTER_HYBRID_CONFLICT = auto()
    ABILITY_PROGRESSION = auto()
    TIME_META_LOOP = auto()
    HEIST_CRIME_UNDERCOVER = auto()
    CRAFT_CAREER_PERFORMANCE = auto()
    DEATHMATCH_COMPETITION = auto()


class FlagSpec(msgspec.Struct, frozen=True):
    any_of: frozenset[str]
    none_of: frozenset[str] = frozenset()


class ClashRule(msgspec.Struct, frozen=True):
    anchor_flag: ClashFlag
    candidate_flag: ClashFlag
    penalty: float
    max_dense_cosine: float | None = None
    symmetric: bool = True


FLAG_SPECS: dict[ClashFlag, FlagSpec] = {
    ClashFlag.KIDS_FAMILY_PROTAG: FlagSpec(
        frozenset({Genre.EDUCATIONAL, Theme.PETS}),
        none_of=frozenset({Tag.DARK, Theme.GORE, Genre.HORROR, Genre.ECCHI, Tag.BLEAK, Tag.NOIR}),
    ),
    ClashFlag.TEEN_PROTAG: FlagSpec(
        frozenset({Tag.TEEN_PROTAGONIST, Theme.SCHOOL, Tag.ACADEMY, Tag.COMING_OF_AGE}),
    ),
    ClashFlag.ADULT_WORKING_PROTAG: FlagSpec(
        frozenset(
            {Theme.ADULT_CAST, Tag.ADULT_PROTAGONIST, Theme.WORKPLACE, Tag.WORK_LIFE, Tag.CAREER_AMBITION, 'parenting'}
        ),
    ),
    ClashFlag.ANTIHERO_VILLAIN_PROTAG: FlagSpec(
        frozenset(
            {
                Tag.ANTIHERO,
                Theme.VILLAINESS,
                Tag.ASSASSIN,
                Tag.BOUNTY_HUNTER,
                Theme.ORGANIZED_CRIME,
                Theme.DELINQUENTS,
                Tag.VIGILANTES,
            }
        ),
    ),
    ClashFlag.CGDCT_IDOL_CAST: FlagSpec(
        frozenset({Theme.CGDCT, Theme.IDOLS_FEMALE, Theme.IDOLS_MALE}),
    ),
    ClashFlag.NON_HUMAN_PROTAG: FlagSpec(
        frozenset({Tag.NON_HUMAN_PROTAGONIST, Theme.ANTHROPOMORPHIC, Theme.VAMPIRE, Tag.MONSTERIZATION}),
    ),
    ClashFlag.ENSEMBLE_CAST: FlagSpec(
        frozenset({Tag.ENSEMBLE_CAST, Tag.ADVENTURING_PARTY}),
    ),
    ClashFlag.GENIUS_STRATEGIST_PROTAG: FlagSpec(
        frozenset({Tag.GENIUS_PROTAGONIST, Tag.STRATEGIC_PROTAGONIST, Tag.OVERPOWERED_PROTAGONIST}),
    ),
    ClashFlag.MUNDANE_CONTEMPORARY: FlagSpec(
        frozenset({Theme.SCHOOL, Theme.WORKPLACE, Tag.WORK_LIFE, Theme.GOURMET, Tag.RESTAURANT_CAFE}),
        none_of=frozenset(
            {
                Genre.FANTASY,
                Theme.ISEKAI,
                Genre.SCI_FI,
                Genre.SUPERNATURAL,
                Theme.URBAN_FANTASY,
                Theme.SPACE,
                Theme.MECHA,
                Theme.MAHOU_SHOUJO,
            }
        ),
    ),
    ClashFlag.URBAN_METROPOLITAN: FlagSpec(
        frozenset({Tag.URBAN_SETTING, Tag.GANGS}),
    ),
    ClashFlag.COUNTRYSIDE_RURAL: FlagSpec(
        frozenset({Tag.COUNTRYSIDE, Tag.AGRICULTURE, Tag.CAMPING}),
    ),
    ClashFlag.HISTORICAL_FEUDAL: FlagSpec(
        frozenset({Theme.HISTORICAL, Theme.SAMURAI, Tag.MEDIEVAL, Tag.VICTORIAN, Tag.ALTERNATE_HISTORY}),
    ),
    ClashFlag.STEAMPUNK_ALTERNATE: FlagSpec(
        frozenset({Tag.STEAMPUNK}),
    ),
    ClashFlag.FUTURISTIC_SCIFI: FlagSpec(
        frozenset(
            {
                Genre.SCI_FI,
                Theme.SPACE,
                Tag.OUTER_SPACE,
                Theme.MECHA,
                Tag.CYBERPUNK,
                Tag.DYSTOPIAN,
                Tag.ALIENS,
                Tag.ANDROID,
                Tag.ARTIFICIAL_INTELLIGENCE,
                Tag.CLONING,
                Tag.CYBERNETICS,
            }
        ),
    ),
    ClashFlag.SPACE_OPERA_MECHA: FlagSpec(
        frozenset({Tag.SPACE_OPERA, Theme.MECHA, Tag.OUTER_SPACE}),
    ),
    ClashFlag.POST_APOCALYPTIC: FlagSpec(
        frozenset({Tag.POST_APOCALYPTIC, Tag.APOCALYPSE, Tag.ENVIRONMENTAL_COLLAPSE}),
    ),
    ClashFlag.HIGH_FANTASY: FlagSpec(
        frozenset({Genre.FANTASY, Theme.MYTHOLOGY, Tag.ALCHEMY, Tag.DUNGEON, Tag.DRAGONS}),
        none_of=frozenset({Genre.SCI_FI, Theme.ISEKAI}),
    ),
    ClashFlag.ISEKAI: FlagSpec(
        frozenset(
            {
                Theme.ISEKAI,
                Theme.REINCARNATION,
                Tag.TRANSMIGRATION,
                Tag.SUMMONED_TO_ANOTHER_WORLD,
                Tag.PERSON_IN_A_STRANGE_WORLD,
            }
        ),
        none_of=frozenset({Genre.SCI_FI}),
    ),
    ClashFlag.REVERSE_ISEKAI: FlagSpec(
        frozenset({Tag.REVERSE_ISEKAI}),
    ),
    ClashFlag.GAME_VR_TRAPPED: FlagSpec(
        frozenset(
            {
                Tag.VIRTUAL_REALITY,
                Tag.TRAPPED_IN_GAME,
                Theme.VIDEO_GAME,
                Tag.GAME_WORLD_BECOMES_REALITY,
                Tag.AUGMENTED_REALITY,
                Tag.ESPORTS,
            }
        ),
    ),
    ClashFlag.URBAN_FANTASY: FlagSpec(
        frozenset({Theme.URBAN_FANTASY, Genre.SUPERNATURAL, Tag.OCCULT, Tag.EXORCISM, Tag.YOKAI}),
    ),
    ClashFlag.PRISON_CLOSED: FlagSpec(
        frozenset({Tag.PRISON_SETTING, Tag.CLOSED_SOCIETY, Tag.CAPTIVITY}),
    ),
    ClashFlag.BLEAK_NOIR: FlagSpec(
        frozenset({Tag.BLEAK, Tag.NOIR, Tag.APOCALYPSE, Tag.POST_APOCALYPTIC, Tag.ACTS_OF_TERROR}),
        none_of=frozenset({Theme.MAHOU_SHOUJO, Genre.COMEDY}),
    ),
    ClashFlag.PSYCHOLOGICAL_THRILLER: FlagSpec(
        frozenset({Genre.SUSPENSE, Theme.PSYCHOLOGICAL, Tag.CAT_AND_MOUSE, Tag.ESPIONAGE, Tag.SPY}),
    ),
    ClashFlag.HEAVY_TRAUMA_DRAMA: FlagSpec(
        frozenset({Tag.TRAUMA, Tag.GRIEF, Tag.BULLYING}),
    ),
    ClashFlag.HIGH_STAKES_SURVIVAL: FlagSpec(
        frozenset({Tag.DEATH_GAME, Tag.BATTLE_ROYALE, Theme.HIGH_STAKES_GAME, Tag.CAPTIVITY}),
    ),
    ClashFlag.MELODRAMA_TRAGEDY: FlagSpec(
        frozenset({Tag.TRAGEDY, Tag.MELANCHOLIC, Tag.BITTERSWEET, Tag.MORTALITY, Tag.SERIOUS_ILLNESS}),
    ),
    ClashFlag.COZY_IYASHIKEI: FlagSpec(
        frozenset({Theme.IYASHIKEI, Tag.SLOW_LIFE, Tag.HEARTWARMING, Tag.COMMUNITY_LIFE, Theme.PETS, Tag.CAMPING}),
        none_of=frozenset({Tag.DARK, Theme.GORE, Genre.HORROR, Theme.SURVIVAL}),
    ),
    ClashFlag.PURE_COMEDY: FlagSpec(
        frozenset({Genre.COMEDY}),
        none_of=frozenset({Tag.DARK, Genre.HORROR, Theme.GORE, Tag.BLEAK, Tag.NOIR, Tag.TRAGEDY}),
    ),
    ClashFlag.SLAPSTICK_PARODY: FlagSpec(
        frozenset({Theme.PARODY, Theme.GAG_HUMOR, Tag.SATIRE, Tag.ABSURDIST}),
    ),
    ClashFlag.WHIMSICAL_LIGHT: FlagSpec(
        frozenset({Tag.WHIMSICAL, Tag.HEARTWARMING}),
    ),
    ClashFlag.VISCERAL_HORROR_GORE: FlagSpec(
        frozenset({Genre.HORROR, Theme.GORE, Tag.BODY_HORROR, Tag.SERIAL_KILLER}),
    ),
    ClashFlag.ECCHI_FANSERVICE: FlagSpec(
        frozenset({Genre.ECCHI}),
    ),
    ClashFlag.HAREM_POLY: FlagSpec(
        frozenset({Theme.HAREM, Theme.REVERSE_HAREM}),
    ),
    ClashFlag.BL_GL: FlagSpec(
        frozenset({Genre.BOYS_LOVE, Genre.GIRLS_LOVE}),
    ),
    ClashFlag.FOUND_FAMILY_PLATONIC: FlagSpec(
        frozenset({Tag.FOUND_FAMILY, Theme.CHILDCARE, Tag.SIBLINGS, Tag.MENTOR_STUDENT_RELATIONSHIP}),
        none_of=frozenset({Theme.HAREM, Theme.REVERSE_HAREM, Genre.ECCHI}),
    ),
    ClashFlag.ROMANCE_CENTERED: FlagSpec(
        frozenset(
            {
                Genre.ROMANCE,
                Theme.LOVE_POLYGON,
                Tag.ENEMIES_TO_LOVERS,
                Tag.FAKE_RELATIONSHIP,
                Tag.ARRANGED_MARRIAGE,
                Tag.AGE_GAP_ROMANCE,
            }
        ),
    ),
    ClashFlag.PURE_SLICE_OF_LIFE: FlagSpec(
        frozenset({Genre.SLICE_OF_LIFE}),
        none_of=frozenset({Genre.ACTION, Genre.ADVENTURE, Genre.DRAMA, Genre.FANTASY, Theme.GORE, Genre.HORROR}),
    ),
    ClashFlag.BATTLE_ACTION: FlagSpec(
        frozenset({Genre.ACTION, Theme.MARTIAL_ARTS, Theme.COMBAT_SPORTS, Tag.ABILITY_BATTLES, Tag.POWER_SYSTEM}),
    ),
    ClashFlag.SPORTS_COMPETITION: FlagSpec(
        frozenset(
            {
                Genre.SPORTS,
                Theme.TEAM_SPORTS,
                Theme.COMBAT_SPORTS,
                Theme.RACING,
                Tag.ACADEMIC_COMPETITION,
                Tag.COOKING_COMPETITION,
            }
        ),
        none_of=frozenset({Genre.FANTASY, Genre.SCI_FI, Genre.HORROR}),
    ),
    ClashFlag.CREATURE_TOY_BATTLER: FlagSpec(
        frozenset({Tag.CREATURE_TAMING, Tag.PARTNER_BATTLING, Tag.CARD_BATTLING, Tag.TOY_BATTLING}),
    ),
    ClashFlag.MYSTERY_INVESTIGATION: FlagSpec(
        frozenset(
            {
                Genre.MYSTERY,
                Theme.DETECTIVE,
                Tag.MURDER_MYSTERY,
                Tag.INVESTIGATION,
                Tag.SOCIAL_DEDUCTION,
                Tag.PUZZLES,
                Tag.CONSPIRACY,
            }
        ),
    ),
    ClashFlag.MILITARY_POLITICAL: FlagSpec(
        frozenset({Theme.MILITARY, Tag.WAR, Tag.POLITICAL, Tag.KINGDOM_BUILDING}),
    ),
    ClashFlag.AVANT_GARDE_EXPERIMENTAL: FlagSpec(
        frozenset({Genre.AVANT_GARDE, Tag.PHILOSOPHICAL}),
    ),
    ClashFlag.MONSTER_HYBRID_CONFLICT: FlagSpec(
        frozenset(
            {
                Tag.MONSTERIZATION,
                Tag.HUMAN_NONHUMAN_HYBRID,
                Tag.HUMAN_NONHUMAN_CONFLICT,
                Tag.INTERSPECIES_CONFLICT,
                Tag.MONSTER_HUNTING,
                Tag.EXORCISM,
                Tag.NECROMANCY,
                Tag.CURSE,
                Tag.POSSESSION,
            }
        ),
    ),
    ClashFlag.ABILITY_PROGRESSION: FlagSpec(
        frozenset(
            {
                Tag.ABILITY_BATTLES,
                Tag.POWER_SYSTEM,
                Tag.WEAK_TO_STRONG,
                Tag.LEVELING,
                Tag.TOWER_CLIMBING,
                Tag.CULTIVATION,
                Tag.GRANTED_POWER,
                Tag.SEALED_POWER,
                Tag.SYSTEM,
                Tag.DUNGEON,
            }
        ),
    ),
    ClashFlag.TIME_META_LOOP: FlagSpec(
        frozenset(
            {
                Tag.TIME_LOOP,
                Tag.TIME_LEAP,
                Theme.TIME_TRAVEL,
                Tag.REGRESSION,
                Tag.SECOND_CHANCE,
                Tag.BODY_SWAP,
                Tag.BODY_SHARING,
                Tag.MEMORY_LOSS,
                Tag.MEMORY_MANIPULATION,
            }
        ),
    ),
    ClashFlag.HEIST_CRIME_UNDERCOVER: FlagSpec(
        frozenset(
            {
                Tag.HEIST,
                Tag.ESPIONAGE,
                Tag.SPY,
                Tag.UNDERCOVER,
                Tag.LAW_ENFORCEMENT,
                Tag.FRAMED_FOR_A_CRIME,
                Tag.REVENGE,
                Tag.BETRAYAL,
                Tag.REBELLION,
            }
        ),
    ),
    ClashFlag.CRAFT_CAREER_PERFORMANCE: FlagSpec(
        frozenset(
            {
                Tag.MANGA_ANIME_CREATION,
                Tag.MEDIA_PRODUCTION,
                Tag.VOICE_ACTING,
                Tag.THEATER,
                Tag.MUSICAL_BAND,
                Tag.CLASSICAL_MUSIC,
                Theme.SHOWBIZ,
                Theme.PERFORMING_ARTS,
                Theme.MEDICAL,
                Tag.LEGAL,
                Tag.JOURNALISM,
                Theme.GOURMET,
            }
        ),
    ),
    ClashFlag.DEATHMATCH_COMPETITION: FlagSpec(
        frozenset(
            {
                Tag.DEATH_GAME,
                Tag.DEATHMATCH,
                Tag.BATTLE_ROYALE,
                Theme.HIGH_STAKES_GAME,
                Tag.GAMBLING,
                Tag.TOURNAMENT,
                Tag.COOKING_COMPETITION,
                Tag.ACADEMIC_COMPETITION,
            }
        ),
    ),
}

DARK_HEAVY_FLAGS = (
    ClashFlag.VISCERAL_HORROR_GORE
    | ClashFlag.BLEAK_NOIR
    | ClashFlag.PSYCHOLOGICAL_THRILLER
    | ClashFlag.HEAVY_TRAUMA_DRAMA
    | ClashFlag.HIGH_STAKES_SURVIVAL
    | ClashFlag.MELODRAMA_TRAGEDY
)
LIGHT_COZY_FLAGS = (
    ClashFlag.COZY_IYASHIKEI | ClashFlag.CGDCT_IDOL_CAST | ClashFlag.KIDS_FAMILY_PROTAG | ClashFlag.WHIMSICAL_LIGHT
)
SPECULATIVE_SETTING_FLAGS = ClashFlag.FUTURISTIC_SCIFI | ClashFlag.HIGH_FANTASY | ClashFlag.ISEKAI
MATURE_RELATIONSHIP_FLAGS = ClashFlag.ECCHI_FANSERVICE | ClashFlag.HAREM_POLY | ClashFlag.BL_GL
NARRATIVE_HOOK_FLAGS = (
    ClashFlag.MYSTERY_INVESTIGATION
    | ClashFlag.PSYCHOLOGICAL_THRILLER
    | ClashFlag.HIGH_STAKES_SURVIVAL
    | ClashFlag.MILITARY_POLITICAL
    | ClashFlag.CREATURE_TOY_BATTLER
    | ClashFlag.SPORTS_COMPETITION
    | ClashFlag.AVANT_GARDE_EXPERIMENTAL
    | ClashFlag.MONSTER_HYBRID_CONFLICT
    | ClashFlag.ABILITY_PROGRESSION
    | ClashFlag.TIME_META_LOOP
    | ClashFlag.HEIST_CRIME_UNDERCOVER
    | ClashFlag.CRAFT_CAREER_PERFORMANCE
    | ClashFlag.DEATHMATCH_COMPETITION
)

CLASH_RULES: tuple[ClashRule, ...] = (
    ClashRule(DARK_HEAVY_FLAGS, LIGHT_COZY_FLAGS, penalty=0.30, max_dense_cosine=0.50),
    ClashRule(ClashFlag.VISCERAL_HORROR_GORE, LIGHT_COZY_FLAGS, penalty=0.20),
    ClashRule(ClashFlag.VISCERAL_HORROR_GORE, ClashFlag.KIDS_FAMILY_PROTAG, penalty=0.15),
    ClashRule(ClashFlag.BLEAK_NOIR, ClashFlag.PURE_COMEDY, penalty=0.30, max_dense_cosine=0.50),
    ClashRule(MATURE_RELATIONSHIP_FLAGS, ClashFlag.KIDS_FAMILY_PROTAG, penalty=0.20),
    ClashRule(ClashFlag.ECCHI_FANSERVICE, ClashFlag.COZY_IYASHIKEI, penalty=0.40, max_dense_cosine=0.50),
    ClashRule(ClashFlag.HAREM_POLY, ClashFlag.FOUND_FAMILY_PLATONIC, penalty=0.45, max_dense_cosine=0.45),
    ClashRule(ClashFlag.HISTORICAL_FEUDAL, ClashFlag.FUTURISTIC_SCIFI, penalty=0.45, max_dense_cosine=0.50),
    ClashRule(ClashFlag.MUNDANE_CONTEMPORARY, SPECULATIVE_SETTING_FLAGS, penalty=0.50, max_dense_cosine=0.45),
    ClashRule(ClashFlag.KIDS_FAMILY_PROTAG, ClashFlag.ADULT_WORKING_PROTAG, penalty=0.35, max_dense_cosine=0.50),
    ClashRule(
        ClashFlag.KIDS_FAMILY_PROTAG | ClashFlag.CGDCT_IDOL_CAST,
        ClashFlag.ANTIHERO_VILLAIN_PROTAG,
        penalty=0.25,
    ),
    ClashRule(ClashFlag.PURE_SLICE_OF_LIFE, ClashFlag.BATTLE_ACTION, penalty=0.35, max_dense_cosine=0.45),
    ClashRule(ClashFlag.AVANT_GARDE_EXPERIMENTAL, ClashFlag.CGDCT_IDOL_CAST, penalty=0.35, max_dense_cosine=0.45),
    ClashRule(
        ClashFlag.AVANT_GARDE_EXPERIMENTAL,
        ClashFlag.SLAPSTICK_PARODY | ClashFlag.ECCHI_FANSERVICE,
        penalty=0.40,
        max_dense_cosine=0.45,
    ),
    ClashRule(ClashFlag.ADULT_WORKING_PROTAG, ClashFlag.CGDCT_IDOL_CAST, penalty=0.45, max_dense_cosine=0.55),
    ClashRule(ClashFlag.SPORTS_COMPETITION, ClashFlag.VISCERAL_HORROR_GORE, penalty=0.25),
    ClashRule(ClashFlag.SPORTS_COMPETITION, ClashFlag.COZY_IYASHIKEI, penalty=0.50, max_dense_cosine=0.45),
    ClashRule(ClashFlag.CREATURE_TOY_BATTLER, ClashFlag.VISCERAL_HORROR_GORE | ClashFlag.BLEAK_NOIR, penalty=0.25),
    ClashRule(ClashFlag.CREATURE_TOY_BATTLER, ClashFlag.ADULT_WORKING_PROTAG, penalty=0.45, max_dense_cosine=0.45),
    ClashRule(
        ClashFlag.SPACE_OPERA_MECHA,
        ClashFlag.MUNDANE_CONTEMPORARY | ClashFlag.COZY_IYASHIKEI,
        penalty=0.45,
        max_dense_cosine=0.45,
    ),
    ClashRule(
        ClashFlag.GAME_VR_TRAPPED,
        ClashFlag.HISTORICAL_FEUDAL | ClashFlag.COZY_IYASHIKEI,
        penalty=0.50,
        max_dense_cosine=0.45,
    ),
)


def normalize_clash_tokens(tokens: Iterable[str]) -> frozenset[str]:
    return frozenset(str(token).strip().lower().replace(' ', '_') for token in tokens if token)


def extract_clash_flags(tokens: frozenset[str]) -> ClashFlag:
    mask = ClashFlag.NONE
    for flag, spec in FLAG_SPECS.items():
        if (tokens & spec.any_of) and not (tokens & spec.none_of):
            mask |= flag
    return mask


_NARRATIVE_HOOK_INT = int(NARRATIVE_HOOK_FLAGS)


def compile_anchor_clash_rules(anchor_mask: ClashFlag) -> tuple[tuple[int, float, float | None], ...]:
    compiled: list[tuple[int, float, float | None]] = []
    for rule in CLASH_RULES:
        req = ClashFlag.NONE
        if anchor_mask & rule.anchor_flag:
            req |= rule.candidate_flag
        if rule.symmetric and (anchor_mask & rule.candidate_flag):
            req |= rule.anchor_flag
        if req:
            compiled.append((int(req), rule.penalty, rule.max_dense_cosine))
    return tuple(compiled)


def evaluate_compiled_clash_rules(
    compiled_rules: tuple[tuple[int, float, float | None], ...],
    candidate_mask: ClashFlag | int,
    dense_cosine: float,
    anchor_mask: ClashFlag | int = 0,
) -> float:
    cand_int = int(candidate_mask)
    if not cand_int:
        return 1.0
    penalty = 1.0
    for req_mask, rule_penalty, max_dense_cosine in compiled_rules:
        if (cand_int & req_mask) and (max_dense_cosine is None or dense_cosine < max_dense_cosine):
            penalty = min(penalty, rule_penalty)
    if penalty < 1.0:
        return penalty
    shared_hooks = (int(anchor_mask) & cand_int & _NARRATIVE_HOOK_INT).bit_count()
    return 1.0 + min(0.12, 0.06 * shared_hooks) if shared_hooks else 1.0


def evaluate_compiled_clash_rules_batch(
    compiled_rules: tuple[tuple[int, float, float | None], ...],
    candidate_masks: 'np.ndarray',
    dense_cosines: 'np.ndarray',
    anchor_mask: int = 0,
) -> 'np.ndarray':
    n = len(candidate_masks)
    penalties = np.ones(n, dtype=np.float64)
    nonzero = candidate_masks != 0
    if not np.any(nonzero):
        return penalties
    for req_mask, rule_penalty, max_dense_cosine in compiled_rules:
        hit = nonzero & ((candidate_masks & req_mask) != 0)
        if max_dense_cosine is not None:
            hit &= dense_cosines < max_dense_cosine
        penalties = np.where(hit & (rule_penalty < penalties), rule_penalty, penalties)
    hook_mask = int(anchor_mask) & _NARRATIVE_HOOK_INT
    if hook_mask:
        no_penalty = nonzero & (penalties >= 1.0)
        if np.any(no_penalty):
            shared_bits = candidate_masks[no_penalty] & hook_mask
            counts = np.bitwise_count(shared_bits).astype(np.float64)
            penalties[no_penalty] = 1.0 + np.minimum(0.12, 0.06 * counts)
    return penalties
