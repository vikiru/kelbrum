"""Canonical Kelbrum tag vocabulary and narrative policy tag groups."""

from enum import StrEnum
from typing import Final


class Tag(StrEnum):
    """Stable identifiers for the curated Kelbrum tag vocabulary."""

    IMMORTALITY = 'immortality'
    MONSTERIZATION = 'monsterization'
    NECROMANCY = 'necromancy'
    TOURNAMENT = 'tournament'
    ZOMBIE = 'zombie'
    MONSTER_HUNTING = 'monster_hunting'
    NINJA = 'ninja'
    APOCALYPSE = 'apocalypse'
    POST_APOCALYPTIC = 'post_apocalyptic'
    ENVIRONMENTAL_COLLAPSE = 'environmental_collapse'
    URBAN_SETTING = 'urban_setting'
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
    MARKSMANSHIP = 'marksmanship'
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
    POLITICAL = 'political'
    POLITICS = 'political'
    KINGDOM_BUILDING = 'kingdom_building'
    NATION_BUILDING = 'kingdom_building'
    MODERN_KNOWLEDGE = 'modern_knowledge'
    ALIENS = 'aliens'
    THRILLER = 'thriller'
    ASSASSIN = 'assassin'
    GANGS = 'gangs'
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
    SPY = 'spy'
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
    MERCENARY = 'mercenary'
    YOKAI = 'yokai'
    STEAMPUNK = 'steampunk'
    VICTORIAN = 'victorian'
    BODY_SWAP = 'body_swap'
    GOLF = 'golf'
    RAKUGO = 'rakugo'
    PRISON_SETTING = 'prison_setting'
    CAPTIVITY = 'captivity'
    AVIATION = 'aviation'
    ASTRONAUT = 'astronaut'
    FAKE_RELATIONSHIP = 'fake_relationship'
    JUDO = 'judo'
    KENDO = 'kendo'
    ALCHEMY = 'alchemy'
    MUSICAL_BAND = 'musical_band'
    LEGAL = 'legal'
    LAWYERS = 'lawyers'
    WORK_LIFE = 'work_life'
    CAREER_AMBITION = 'career_ambition'
    AFTERLIFE = 'afterlife'
    MELANCHOLIC = 'melancholic'
    BLEAK = 'bleak'
    NOIR = 'noir'
    LIFESTYLE_CHANGE = 'lifestyle_change'
    GODS = 'gods'
    ROYALTY = 'royalty'
    SWORDSMANSHIP = 'swordsmanship'
    BODYGUARDS = 'bodyguards'
    MEDIEVAL = 'medieval'
    PERSON_IN_A_STRANGE_WORLD = 'person_in_a_strange_world'
    GENIUS_PROTAGONIST = 'genius_protagonist'
    STRATEGIC_PROTAGONIST = 'strategic_protagonist'
    MIND_GAMES = 'mind_games'
    CHILD_PROTAGONIST = 'child_protagonist'
    ADULT_PROTAGONIST = 'adult_protagonist'
    MALE_PROTAGONIST = 'male_protagonist'
    FEMALE_PROTAGONIST = 'female_protagonist'
    NON_HUMAN_PROTAGONIST = 'non_human_protagonist'
    ENSEMBLE_CAST = 'ensemble_cast'
    WHIMSICAL = 'whimsical'
    PHILOSOPHICAL = 'philosophical'
    AGRICULTURE = 'agriculture'
    BILLIARDS = 'billiards'
    COOKING = 'cooking'
    RESTAURANT_CAFE = 'restaurant_cafe'
    GYMNASTICS = 'gymnastics'
    HOCKEY = 'hockey'
    ICE_SKATING = 'ice_skating'
    MOUNTAINEERING = 'mountaineering'
    SCUBA_DIVING = 'scuba_diving'
    SKATEBOARDING = 'skateboarding'
    SKIING = 'skiing'
    SUMO = 'sumo'
    SURFING = 'surfing'
    TRACK_AND_FIELD = 'track_and_field'
    WATER_POLO = 'water_polo'
    WRESTLING = 'wrestling'
    WEIGHTLIFTING = 'weightlifting'
    COOKING_COMPETITION = 'cooking_competition'
    BAKING = 'baking'
    REVERSE_ISEKAI = 'reverse_isekai'
    TRANSMIGRATION = 'transmigration'
    TRANSPORTED_INTO_FICTION = 'transported_into_fiction'
    EPISODIC = 'episodic'
    ANTHOLOGY = 'anthology'
    SERIALIZED = 'serialized'
    PROCEDURAL = 'procedural'
    OCCULT = 'occult'
    TOWER_CLIMBING = 'tower_climbing'
    DANCING = 'dancing'
    CALLIGRAPHY = 'calligraphy'
    CAMPING = 'camping'
    FENCING = 'fencing'
    HIDDEN_IDENTITY = 'hidden_identity'
    WEAK_TO_STRONG = 'weak_to_strong'
    OVERPOWERED_PROTAGONIST = 'overpowered_protagonist'
    DYSTOPIAN = 'dystopian'
    UTOPIAN = 'utopian'
    FIREFIGHTER = 'firefighter'
    MERCHANT = 'merchant'
    MURDER_MYSTERY = 'murder_mystery'
    SERIAL_KILLER = 'serial_killer'
    UNDERCOVER = 'undercover'
    ALTERNATE_HISTORY = 'alternate_history'
    ANTIHERO = 'antihero'
    ACADEMY = 'academy'
    SCHOOL_CLUB = 'school_club'
    PROPHECY = 'prophecy'
    SEALED_POWER = 'sealed_power'
    SUMMONING = 'summoning'
    CONTRACT = 'contract'
    SUMMONED_TO_ANOTHER_WORLD = 'summoned_to_another_world'
    TRAPPED_IN_GAME = 'trapped_in_game'
    GAME_WORLD_BECOMES_REALITY = 'game_world_becomes_reality'
    WORLD_HOPPING = 'world_hopping'
    WAR = 'war'
    CHILDHOOD_FRIENDS = 'childhood_friends'
    BETRAYAL = 'betrayal'
    BULLYING = 'bullying'
    GRIEF = 'grief'
    CRIME = 'crime'
    RIVALRY = 'rivalry'
    COMING_OF_AGE = 'coming_of_age'
    BODY_HORROR = 'body_horror'
    SHAPESHIFTING = 'shapeshifting'
    DEATH_GAME = 'death_game'
    FAMILY = 'family'
    UNDEAD = 'undead'
    MONSTERS = 'monsters'
    IDENTITY_CONFLICT = 'identity_conflict'
    HUMAN_NONHUMAN_HYBRID = 'human_nonhuman_hybrid'
    HUMAN_NONHUMAN_CONFLICT = 'human_nonhuman_conflict'
    HIDDEN_NONHUMAN_SOCIETY = 'hidden_nonhuman_society'
    OUTER_SPACE = 'outer_space'
    TRANSFER_STUDENT = 'transfer_student'
    CAUGHT_BETWEEN_SIDES = 'caught_between_sides'
    CRAFTING = 'crafting'
    SCIENCE = 'science'
    PUZZLES = 'puzzles'
    ACADEMIC_COMPETITION = 'academic_competition'
    PERSECUTION = 'persecution'
    PREDATION = 'predation'
    SOCIAL_ISOLATION = 'social_isolation'
    JOURNEY = 'journey'
    COUNTRYSIDE = 'countryside'
    DISABILITY = 'disability'
    REDEMPTION = 'redemption'
    TRAUMA = 'trauma'
    SUPERNATURAL_ENCOUNTERS = 'supernatural_encounters'
    DEATHMATCH = 'deathmatch'
    BODY_SHARING = 'body_sharing'
    CLOSED_SOCIETY = 'closed_society'
    EXPERIMENTAL_SUBJECTS = 'experimental_subjects'
    OUTBREAK = 'outbreak'
    VIGILANTES = 'vigilantes'
    DARK = 'dark'
    PRECOGNITION = 'precognition'
    SECRET_ORGANIZATION = 'secret_organization'  # noqa: S105
    ANDROID = 'android'
    ARTIFICIAL_INTELLIGENCE = 'artificial_intelligence'
    GRANTED_POWER = 'granted_power'
    HIDDEN_STRENGTH = 'hidden_strength'
    TRAINING = 'training'
    TRIALS = 'trials'
    POWER_SYSTEM = 'power_system'
    FORBIDDEN_KNOWLEDGE = 'forbidden_knowledge'
    IDEOLOGICAL_CONFLICT = 'ideological_conflict'
    GENERATIONAL_STORY = 'generational_story'
    LEGACY = 'legacy'
    MORTALITY = 'mortality'
    SACRIFICE = 'sacrifice'
    POSSESSION = 'possession'
    CURSE = 'curse'
    MENTOR_STUDENT_RELATIONSHIP = 'mentor_student_relationship'
    RELIGION = 'religion'
    MASTER_SERVANT = 'master_servant'
    CULT = 'cult'
    BLOODLINE = 'bloodline'
    ARTIFACT = 'artifact'
    CAT_AND_MOUSE = 'cat_and_mouse'
    INVESTIGATION = 'investigation'
    MIND_CONTROL = 'mind_control'
    MILITARY_STRATEGY = 'military_strategy'
    POLITICAL_VIOLENCE = 'political_violence'
    DEMONS = 'demons'
    INTERSPECIES_RELATIONSHIP = 'interspecies_relationship'
    INTERSPECIES_CONFLICT = 'interspecies_conflict'
    SOCIAL_HIERARCHY = 'social_hierarchy'
    LIBERATION = 'liberation'
    EXPLORATION = 'exploration'
    SPIRIT_WORLD = 'spirit_world'
    FINANCIAL_HARDSHIP = 'financial_hardship'
    NATURAL_DISASTER = 'natural_disaster'
    ARRANGED_MARRIAGE = 'arranged_marriage'
    COHABITATION = 'cohabitation'
    SERIOUS_ILLNESS = 'serious_illness'
    MARRIED_LIFE = 'married_life'
    FISHING = 'fishing'
    KARUTA = 'karuta'
    MEMORY_MANIPULATION = 'memory_manipulation'
    CLASSICAL_MUSIC = 'classical_music'
    CYBERNETICS = 'cybernetics'
    MEDIA_PRODUCTION = 'media_production'
    FRIENDSHIP = 'friendship'
    COMMUNITY_LIFE = 'community_life'
    PARALLEL_WORLDS = 'parallel_worlds'
    DREAM_WORLDS = 'dream_worlds'
    RECONCILIATION = 'reconciliation'
    DRAGONS = 'dragons'
    WITCH = 'witch'
    DINOSAURS = 'dinosaurs'
    UNDERWATER_SETTING = 'underwater_setting'
    UNDERGROUND_SETTING = 'underground_setting'
    PHOTOGRAPHY = 'photography'
    JOURNALISM = 'journalism'
    CLONING = 'cloning'
    ENSLAVEMENT = 'enslavement'
    ABANDONMENT = 'abandonment'
    ACTS_OF_TERROR = 'acts_of_terror'
    ABUSIVE_TREATMENT = 'abusive_treatment'
    PARTNER_BATTLING = 'partner_battling'
    TOY_BATTLING = 'toy_battling'
    DYSFUNCTIONAL_FAMILY = 'dysfunctional_family'
    ELEMENTAL_POWERS = 'elemental_powers'
    FRAMED_FOR_A_CRIME = 'framed_for_a_crime'
    HACKING = 'hacking'
    HISTORICAL_FIGURES = 'historical_figures'
    KIDNAPPING = 'kidnapping'
    LONELINESS = 'loneliness'
    MONSTER_OF_THE_WEEK = 'monster_of_the_week'
    MOTORSPORT = 'motorsport'
    ORPHAN = 'orphan'
    SECOND_CHANCE = 'second_chance'
    SIBLINGS = 'siblings'
    SOCIAL_ANXIETY = 'social_anxiety'
    SPLIT_PERSONALITY = 'split_personality'
    TEEN_PROTAGONIST = 'teen_protagonist'
    URBAN_LEGEND = 'urban_legend'
    WEREWOLVES = 'werewolves'
    GUILDS = 'guilds'
    SPIRIT_MANIFESTATION = 'spirit_manifestation'
    LAW_ENFORCEMENT = 'law_enforcement'
    ADOPTION = 'adoption'
    FAIRIES = 'fairies'
    GHOSTS = 'ghosts'
    ANGELS = 'angels'
    UNREQUITED_LOVE = 'unrequited_love'
    FORBIDDEN_ROMANCE = 'forbidden_romance'
    ENEMIES_TO_LOVERS = 'enemies_to_lovers'
    AGE_GAP_ROMANCE = 'age_gap_romance'
    HEARTWARMING = 'heartwarming'
    SATIRE = 'satire'
    ABSURDIST = 'absurdist'
    BITTERSWEET = 'bittersweet'
    TRAGEDY = 'tragedy'
    SLOW_LIFE = 'slow_life'
    SPACE_OPERA = 'space_opera'
    GLADIATOR = 'gladiator'
    STOIC_PROTAGONIST = 'stoic_protagonist'
    THEATER = 'theater'
    PAINTING_DRAWING = 'painting_drawing'
    MANGA_ANIME_CREATION = 'manga_anime_creation'
    VOICE_ACTING = 'voice_acting'
    APOTHECARY = 'apothecary'
    NOSTALGIC = 'nostalgic'


NARRATIVE_POLICY_TAGS: Final[frozenset[Tag]] = frozenset({Tag.ANTHOLOGY, Tag.SERIALIZED, Tag.EPISODIC, Tag.PROCEDURAL})

PERSONA_CAST_TAGS: Final[frozenset[Tag]] = frozenset(
    {
        Tag.ADULT_PROTAGONIST,
        Tag.CHILD_PROTAGONIST,
        Tag.ENSEMBLE_CAST,
        Tag.FEMALE_PROTAGONIST,
        Tag.GENIUS_PROTAGONIST,
        Tag.HIDDEN_STRENGTH,
        Tag.MALE_PROTAGONIST,
        Tag.NON_HUMAN_PROTAGONIST,
        Tag.OVERPOWERED_PROTAGONIST,
        Tag.SIBLINGS,
        Tag.STOIC_PROTAGONIST,
        Tag.STRATEGIC_PROTAGONIST,
        Tag.TEEN_PROTAGONIST,
        Tag.TRANSFER_STUDENT,
    }
)

CORE_HOOK_TAGS: Final[frozenset[Tag]] = frozenset(
    {
        Tag.ACADEMIC_COMPETITION,
        Tag.ADVENTURING_PARTY,
        Tag.ALCHEMY,
        Tag.AMERICAN_FOOTBALL,
        Tag.BADMINTON,
        Tag.BASEBALL,
        Tag.BASKETBALL,
        Tag.BATTLE_ROYALE,
        Tag.BILLIARDS,
        Tag.BLOODLINE,
        Tag.BODY_HORROR,
        Tag.BODY_SWAP,
        Tag.BOXING,
        Tag.CARD_BATTLING,
        Tag.COOKING_COMPETITION,
        Tag.DEATH_GAME,
        Tag.DEATHMATCH,
        Tag.DREAM_WORLDS,
        Tag.FENCING,
        Tag.FIGURE_SKATING,
        Tag.GAME_WORLD_BECOMES_REALITY,
        Tag.GO,
        Tag.GOLF,
        Tag.HEIST,
        Tag.MIND_CONTROL,
        Tag.MONSTERIZATION,
        Tag.MURDER_MYSTERY,
        Tag.PARALLEL_WORLDS,
        Tag.PERSON_IN_A_STRANGE_WORLD,
        Tag.PROPHECY,
        Tag.REGRESSION,
        Tag.REVERSE_ISEKAI,
        Tag.RUGBY,
        Tag.SHOGI,
        Tag.SOCCER,
        Tag.SUMMONED_TO_ANOTHER_WORLD,
        Tag.SUMMONING,
        Tag.SUMO,
        Tag.TABLE_TENNIS,
        Tag.TENNIS,
        Tag.TIME_LEAP,
        Tag.TIME_LOOP,
        Tag.TRANSMIGRATION,
        Tag.TRANSPORTED_INTO_FICTION,
        Tag.TRAPPED_IN_GAME,
        Tag.VOLLEYBALL,
        Tag.WATER_POLO,
        Tag.WRESTLING,
    }
)

TONE_ATMOSPHERE_TAGS: Final[frozenset[Tag]] = frozenset(
    {
        Tag.ABANDONMENT,
        Tag.ABSURDIST,
        Tag.ABUSIVE_TREATMENT,
        Tag.ACTS_OF_TERROR,
        Tag.ADOPTION,
        Tag.AFTERLIFE,
        Tag.AGE_GAP_ROMANCE,
        Tag.ALTERNATE_HISTORY,
        Tag.APOCALYPSE,
        Tag.ARRANGED_MARRIAGE,
        Tag.BETRAYAL,
        Tag.BITTERSWEET,
        Tag.BLEAK,
        Tag.BULLYING,
        Tag.CAPTIVITY,
        Tag.CAT_AND_MOUSE,
        Tag.CAUGHT_BETWEEN_SIDES,
        Tag.CHILDHOOD_FRIENDS,
        Tag.CLASSICAL_MUSIC,
        Tag.COMING_OF_AGE,
        Tag.CONSPIRACY,
        Tag.DARK,
        Tag.DISABILITY,
        Tag.DYSFUNCTIONAL_FAMILY,
        Tag.DYSTOPIAN,
        Tag.ENEMIES_TO_LOVERS,
        Tag.ENSLAVEMENT,
        Tag.ENVIRONMENTAL_COLLAPSE,
        Tag.FAKE_RELATIONSHIP,
        Tag.FINANCIAL_HARDSHIP,
        Tag.FORBIDDEN_KNOWLEDGE,
        Tag.FORBIDDEN_ROMANCE,
        Tag.FOUND_FAMILY,
        Tag.FRAMED_FOR_A_CRIME,
        Tag.GAMBLING,
        Tag.GANGS,
        Tag.GENERATIONAL_STORY,
        Tag.GRIEF,
        Tag.HEARTWARMING,
        Tag.MELANCHOLIC,
        Tag.MEMORY_LOSS,
        Tag.MORTALITY,
        Tag.NATURAL_DISASTER,
        Tag.NOSTALGIC,
        Tag.OUTBREAK,
        Tag.PERSECUTION,
        Tag.PHILOSOPHICAL,
        Tag.POST_APOCALYPTIC,
        Tag.PREDATION,
        Tag.RECONCILIATION,
        Tag.REDEMPTION,
        Tag.REVENGE,
        Tag.SACRIFICE,
        Tag.SATIRE,
        Tag.SECOND_CHANCE,
        Tag.SERIAL_KILLER,
        Tag.SERIOUS_ILLNESS,
        Tag.THRILLER,
        Tag.TRAGEDY,
        Tag.TRAUMA,
        Tag.UNREQUITED_LOVE,
    }
)

SETTING_BACKDROP_TAGS: Final[frozenset[Tag]] = frozenset(
    {
        Tag.ACADEMY,
        Tag.AGRICULTURE,
        Tag.APOTHECARY,
        Tag.ARCHERY,
        Tag.ASTRONAUT,
        Tag.AVIATION,
        Tag.BAKING,
        Tag.CAMPING,
        Tag.CAREER_AMBITION,
        Tag.CLOSED_SOCIETY,
        Tag.COHABITATION,
        Tag.COMMUNITY_LIFE,
        Tag.COOKING,
        Tag.COUNTRYSIDE,
        Tag.CRAFTING,
        Tag.CYCLING,
        Tag.FAMILY,
        Tag.FIREFIGHTER,
        Tag.FISHING,
        Tag.FRIENDSHIP,
        Tag.GUILDS,
        Tag.GYMNASTICS,
        Tag.MEDIA_PRODUCTION,
        Tag.MOUNTAINEERING,
        Tag.MUSICAL_BAND,
        Tag.OUTER_SPACE,
        Tag.PAINTING_DRAWING,
        Tag.PHOTOGRAPHY,
        Tag.PRISON_SETTING,
        Tag.RAKUGO,
        Tag.RESTAURANT_CAFE,
        Tag.ROYALTY,
        Tag.RUNNING,
        Tag.SCHOOL_CLUB,
        Tag.SCIENCE,
        Tag.SCUBA_DIVING,
        Tag.SKATEBOARDING,
        Tag.SKIING,
        Tag.SLOW_LIFE,
        Tag.SOCIAL_HIERARCHY,
        Tag.SURFING,
        Tag.SWIMMING,
        Tag.THEATER,
        Tag.TRACK_AND_FIELD,
        Tag.TRAINING,
        Tag.UNDERGROUND_SETTING,
        Tag.UNDERWATER_SETTING,
        Tag.URBAN_SETTING,
        Tag.VICTORIAN,
        Tag.VOICE_ACTING,
        Tag.WEIGHTLIFTING,
        Tag.WORK_LIFE,
    }
)
