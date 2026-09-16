"""Kelbrum-owned catalogue tags and their manual assignments."""

from collections.abc import Iterable, Mapping
from enum import StrEnum
from functools import cache

import msgspec

from config import derive_payload_identity

TAG_VOCABULARY_VERSION = 'tag-vocabulary-v1'


class TagId(StrEnum):
    """Stable identifiers for the curated Kelbrum tag vocabulary."""

    IMMORTALITY = 'immortality'
    MONSTERIZATION = 'monsterization'
    NECROMANCY = 'necromancy'
    TOURNAMENT = 'tournament'
    ZOMBIE = 'zombie'
    MONSTER_HUNTING = 'monster_hunting'
    NINJA = 'ninja'
    POST_APOCALYPTIC = 'post_apocalyptic'
    CYBERPUNK = 'cyberpunk'
    CULTIVATION = 'cultivation'
    BASKETBALL = 'basketball'
    SOCCER = 'soccer'
    TENNIS = 'tennis'
    BASEBALL = 'baseball'
    VOLLEYBALL = 'volleyball'
    CYCLING = 'cycling'
    BADMINTON = 'badminton'
    ARCHERY = 'archery'
    RUNNING = 'running'
    AMERICAN_FOOTBALL = 'american_football'
    RUGBY = 'rugby'
    SWIMMING = 'swimming'
    SOCIAL_DEDUCTION = 'social_deduction'
    REGRESSION = 'regression'
    TIME_LOOP = 'time_loop'
    TIME_LEAP = 'time_leap'
    GAMBLING = 'gambling'
    REVENGE = 'revenge'
    LEVELING = 'leveling'
    DUNGEON = 'dungeon'
    POLITICS = 'politics'
    NATION_BUILDING = 'nation_building'
    ASSASSIN = 'assassin'
    CREATURE_TAMING = 'creature_taming'
    ABILITY_BATTLES = 'ability_battles'
    HEIST = 'heist'
    TREASURE_HUNTING = 'treasure_hunting'
    PIRATES = 'pirates'
    CARD_BATTLING = 'card_battling'
    PSYCHIC = 'psychic'
    MEMORY_LOSS = 'memory_loss'
    EXORCISM = 'exorcism'
    SUPERHERO = 'superhero'
    ESPIONAGE = 'espionage'
    TRANSFORMATION = 'transformation'
    REBELLION = 'rebellion'
    SYSTEM = 'system'
    VIRTUAL_REALITY = 'virtual_reality'
    AUGMENTED_REALITY = 'augmented_reality'
    ESPORTS = 'esports'
    FOUND_FAMILY = 'found_family'
    MAHJONG = 'mahjong'
    SHOGI = 'shogi'
    GO = 'go'
    ADVENTURING_PARTY = 'adventuring_party'
    CONSPIRACY = 'conspiracy'
    BOXING = 'boxing'
    TABLE_TENNIS = 'table_tennis'
    FIGURE_SKATING = 'figure_skating'
    BATTLE_ROYALE = 'battle_royale'
    BOUNTY_HUNTER = 'bounty_hunter'
    YOKAI = 'yokai'
    STEAMPUNK = 'steampunk'
    BODY_SWAP = 'body_swap'
    GOLF = 'golf'
    RAKUGO = 'rakugo'
    PRISON_SETTING = 'prison_setting'
    AVIATION = 'aviation'
    ASTRONAUT = 'astronaut'
    FAKE_RELATIONSHIP = 'fake_relationship'
    JUDO = 'judo'
    KENDO = 'kendo'
    ALCHEMY = 'alchemy'
    MUSICAL_BAND = 'musical_band'
    LEGAL = 'legal'
    AFTERLIFE = 'afterlife'
    MELANCHOLIC = 'melancholic'
    BLEAK = 'bleak'
    WHIMSICAL = 'whimsical'
    PHILOSOPHICAL = 'philosophical'


class Tag(msgspec.Struct, frozen=True):
    id: str
    label: str
    definition: str | None = None
    standalone_qualification: bool = False


class TagAssignment(msgspec.Struct, frozen=True):
    anime_ids: tuple[int, ...]
    tag_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.anime_ids or any(anime_id <= 0 for anime_id in self.anime_ids):
            raise ValueError('tag assignment IDs must be positive')
        if not self.tag_ids or any(not tag_id for tag_id in self.tag_ids):
            raise ValueError('tag assignments must contain tag IDs')


class TagRegistry(msgspec.Struct, frozen=True):
    """Versioned typed vocabulary resource consumed by feature engineering."""

    version: str
    definitions: tuple[Tag, ...]

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError('tag vocabulary version cannot be empty')
        tag_ids = [tag.id for tag in self.definitions]
        if len(tag_ids) != len(set(tag_ids)) or any(not tag_id for tag_id in tag_ids):
            raise ValueError('tag vocabulary IDs must be unique and non-empty')

    def identity(self) -> str:
        """Return the deterministic identity of this curated resource."""
        return derive_payload_identity(self)


TAGS: tuple[Tag, ...] = (
    Tag(
        id=TagId.IMMORTALITY,
        label='Immortality',
        definition=(
            "A major character's inability to permanently die or indefinite lifespan substantially shapes their "
            'identity, relationships, conflicts, or the narrative.'
        ),
    ),
    Tag(
        id=TagId.MONSTERIZATION,
        label='Monsterization',
        definition=(
            'A major character acquires or develops a fundamentally monstrous or non-human nature, and that change is '
            'central to their identity or story.'
        ),
    ),
    Tag(
        id=TagId.NECROMANCY,
        label='Necromancy',
        definition=(
            'Raising, summoning, controlling, or commanding the dead or undead through supernatural means is a '
            'substantial ability, practice, or narrative mechanism.'
        ),
    ),
    Tag(
        id=TagId.TOURNAMENT,
        label='Tournament',
        definition='The central plot progresses through organized formal matches or rounds toward a decisive outcome.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.ZOMBIE,
        label='Zombie',
        definition='A major character or recurring population is undead, reanimated, or part of a zombie outbreak.',
    ),
    Tag(
        id=TagId.MONSTER_HUNTING,
        label='Monster Hunting',
        definition='The central characters or organization systematically hunt, kill, or contain dangerous monsters.',
    ),
    Tag(
        id=TagId.NINJA,
        label='Ninja',
        definition='Ninja or shinobi identity, training, or operations are central to the story.',
    ),
    Tag(
        id=TagId.POST_APOCALYPTIC,
        label='Post-Apocalyptic',
        definition='The story takes place after civilization has undergone a major catastrophic collapse.',
    ),
    Tag(
        id=TagId.CYBERPUNK,
        label='Cyberpunk',
        definition=(
            'Advanced technology, surveillance, augmentation, corporate or institutional power, inequality, '
            'alienation, or human-technology conflict substantially shapes the setting or narrative.'
        ),
    ),
    Tag(
        id=TagId.CULTIVATION,
        label='Cultivation',
        definition=(
            'Characters develop supernatural power through a structured spiritual or martial cultivation system.'
        ),
    ),
    Tag(
        id=TagId.BASKETBALL,
        label='Basketball',
        definition='Basketball competition, training, or team development is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.SOCCER,
        label='Soccer',
        definition='Soccer competition, training, or team development is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.TENNIS,
        label='Tennis',
        definition='Tennis competition, training, or player development is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.BASEBALL,
        label='Baseball',
        definition='Baseball competition, training, or player development is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.VOLLEYBALL,
        label='Volleyball',
        definition='Volleyball competition, training, or player development is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.CYCLING,
        label='Cycling',
        definition='Cycling competition, training, or rider development is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.BADMINTON,
        label='Badminton',
        definition='Badminton competition, training, or player development is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.ARCHERY,
        label='Archery',
        definition='Archery training or organized competition is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.RUNNING,
        label='Running',
        definition='Running-based training or organized competition is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.AMERICAN_FOOTBALL,
        label='American Football',
        definition='American football training, teams, or organized competition is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.RUGBY,
        label='Rugby',
        definition='Rugby training, teams, or organized competition is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.SWIMMING,
        label='Swimming',
        definition='Swimming competition, training, or athlete development is central to the story.',
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.SOCIAL_DEDUCTION,
        label='Social Deduction',
        definition=(
            'Determining which member or members of an established group are secretly culprits, impostors, traitors, '
            'or enemies through reasoning about their identities, claims, motives, or actions is a major recurring '
            'narrative element.'
        ),
    ),
    Tag(
        id=TagId.REGRESSION,
        label='Regression',
        definition='A character returns to an earlier point in their life with future knowledge and changes events.',
    ),
    Tag(
        id=TagId.TIME_LOOP,
        label='Time Loop',
        definition=(
            'A bounded period repeatedly resets after a trigger, allowing retained knowledge to change later '
            'iterations.'
        ),
    ),
    Tag(
        id=TagId.TIME_LEAP,
        label='Time Leap',
        definition=(
            "Deliberately traveling or transferring oneself or one's consciousness between distinct points in time is "
            'a substantial recurring narrative mechanism, without requiring a repeating reset cycle or a persistent '
            'restart from an earlier life stage.'
        ),
    ),
    Tag(
        id=TagId.GAMBLING,
        label='Gambling',
        definition='High-stakes gambling or wagering games drive the central conflict and strategic progression.',
    ),
    Tag(
        id=TagId.REVENGE,
        label='Revenge',
        definition="A desire for retribution is the protagonist's central motivation and drives the narrative.",
    ),
    Tag(
        id=TagId.LEVELING,
        label='Leveling',
        definition=(
            'Explicit levels, stats, ranks, experience, or comparable quantified progression are a central mechanism '
            'of character advancement.'
        ),
    ),
    Tag(
        id=TagId.DUNGEON,
        label='Dungeon',
        definition=(
            'Exploring, clearing, surviving, or repeatedly operating within dungeon-like environments is a major '
            'recurring element.'
        ),
    ),
    Tag(
        id=TagId.POLITICS,
        label='Politics',
        definition=(
            'Political power, governance, diplomacy, succession, or factional maneuvering substantially drives the '
            'narrative.'
        ),
    ),
    Tag(
        id=TagId.NATION_BUILDING,
        label='Nation Building',
        definition=(
            'Establishing, expanding, governing, or developing a political state or territory is a substantial '
            'recurring part of the narrative.'
        ),
    ),
    Tag(
        id=TagId.ASSASSIN,
        label='Assassin',
        definition='Assassination, professional killers, or assassin training is a major recurring story element.',
    ),
    Tag(
        id=TagId.CREATURE_TAMING,
        label='Creature Taming',
        definition=(
            'Collecting, raising, training, or forming structured partnerships with creatures that accompany or fight '
            'alongside characters is central to the story.'
        ),
    ),
    Tag(
        id=TagId.ABILITY_BATTLES,
        label='Ability Battles',
        definition=(
            'Combat substantially revolves around distinct character-specific abilities whose explicit rules, '
            'constraints, counters, or strategic interactions materially determine fights, distinct from generic '
            'raw-power or martial-arts clashes.'
        ),
    ),
    Tag(
        id=TagId.HEIST,
        label='Heist',
        definition=(
            'Planning and executing elaborate schemes to steal, acquire, or recover valuable targets through '
            'deception, '
            'infiltration, or coordinated operations is central to the story.'
        ),
    ),
    Tag(
        id=TagId.TREASURE_HUNTING,
        label='Treasure Hunting',
        definition=(
            'Searching for and competing to locate hidden treasure or valuable objects through clues, maps, or '
            'exploration is central to the narrative.'
        ),
    ),
    Tag(
        id=TagId.PIRATES,
        label='Pirates',
        definition='Pirate crews, piracy, or a pirate identity and way of life are central to the story.',
    ),
    Tag(
        id=TagId.CARD_BATTLING,
        label='Card Battling',
        definition=(
            'A structured card-game ruleset using cards or decks to conduct battles or competitive matches is central '
            'to the story.'
        ),
    ),
    Tag(
        id=TagId.PSYCHIC,
        label='Psychic',
        definition=(
            'Psychic or extrasensory abilities such as telekinesis, telepathy, or clairvoyance are central to major '
            'characters or the narrative.'
        ),
    ),
    Tag(
        id=TagId.MEMORY_LOSS,
        label='Memory Loss',
        definition=(
            "Loss, suppression, or inability to retain significant memories substantially shapes a major character's "
            'identity, relationships, motivations, or the narrative.'
        ),
    ),
    Tag(
        id=TagId.EXORCISM,
        label='Exorcism',
        definition=(
            'Exorcising, purifying, sealing, dispelling, or otherwise spiritually removing supernatural entities or '
            'corruption is a central activity or conflict.'
        ),
    ),
    Tag(
        id=TagId.SUPERHERO,
        label='Superhero',
        definition=(
            'Superheroes, supervillains, or a superhero-style society or ecosystem of extraordinary identities, public '
            'or criminal personas, and organized hero-villain conflict substantially structure the narrative.'
        ),
    ),
    Tag(
        id=TagId.ESPIONAGE,
        label='Espionage',
        definition=(
            'Intelligence gathering, infiltration, covert operations, or maintaining undercover identities for '
            'intelligence purposes is central to the story.'
        ),
    ),
    Tag(
        id=TagId.TRANSFORMATION,
        label='Transformation',
        definition=(
            'Assuming a distinct empowered identity or alternate bodily form through an explicit transformation '
            'mechanism is central to the story, without the transformation representing acquisition of a fundamentally '
            'monstrous or non-human nature.'
        ),
    ),
    Tag(
        id=TagId.REBELLION,
        label='Rebellion',
        definition=(
            'Organized resistance or uprising against an established government, occupying power, or ruling authority '
            'is central to the narrative.'
        ),
    ),
    Tag(
        id=TagId.SYSTEM,
        label='System',
        definition=(
            'A major character interacts with an explicit game-like framework exposing stats, skills, levels, quests, '
            'classes, inventories, achievements, or similar structured rules.'
        ),
    ),
    Tag(
        id=TagId.VIRTUAL_REALITY,
        label='Virtual Reality',
        definition="Immersive virtual or simulated reality is a central setting and source of the story's conflicts.",
    ),
    Tag(
        id=TagId.AUGMENTED_REALITY,
        label='Augmented Reality',
        definition=(
            'Technology overlays interactive digital content onto the physical world and is central to the story.'
        ),
    ),
    Tag(
        id=TagId.ESPORTS,
        label='Esports',
        definition=(
            'Organized competitive video gaming, professional players, teams, leagues, or tournaments are central to '
            'the narrative.'
        ),
    ),
    Tag(
        id=TagId.FOUND_FAMILY,
        label='Found Family',
        definition=(
            'A central, enduring group of otherwise unrelated characters develops a family-like bond through shared '
            'experiences, mutual care, and commitment.'
        ),
    ),
    Tag(
        id=TagId.MAHJONG,
        label='Mahjong',
        definition=(
            "Playing or competing in mahjong is a central recurring activity driving the narrative or characters' "
            'goals.'
        ),
    ),
    Tag(
        id=TagId.SHOGI,
        label='Shogi',
        definition=(
            "Playing or competing in shogi is a central recurring activity driving the narrative or characters' goals."
        ),
    ),
    Tag(
        id=TagId.GO,
        label='Go',
        definition=(
            "Playing or competing in Go is a central recurring activity driving the narrative or characters' goals."
        ),
    ),
    Tag(
        id=TagId.ADVENTURING_PARTY,
        label='Adventuring Party',
        definition=(
            'A persistent group of characters who adventure together as a coordinated party substantially structures '
            "the narrative's exploration, quests, combat, or progression."
        ),
    ),
    Tag(
        id=TagId.CONSPIRACY,
        label='Conspiracy',
        definition=(
            'A hidden coordinated plan by powerful individuals or organizations substantially drives the narrative, '
            'conflict, or investigation.'
        ),
    ),
    Tag(
        id=TagId.BOXING,
        label='Boxing',
        definition=(
            'Competitive boxing matches, training, or ring competition substantially structure the narrative and '
            'character development.'
        ),
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.TABLE_TENNIS,
        label='Table Tennis',
        definition=(
            'Competitive table tennis (ping pong) matches, club activities, or tournaments are central to the story.'
        ),
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.FIGURE_SKATING,
        label='Figure Skating',
        definition=(
            'Competitive or exhibition figure skating routines, choreography, and ice rink training substantially '
            'drive the narrative.'
        ),
        standalone_qualification=True,
    ),
    Tag(
        id=TagId.BATTLE_ROYALE,
        label='Battle Royale',
        definition=(
            'An explicit, rule-bound elimination contest where participants are forced or incentivized to eliminate '
            'or kill one another until a single victor or surviving group remains.'
        ),
    ),
    Tag(
        id=TagId.BOUNTY_HUNTER,
        label='Bounty Hunter',
        definition=(
            'Tracking, apprehending, or claiming rewards on criminal bounties or fugitives serves as a primary '
            'profession and episodic plot driver for central characters.'
        ),
    ),
    Tag(
        id=TagId.YOKAI,
        label='Yokai',
        definition=(
            'Yōkai, ayakashi, or closely equivalent Japanese folkloric supernatural beings substantially drive the '
            'setting, characters, or narrative, distinct from generic western spirits or abstract deities.'
        ),
    ),
    Tag(
        id=TagId.STEAMPUNK,
        label='Steampunk',
        definition=(
            'Steam-powered machinery, clockwork engineering, or retro-futuristic Victorian industrial technology '
            "fundamentally defines the fictional world's infrastructure, vehicles, or weapons."
        ),
    ),
    Tag(
        id=TagId.BODY_SWAP,
        label='Body Swap',
        definition=(
            'Two or more characters swap physical bodies, or exchange consciousnesses between bodies, as a central '
            'recurring narrative device or primary source of interpersonal conflict.'
        ),
    ),
    Tag(
        id=TagId.GOLF,
        label='Golf',
        definition=('Competitive or recreational golf serves as the primary athletic focus and narrative driver.'),
    ),
    Tag(
        id=TagId.RAKUGO,
        label='Rakugo',
        definition=(
            'Traditional Japanese rakugo (solo comedic or dramatic monologue storytelling) serves as a central '
            'discipline, career path, or focal art form for primary characters.'
        ),
    ),
    Tag(
        id=TagId.PRISON_SETTING,
        label='Prison Setting',
        definition=(
            'A prison, penal institution, detention facility, or equivalent carceral environment serves as a primary '
            'recurring setting and materially structures the narrative.'
        ),
    ),
    Tag(
        id=TagId.AVIATION,
        label='Aviation',
        definition=(
            'Piloting, designing, operating, or pursuing atmospheric aviation substantially drives the narrative.'
        ),
    ),
    Tag(
        id=TagId.ASTRONAUT,
        label='Astronaut',
        definition=(
            'Astronaut training, professional space operations, or crewed spaceflight substantially drives the '
            'narrative.'
        ),
    ),
    Tag(
        id=TagId.FAKE_RELATIONSHIP,
        label='Fake Relationship',
        definition=(
            'Two or more characters enter into an explicit mutual agreement or deception to pretend to be romantic '
            'partners or a married couple to third parties.'
        ),
    ),
    Tag(
        id=TagId.JUDO,
        label='Judo',
        definition=('Competitive or traditional judo serves as the primary athletic focus and narrative driver.'),
    ),
    Tag(
        id=TagId.KENDO,
        label='Kendo',
        definition=('Competitive or traditional kendo serves as the primary athletic focus and narrative driver.'),
    ),
    Tag(
        id=TagId.ALCHEMY,
        label='Alchemy',
        definition=(
            'Transmutation, chemical or material synthesis, potion brewing, or pseudo-scientific matter conversion '
            'serves as a central discipline and narrative mechanic.'
        ),
    ),
    Tag(
        id=TagId.MUSICAL_BAND,
        label='Musical Band',
        definition=(
            'Forming, practicing, and performing in a collaborative contemporary musical band (such as a rock, indie, '
            'pop, metal, or concert/brass ensemble) is the central structural engine of the plot and character '
            'development.'
        ),
    ),
    Tag(
        id=TagId.LEGAL,
        label='Legal',
        definition=(
            'Formal judicial proceedings, courtroom trials, legal debates, or defense attorney and prosecutor casework '
            'materially structure the investigation and narrative resolution.'
        ),
    ),
    Tag(
        id=TagId.AFTERLIFE,
        label='Afterlife',
        definition=(
            'An afterlife, limbo, purgatory, or underworld realm serves as a central ongoing setting and '
            'substantially structures character goals, judgments, or transitions.'
        ),
    ),
    Tag(
        id=TagId.MELANCHOLIC,
        label='Melancholic',
        definition=(
            'A persistent atmosphere of quiet sorrow, loneliness, impermanence, or bittersweet yearning '
            '(mono no aware) consistently permeates the aesthetic, character reflections, and narrative tone.'
        ),
    ),
    Tag(
        id=TagId.BLEAK,
        label='Bleak',
        definition=(
            'An oppressive, unforgiving world where moral compromise is mandatory, triumph is Pyrrhic or fleeting, '
            'and suffering, brutality, or fatalism fundamentally structures the narrative environment.'
        ),
    ),
    Tag(
        id=TagId.WHIMSICAL,
        label='Whimsical',
        definition=(
            'A dreamlike, offbeat, or fairytale-like atmosphere where eccentric logic, magical realism, or playful '
            'absurdity governs the world rather than grounded or hard-magic rules.'
        ),
    ),
    Tag(
        id=TagId.PHILOSOPHICAL,
        label='Philosophical',
        definition=(
            'Abstract inquiries into epistemology, metaphysics, ethics, free will, the nature of consciousness, '
            'or human existence directly structure the central narrative conflicts and character reflections.'
        ),
    ),
)

TAG_REGISTRY = TagRegistry(TAG_VOCABULARY_VERSION, TAGS)


@cache
def tag_registry_identity() -> str:
    """Return the cached identity of the feature tag vocabulary."""
    return TAG_REGISTRY.identity()


def apply_tag_assignments(
    anime_ids: Iterable[int],
    assignments: Iterable[TagAssignment],
    tags: Iterable[Tag] = TAG_REGISTRY.definitions,
) -> dict[int, tuple[str, ...]]:
    """Return deterministic tag assignments for IDs present in the catalogue."""
    available_ids = set(anime_ids)
    tag_ids = {tag.id for tag in tags}
    result: dict[int, set[str]] = {}
    for assignment in assignments:
        unknown = set(assignment.tag_ids) - tag_ids
        if unknown:
            raise ValueError(f'unknown tag IDs: {sorted(unknown)}')
        for anime_id in assignment.anime_ids:
            if anime_id in available_ids:
                result.setdefault(anime_id, set()).update(assignment.tag_ids)
    order = {tag.id: index for index, tag in enumerate(tags)}
    return {anime_id: tuple(sorted(values, key=order.__getitem__)) for anime_id, values in result.items()}


def validate_tags_against_taxonomy(tags: Iterable[Tag], taxonomy: Mapping[str, Iterable[str]]) -> None:
    """Reject Kelbrum tags that duplicate source taxonomy values."""
    source_values = {value.casefold() for values in taxonomy.values() for value in values}
    seen_ids: set[str] = set()
    for tag in tags:
        if not tag.id or tag.id in seen_ids:
            raise ValueError(f'duplicate or empty tag ID: {tag.id!r}')
        if tag.label.casefold() in source_values:
            raise ValueError(f'tag overlaps source taxonomy: {tag.label}')
        seen_ids.add(tag.id)
