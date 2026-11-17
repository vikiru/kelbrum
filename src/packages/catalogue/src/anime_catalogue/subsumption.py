"""Typed subsumption DAG mapping fine-grained leaf concepts to their hypernyms.

This module provides pure, deterministic lookups to deduplicate ancestor tags/themes
and award bounded parent mass across sibling leaves (e.g. baseball -> volleyball).
Zero magic strings or numbers: all relations use Genre, Theme, and Tag enums.
"""

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from functools import lru_cache
from typing import Final, override

from anime_catalogue.tags import Tag
from anime_catalogue.taxonomy import Genre, Theme

type TaxonomyToken = Genre | Theme | Tag
type TokenKey = tuple[type[TaxonomyToken], TaxonomyToken]


def _token_key(token: TaxonomyToken) -> TokenKey:
    return (type(token), token)


class _TokenLookup[V](Mapping[TaxonomyToken, V]):
    """Read-only token mapping keyed by (type(token), token) to prevent StrEnum collisions."""

    __slots__ = ('_by_key',)

    def __init__(self, by_key: Mapping[TokenKey, V]) -> None:
        self._by_key = dict(by_key)

    @override
    def __getitem__(self, key: TaxonomyToken) -> V:
        return self._by_key[_token_key(key)]

    @override
    def __iter__(self) -> Iterator[TaxonomyToken]:
        return (token for token_type, token in self._by_key)

    @override
    def __len__(self) -> int:
        return len(self._by_key)

    @override
    def __contains__(self, key: object) -> bool:
        if not isinstance(key, (Genre, Theme, Tag)):
            return False
        return _token_key(key) in self._by_key


@dataclass(frozen=True, slots=True)
class SubsumptionEdge:
    """Directed edge where leaf concept is subsumed by parent hypernym."""

    child: TaxonomyToken
    parent: TaxonomyToken


# Sibling transfer coefficient: When candidate matches anchor's sibling under the same hypernym,
# award this bounded fraction of the hypernym's weight.
SIBLING_TRANSFER_FACTOR: Final[float] = 0.40

# Complete taxonomy hypernym subsumption graph
_SUBSUMPTION_EDGES: Final[tuple[SubsumptionEdge, ...]] = (
    # --- Sports & Athletics Hierarchy ---
    # Team Sports
    SubsumptionEdge(child=Tag.BASEBALL, parent=Theme.TEAM_SPORTS),
    SubsumptionEdge(child=Tag.VOLLEYBALL, parent=Theme.TEAM_SPORTS),
    SubsumptionEdge(child=Tag.BASKETBALL, parent=Theme.TEAM_SPORTS),
    SubsumptionEdge(child=Tag.SOCCER, parent=Theme.TEAM_SPORTS),
    SubsumptionEdge(child=Tag.AMERICAN_FOOTBALL, parent=Theme.TEAM_SPORTS),
    SubsumptionEdge(child=Tag.RUGBY, parent=Theme.TEAM_SPORTS),
    SubsumptionEdge(child=Tag.HOCKEY, parent=Theme.TEAM_SPORTS),
    SubsumptionEdge(child=Tag.WATER_POLO, parent=Theme.TEAM_SPORTS),
    SubsumptionEdge(child=Theme.TEAM_SPORTS, parent=Genre.SPORTS),
    # Racket / Solo Athletics
    SubsumptionEdge(child=Tag.TENNIS, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.BADMINTON, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.TABLE_TENNIS, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.CYCLING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.RUNNING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.SWIMMING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.ARCHERY, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.TRACK_AND_FIELD, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.FIGURE_SKATING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.ICE_SKATING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.GYMNASTICS, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.GOLF, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.SURFING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.SKATEBOARDING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.SKIING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.MOUNTAINEERING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.SCUBA_DIVING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.WEIGHTLIFTING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.FENCING, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.ESPORTS, parent=Genre.SPORTS),
    SubsumptionEdge(child=Tag.BILLIARDS, parent=Genre.SPORTS),
    # Combat Sports (Regulated Athletics / Arena)
    SubsumptionEdge(child=Tag.BOXING, parent=Theme.COMBAT_SPORTS),
    SubsumptionEdge(child=Tag.WRESTLING, parent=Theme.COMBAT_SPORTS),
    SubsumptionEdge(child=Tag.JUDO, parent=Theme.COMBAT_SPORTS),
    SubsumptionEdge(child=Tag.KENDO, parent=Theme.COMBAT_SPORTS),
    SubsumptionEdge(child=Tag.SUMO, parent=Theme.COMBAT_SPORTS),
    SubsumptionEdge(child=Theme.COMBAT_SPORTS, parent=Genre.SPORTS),
    # Martial Arts (Lethal / Philosophical / Underground Combat)
    SubsumptionEdge(child=Theme.MARTIAL_ARTS, parent=Genre.ACTION),
    # Automotive / Racing / Motorsport
    SubsumptionEdge(child=Tag.MOTORSPORT, parent=Theme.RACING),
    SubsumptionEdge(child=Theme.RACING, parent=Genre.SPORTS),
    # --- Performing Arts & Creative Professions Hierarchy ---
    SubsumptionEdge(child=Tag.THEATER, parent=Theme.PERFORMING_ARTS),
    SubsumptionEdge(child=Tag.DANCING, parent=Theme.PERFORMING_ARTS),
    SubsumptionEdge(child=Tag.RAKUGO, parent=Theme.PERFORMING_ARTS),
    SubsumptionEdge(child=Theme.MUSIC, parent=Theme.PERFORMING_ARTS),
    SubsumptionEdge(child=Tag.CLASSICAL_MUSIC, parent=Theme.MUSIC),
    SubsumptionEdge(child=Tag.MUSICAL_BAND, parent=Theme.MUSIC),
    SubsumptionEdge(child=Theme.IDOLS_FEMALE, parent=Theme.PERFORMING_ARTS),
    SubsumptionEdge(child=Theme.IDOLS_MALE, parent=Theme.PERFORMING_ARTS),
    SubsumptionEdge(child=Tag.PAINTING_DRAWING, parent=Theme.VISUAL_ARTS),
    SubsumptionEdge(child=Tag.MANGA_ANIME_CREATION, parent=Theme.VISUAL_ARTS),
    SubsumptionEdge(child=Tag.PHOTOGRAPHY, parent=Theme.VISUAL_ARTS),
    SubsumptionEdge(child=Tag.CALLIGRAPHY, parent=Theme.VISUAL_ARTS),
    SubsumptionEdge(child=Tag.VOICE_ACTING, parent=Theme.SHOWBIZ),
    # --- Speculative / Sci-Fi / Cybernetics Hierarchy ---
    SubsumptionEdge(child=Tag.CYBERPUNK, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.STEAMPUNK, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.SPACE_OPERA, parent=Theme.SPACE),
    SubsumptionEdge(child=Tag.OUTER_SPACE, parent=Theme.SPACE),
    SubsumptionEdge(child=Tag.ASTRONAUT, parent=Theme.SPACE),
    SubsumptionEdge(child=Tag.CYBERNETICS, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.ARTIFICIAL_INTELLIGENCE, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.ANDROID, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.ALIENS, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.CLONING, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.HACKING, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.PARALLEL_WORLDS, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Theme.SPACE, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Theme.TIME_TRAVEL, parent=Genre.SCI_FI),
    SubsumptionEdge(child=Tag.TIME_LOOP, parent=Theme.TIME_TRAVEL),
    SubsumptionEdge(child=Tag.TIME_LEAP, parent=Theme.TIME_TRAVEL),
    SubsumptionEdge(child=Theme.MECHA, parent=Genre.SCI_FI),
    # --- Virtual Reality / Gaming Worlds Hierarchy ---
    SubsumptionEdge(child=Tag.VIRTUAL_REALITY, parent=Theme.VIDEO_GAME),
    SubsumptionEdge(child=Tag.AUGMENTED_REALITY, parent=Theme.VIDEO_GAME),
    SubsumptionEdge(child=Tag.TRAPPED_IN_GAME, parent=Theme.VIDEO_GAME),
    SubsumptionEdge(child=Tag.GAME_WORLD_BECOMES_REALITY, parent=Theme.VIDEO_GAME),
    SubsumptionEdge(child=Theme.VIDEO_GAME, parent=Genre.SCI_FI),
    # --- Strategy Games & Tabletop Hierarchy ---
    SubsumptionEdge(child=Tag.SHOGI, parent=Theme.STRATEGY_GAME),
    SubsumptionEdge(child=Tag.GO, parent=Theme.STRATEGY_GAME),
    SubsumptionEdge(child=Tag.MAHJONG, parent=Theme.STRATEGY_GAME),
    SubsumptionEdge(child=Tag.KARUTA, parent=Theme.STRATEGY_GAME),
    SubsumptionEdge(child=Tag.CARD_BATTLING, parent=Theme.STRATEGY_GAME),
    SubsumptionEdge(child=Tag.MIND_GAMES, parent=Theme.STRATEGY_GAME),
    SubsumptionEdge(child=Tag.PUZZLES, parent=Theme.STRATEGY_GAME),
    SubsumptionEdge(child=Tag.GAMBLING, parent=Theme.STRATEGY_GAME),
    SubsumptionEdge(child=Tag.TOY_BATTLING, parent=Theme.STRATEGY_GAME),
    # --- Historical / Period Settings Hierarchy ---
    SubsumptionEdge(child=Tag.MEDIEVAL, parent=Theme.HISTORICAL),
    SubsumptionEdge(child=Tag.VICTORIAN, parent=Theme.HISTORICAL),
    SubsumptionEdge(child=Tag.HISTORICAL_FIGURES, parent=Theme.HISTORICAL),
    SubsumptionEdge(child=Tag.ALTERNATE_HISTORY, parent=Theme.HISTORICAL),
    SubsumptionEdge(child=Theme.SAMURAI, parent=Theme.HISTORICAL),
    # --- Apocalyptic / Wasteland / Dystopian Hierarchy ---
    SubsumptionEdge(child=Tag.POST_APOCALYPTIC, parent=Theme.SURVIVAL),
    SubsumptionEdge(child=Tag.APOCALYPSE, parent=Theme.SURVIVAL),
    SubsumptionEdge(child=Tag.ENVIRONMENTAL_COLLAPSE, parent=Theme.SURVIVAL),
    SubsumptionEdge(child=Tag.DYSTOPIAN, parent=Genre.SCI_FI),
    # --- Fantasy Systems, Dungeon Crawling & Isekai Hierarchy ---
    SubsumptionEdge(child=Theme.ISEKAI, parent=Genre.FANTASY),
    SubsumptionEdge(child=Theme.REINCARNATION, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.REGRESSION, parent=Theme.REINCARNATION),
    SubsumptionEdge(child=Tag.SECOND_CHANCE, parent=Theme.REINCARNATION),
    SubsumptionEdge(child=Theme.VILLAINESS, parent=Theme.ISEKAI),
    SubsumptionEdge(child=Tag.TRANSMIGRATION, parent=Theme.ISEKAI),
    SubsumptionEdge(child=Tag.SUMMONED_TO_ANOTHER_WORLD, parent=Theme.ISEKAI),
    SubsumptionEdge(child=Tag.REVERSE_ISEKAI, parent=Theme.ISEKAI),
    SubsumptionEdge(child=Tag.TRANSPORTED_INTO_FICTION, parent=Theme.ISEKAI),
    SubsumptionEdge(child=Tag.WORLD_HOPPING, parent=Theme.ISEKAI),
    SubsumptionEdge(child=Tag.PERSON_IN_A_STRANGE_WORLD, parent=Theme.ISEKAI),
    SubsumptionEdge(child=Theme.MAHOU_SHOUJO, parent=Genre.FANTASY),
    SubsumptionEdge(child=Theme.URBAN_FANTASY, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.CULTIVATION, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.DUNGEON, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.ADVENTURING_PARTY, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.GUILDS, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.ALCHEMY, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.SUMMONING, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.CREATURE_TAMING, parent=Tag.PARTNER_BATTLING),
    SubsumptionEdge(child=Tag.PARTNER_BATTLING, parent=Genre.ADVENTURE),
    SubsumptionEdge(child=Tag.DRAGONS, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.FAIRIES, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.LEVELING, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.SYSTEM, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.TOWER_CLIMBING, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.MONSTERS, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.KINGDOM_BUILDING, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.ROYALTY, parent=Genre.FANTASY),
    SubsumptionEdge(child=Tag.DREAM_WORLDS, parent=Genre.FANTASY),
    SubsumptionEdge(child=Theme.ANTHROPOMORPHIC, parent=Genre.FANTASY),
    # --- Supernatural Entities, Spirits & Occult Hierarchy ---
    SubsumptionEdge(child=Theme.MYTHOLOGY, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.GODS, parent=Theme.MYTHOLOGY),
    SubsumptionEdge(child=Theme.VAMPIRE, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.ZOMBIE, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.NECROMANCY, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.YOKAI, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.SPIRIT_WORLD, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.SPIRIT_MANIFESTATION, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.EXORCISM, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.DEMONS, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.ANGELS, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.GHOSTS, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.UNDEAD, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.WEREWOLVES, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.OCCULT, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.CURSE, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.IMMORTALITY, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.POSSESSION, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.BODY_SWAP, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.SHAPESHIFTING, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.AFTERLIFE, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.HUMAN_NONHUMAN_HYBRID, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.HUMAN_NONHUMAN_CONFLICT, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.HIDDEN_NONHUMAN_SOCIETY, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.INTERSPECIES_CONFLICT, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.BODY_SHARING, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.WITCH, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.URBAN_LEGEND, parent=Genre.SUPERNATURAL),
    SubsumptionEdge(child=Tag.SUPERNATURAL_ENCOUNTERS, parent=Genre.SUPERNATURAL),
    # --- Superpower, Powers & Superheroics Hierarchy ---
    SubsumptionEdge(child=Tag.ELEMENTAL_POWERS, parent=Theme.SUPER_POWER),
    SubsumptionEdge(child=Tag.GRANTED_POWER, parent=Theme.SUPER_POWER),
    SubsumptionEdge(child=Tag.SEALED_POWER, parent=Theme.SUPER_POWER),
    SubsumptionEdge(child=Tag.POWER_SYSTEM, parent=Theme.SUPER_POWER),
    SubsumptionEdge(child=Tag.PSYCHIC, parent=Theme.SUPER_POWER),
    SubsumptionEdge(child=Tag.PRECOGNITION, parent=Theme.SUPER_POWER),
    SubsumptionEdge(child=Tag.SUPERHERO, parent=Theme.SUPER_POWER),
    SubsumptionEdge(child=Theme.SUPER_POWER, parent=Genre.ACTION),
    # --- Military & Strategic Warfare Hierarchy ---
    SubsumptionEdge(child=Tag.MILITARY_STRATEGY, parent=Theme.MILITARY),
    SubsumptionEdge(child=Tag.WAR, parent=Theme.MILITARY),
    SubsumptionEdge(child=Tag.MERCENARY, parent=Theme.MILITARY),
    SubsumptionEdge(child=Theme.MILITARY, parent=Genre.ACTION),
    # --- Combat Disciplines & Martial Action Hierarchy ---
    SubsumptionEdge(child=Tag.SWORDSMANSHIP, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.MARKSMANSHIP, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.ABILITY_BATTLES, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.BATTLE_ROYALE, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.DEATHMATCH, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.GLADIATOR, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.MONSTER_HUNTING, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.TOURNAMENT, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.NINJA, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.BOUNTY_HUNTER, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.REBELLION, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.LIBERATION, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.ANTIHERO, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.VIGILANTES, parent=Genre.ACTION),
    SubsumptionEdge(child=Theme.DELINQUENTS, parent=Genre.ACTION),
    # --- Dark / Horror / Threat Hierarchy ---
    SubsumptionEdge(child=Theme.GORE, parent=Genre.HORROR),
    SubsumptionEdge(child=Tag.BODY_HORROR, parent=Genre.HORROR),
    SubsumptionEdge(child=Tag.MONSTERIZATION, parent=Tag.BODY_HORROR),
    SubsumptionEdge(child=Tag.PREDATION, parent=Genre.HORROR),
    SubsumptionEdge(child=Tag.SERIAL_KILLER, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Theme.PSYCHOLOGICAL, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.ACTS_OF_TERROR, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.SOCIAL_DEDUCTION, parent=Theme.PSYCHOLOGICAL),
    SubsumptionEdge(child=Tag.MIND_CONTROL, parent=Theme.PSYCHOLOGICAL),
    SubsumptionEdge(child=Tag.MEMORY_MANIPULATION, parent=Theme.PSYCHOLOGICAL),
    SubsumptionEdge(child=Tag.CAT_AND_MOUSE, parent=Theme.PSYCHOLOGICAL),
    SubsumptionEdge(child=Tag.REVENGE, parent=Genre.DRAMA),
    SubsumptionEdge(child=Tag.POLITICAL, parent=Genre.DRAMA),
    SubsumptionEdge(child=Tag.POLITICAL_VIOLENCE, parent=Genre.DRAMA),
    # --- Investigative, Mystery & Espionage Hierarchy ---
    SubsumptionEdge(child=Genre.DETECTIVE, parent=Genre.MYSTERY),
    SubsumptionEdge(child=Theme.DETECTIVE, parent=Genre.MYSTERY),
    SubsumptionEdge(child=Tag.LAWYERS, parent=Genre.MYSTERY),
    SubsumptionEdge(child=Tag.INVESTIGATION, parent=Genre.MYSTERY),
    SubsumptionEdge(child=Tag.MURDER_MYSTERY, parent=Genre.MYSTERY),
    SubsumptionEdge(child=Tag.LAW_ENFORCEMENT, parent=Genre.MYSTERY),
    SubsumptionEdge(child=Tag.SPY, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.ESPIONAGE, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.SECRET_ORGANIZATION, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.UNDERCOVER, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.CONSPIRACY, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.CRIME, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.HEIST, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.PRISON_SETTING, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.CAPTIVITY, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.KIDNAPPING, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.FRAMED_FOR_A_CRIME, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.NOIR, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.MEMORY_LOSS, parent=Genre.MYSTERY),
    SubsumptionEdge(child=Tag.ASSASSIN, parent=Genre.ACTION),
    SubsumptionEdge(child=Tag.GANGS, parent=Theme.ORGANIZED_CRIME),
    SubsumptionEdge(child=Theme.ORGANIZED_CRIME, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.DEATH_GAME, parent=Theme.HIGH_STAKES_GAME),
    SubsumptionEdge(child=Theme.HIGH_STAKES_GAME, parent=Genre.SUSPENSE),
    SubsumptionEdge(child=Tag.PIRATES, parent=Genre.ADVENTURE),
    SubsumptionEdge(child=Tag.TREASURE_HUNTING, parent=Genre.ADVENTURE),
    SubsumptionEdge(child=Tag.JOURNEY, parent=Genre.ADVENTURE),
    SubsumptionEdge(child=Tag.EXPLORATION, parent=Tag.JOURNEY),
    SubsumptionEdge(child=Tag.AVIATION, parent=Genre.ADVENTURE),
    SubsumptionEdge(child=Tag.DINOSAURS, parent=Genre.ADVENTURE),
    # --- Culinary Arts & Gourmet Hierarchy ---
    SubsumptionEdge(child=Tag.COOKING, parent=Theme.GOURMET),
    SubsumptionEdge(child=Tag.COOKING_COMPETITION, parent=Theme.GOURMET),
    SubsumptionEdge(child=Tag.BAKING, parent=Theme.GOURMET),
    SubsumptionEdge(child=Tag.RESTAURANT_CAFE, parent=Theme.WORKPLACE),
    # --- Workplace, Professions & Vocations Hierarchy ---
    SubsumptionEdge(child=Tag.WORK_LIFE, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Tag.APOTHECARY, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Tag.JOURNALISM, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Tag.CAREER_AMBITION, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Theme.MEDICAL, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Tag.LEGAL, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Tag.BODYGUARDS, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Tag.FIREFIGHTER, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Tag.MERCHANT, parent=Theme.WORKPLACE),
    SubsumptionEdge(child=Tag.MEDIA_PRODUCTION, parent=Theme.WORKPLACE),
    # --- School & Institutional Settings Hierarchy ---
    SubsumptionEdge(child=Tag.ACADEMY, parent=Theme.SCHOOL),
    SubsumptionEdge(child=Tag.SCHOOL_CLUB, parent=Theme.SCHOOL),
    SubsumptionEdge(child=Tag.ACADEMIC_COMPETITION, parent=Theme.SCHOOL),
    SubsumptionEdge(child=Tag.TRANSFER_STUDENT, parent=Theme.SCHOOL),
    # --- Lighthearted / Iyashikei / Comedy Hierarchy ---
    SubsumptionEdge(child=Theme.GAG_HUMOR, parent=Genre.COMEDY),
    SubsumptionEdge(child=Theme.PARODY, parent=Genre.COMEDY),
    SubsumptionEdge(child=Tag.SATIRE, parent=Genre.COMEDY),
    SubsumptionEdge(child=Tag.ABSURDIST, parent=Genre.COMEDY),
    SubsumptionEdge(child=Theme.OTAKU_CULTURE, parent=Genre.COMEDY),
    SubsumptionEdge(child=Theme.CROSSDRESSING, parent=Genre.COMEDY),
    SubsumptionEdge(child=Theme.MAGICAL_GENDER_SHIFT, parent=Genre.COMEDY),
    SubsumptionEdge(child=Tag.SLOW_LIFE, parent=Theme.IYASHIKEI),
    SubsumptionEdge(child=Tag.HEARTWARMING, parent=Theme.IYASHIKEI),
    SubsumptionEdge(child=Theme.CGDCT, parent=Genre.SLICE_OF_LIFE),
    SubsumptionEdge(child=Theme.CHILDCARE, parent=Genre.SLICE_OF_LIFE),
    SubsumptionEdge(child=Theme.PETS, parent=Genre.SLICE_OF_LIFE),
    SubsumptionEdge(child=Theme.EDUCATIONAL, parent=Genre.SLICE_OF_LIFE),
    SubsumptionEdge(child=Theme.IYASHIKEI, parent=Genre.SLICE_OF_LIFE),
    SubsumptionEdge(child=Tag.AGRICULTURE, parent=Genre.SLICE_OF_LIFE),
    SubsumptionEdge(child=Tag.CAMPING, parent=Genre.SLICE_OF_LIFE),
    SubsumptionEdge(child=Tag.FISHING, parent=Genre.SLICE_OF_LIFE),
    SubsumptionEdge(child=Tag.OUTBREAK, parent=Theme.SURVIVAL),
    # --- Romance / Relationship Topology Hierarchy ---
    SubsumptionEdge(child=Theme.HAREM, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Theme.REVERSE_HAREM, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Theme.LOVE_POLYGON, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Theme.LOVE_STATUS_QUO, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Tag.ENEMIES_TO_LOVERS, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Tag.AGE_GAP_ROMANCE, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Tag.ARRANGED_MARRIAGE, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Tag.MARRIED_LIFE, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Tag.FORBIDDEN_ROMANCE, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Tag.UNREQUITED_LOVE, parent=Genre.ROMANCE),
    SubsumptionEdge(child=Tag.FAKE_RELATIONSHIP, parent=Genre.ROMANCE),
    # --- Cast & Demographics Hierarchy ---
    SubsumptionEdge(child=Theme.ADULT_CAST, parent=Tag.ADULT_PROTAGONIST),
)


def _build_direct_parents_by_key() -> dict[TokenKey, set[TokenKey]]:
    direct_parents: dict[TokenKey, set[TokenKey]] = {}
    for edge in _SUBSUMPTION_EDGES:
        direct_parents.setdefault(_token_key(edge.child), set()).add(_token_key(edge.parent))
    return direct_parents


def _build_ancestors_by_key(
    direct_parents: Mapping[TokenKey, set[TokenKey]],
) -> dict[TokenKey, frozenset[TokenKey]]:
    """Build precomputed transitive ancestor key set for each token in the DAG."""
    ancestors_lookup: dict[TokenKey, frozenset[TokenKey]] = {}
    for child_key in direct_parents:
        visited: set[TokenKey] = set()
        stack = list(direct_parents[child_key])
        while stack:
            current_token_key = stack.pop()
            if current_token_key not in visited:
                visited.add(current_token_key)
                stack.extend(direct_parents.get(current_token_key, ()))
        ancestors_lookup[child_key] = frozenset(visited)
    return ancestors_lookup


_DIRECT_PARENTS_BY_KEY: Final[dict[TokenKey, set[TokenKey]]] = _build_direct_parents_by_key()
_ANCESTORS_BY_KEY: Final[dict[TokenKey, frozenset[TokenKey]]] = _build_ancestors_by_key(_DIRECT_PARENTS_BY_KEY)

ANCESTORS_BY_TOKEN: Final[Mapping[TaxonomyToken, frozenset[TaxonomyToken]]] = _TokenLookup(
    {key: frozenset(token for token_type, token in ancestor_keys) for key, ancestor_keys in _ANCESTORS_BY_KEY.items()}
)
ALL_ANCESTOR_TOKENS: Final[frozenset[TaxonomyToken]] = frozenset(
    token for ancestor_keys in _ANCESTORS_BY_KEY.values() for token_type, token in ancestor_keys
)

# Orthogonal protagonist demographics and delivery format tags.
# These represent character persona or delivery structure rather than thematic / genre concepts,
# so they are excluded from thematic leaf-specificity discrimination.
NON_THEMATIC_ORTHOGONAL_TAGS: Final[frozenset[Tag | Theme]] = frozenset(
    {
        Theme.ADULT_CAST,
        Tag.MALE_PROTAGONIST,
        Tag.FEMALE_PROTAGONIST,
        Tag.NON_HUMAN_PROTAGONIST,
        Tag.CHILD_PROTAGONIST,
        Tag.TEEN_PROTAGONIST,
        Tag.ADULT_PROTAGONIST,
        Tag.OVERPOWERED_PROTAGONIST,
        Tag.WEAK_TO_STRONG,
        Tag.HIDDEN_STRENGTH,
        Tag.GENIUS_PROTAGONIST,
        Tag.STRATEGIC_PROTAGONIST,
        Tag.STOIC_PROTAGONIST,
        Tag.ENSEMBLE_CAST,
        Tag.EPISODIC,
        Tag.ANTHOLOGY,
        Tag.SERIALIZED,
        Tag.PROCEDURAL,
    }
)


@lru_cache(maxsize=8192)
def _prune_ancestor_frozenset(token_keys: frozenset[TokenKey]) -> frozenset[TaxonomyToken]:
    subsumed_keys = frozenset().union(*(_ANCESTORS_BY_KEY.get(key, frozenset()) for key in token_keys))
    return frozenset(key[1] for key in token_keys if key not in subsumed_keys)


def prune_ancestor_tokens(tokens: Iterable[TaxonomyToken]) -> frozenset[TaxonomyToken]:
    """Prune any hypernym ancestor that is subsumed by a more specific descendant.

    Example:
        {Tag.BASEBALL, Theme.TEAM_SPORTS, Genre.SPORTS} -> {Tag.BASEBALL}
    """
    token_keys = frozenset(_token_key(token) for token in tokens)
    return _prune_ancestor_frozenset(token_keys)


def _build_sibling_lookup() -> dict[TokenKey, dict[TokenKey, TaxonomyToken]]:
    depth_by_key: dict[TokenKey, int] = {}

    def _depth(key: TokenKey) -> int:
        cached = depth_by_key.get(key)
        if cached is not None:
            return cached
        parents = _DIRECT_PARENTS_BY_KEY.get(key)
        depth = 0 if not parents else 1 + max(_depth(parent) for parent in parents)
        depth_by_key[key] = depth
        return depth

    keys = tuple(sorted(_ANCESTORS_BY_KEY.keys(), key=lambda key: (key[0].__name__, key[1].value)))
    table: dict[TokenKey, dict[TokenKey, TaxonomyToken]] = {key: {} for key in keys}
    for i, key_a in enumerate(keys):
        ancestors_a = _ANCESTORS_BY_KEY[key_a]
        for key_b in keys[i + 1 :]:
            ancestors_b = _ANCESTORS_BY_KEY[key_b]
            if key_a in ancestors_b or key_b in ancestors_a:
                continue
            common = ancestors_a & ancestors_b
            if not common:
                continue
            sorted_common = sorted(
                common,
                key=lambda key: (-_depth(key), key[0].__name__, key[1].value),
            )
            lca_key: TokenKey | None = None
            for common_ancestor_key in sorted_common:
                is_parent = any(
                    common_ancestor_key in _ANCESTORS_BY_KEY.get(other, frozenset())
                    for other in sorted_common
                    if other != common_ancestor_key
                )
                if not is_parent:
                    lca_key = common_ancestor_key
                    break
            if lca_key is None:
                lca_key = sorted_common[0]
            lca_token = lca_key[1]
            table[key_a][key_b] = lca_token
            table[key_b][key_a] = lca_token
    return {key: siblings for key, siblings in table.items() if siblings}


_SIBLINGS_BY_KEY: Final[dict[TokenKey, dict[TokenKey, TaxonomyToken]]] = _build_sibling_lookup()
SIBLINGS_BY_TOKEN: Final[Mapping[TaxonomyToken, Mapping[TaxonomyToken, TaxonomyToken]]] = _TokenLookup(
    {key: _TokenLookup(siblings) for key, siblings in _SIBLINGS_BY_KEY.items()}
)


def compute_sibling_hypernym(token_a: TaxonomyToken, token_b: TaxonomyToken) -> TaxonomyToken | None:
    """Return the closest common ancestor hypernym if tokens are distinct siblings, else None."""
    key_a = _token_key(token_a)
    key_b = _token_key(token_b)
    if key_a == key_b:
        return None
    token_siblings = _SIBLINGS_BY_KEY.get(key_a)
    return token_siblings.get(key_b) if token_siblings is not None else None
