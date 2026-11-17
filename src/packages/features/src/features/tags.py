"""Kelbrum-owned catalogue tags and their manual assignments."""

from collections.abc import Iterable, Mapping
from enum import Enum
from functools import cache, lru_cache
from typing import Final

import msgspec

from anime_catalogue.tags import CORE_HOOK_TAGS as CORE_HOOK_TAGS
from anime_catalogue.tags import NARRATIVE_POLICY_TAGS as NARRATIVE_POLICY_TAGS
from anime_catalogue.tags import PERSONA_CAST_TAGS as PERSONA_CAST_TAGS
from anime_catalogue.tags import SETTING_BACKDROP_TAGS as SETTING_BACKDROP_TAGS
from anime_catalogue.tags import TONE_ATMOSPHERE_TAGS as TONE_ATMOSPHERE_TAGS
from anime_catalogue.tags import Tag as Tag
from config import derive_payload_identity

TAG_VOCABULARY_VERSION = 'tag-vocabulary-v2'


class TagSalienceTier(float, Enum):
    """Clean domain model establishing narrative specificity tiers for tag evidence."""

    CORE_HOOK = 1.45
    TONE_ATMOSPHERE = 1.30
    MOTIF_ORGANISM = 0.85
    SETTING_BACKDROP = 0.45
    PERSONA_CAST = 0.20


@lru_cache(maxsize=8192)
def _similarity_tag_ids_cached(tag_ids: frozenset[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(tag_id for tag_id in tag_ids if tag_id not in NARRATIVE_POLICY_TAGS)


def similarity_tag_ids(tag_ids: Iterable[str]) -> tuple[str, ...]:
    """Keep narrative form available to policy without counting it as content evidence."""
    if isinstance(tag_ids, (frozenset, tuple)):
        return _similarity_tag_ids_cached(tag_ids)
    return tuple(tag_id for tag_id in tag_ids if tag_id not in NARRATIVE_POLICY_TAGS)


class TagDefinition(msgspec.Struct, frozen=True):
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
    definitions: tuple[TagDefinition, ...]

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError('tag vocabulary version cannot be empty')
        tag_ids = [tag.id for tag in self.definitions]
        if len(tag_ids) != len(set(tag_ids)) or any(not tag_id for tag_id in tag_ids):
            raise ValueError('tag vocabulary IDs must be unique and non-empty')

    def identity(self) -> str:
        """Return the deterministic identity of this curated resource."""
        return derive_payload_identity(self)


TAGS: tuple[TagDefinition, ...] = (
    TagDefinition(
        id=Tag.IMMORTALITY,
        label='Immortality',
        definition=(
            "A major character's inability to permanently die or indefinite lifespan substantially shapes their "
            'identity, relationships, conflicts, or the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.MONSTERIZATION,
        label='Monsterization',
        definition=(
            'A major character acquires or develops a fundamentally monstrous or non-human nature, and that change is '
            'central to their identity or story.'
        ),
    ),
    TagDefinition(
        id=Tag.BODY_HORROR,
        label='Body Horror',
        definition=(
            'Disturbing transformation, mutation, deformation, invasion, or violation of the body is a substantial '
            'recurring source of horror or discomfort; ordinary injury or gore alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SHAPESHIFTING,
        label='Shapeshifting',
        definition=(
            'Changing physical form is a recurring or central ability or premise; this is distinct from transformation '
            'as an empowered alternate identity or form, and from acquiring a fundamentally monstrous nature.'
        ),
    ),
    TagDefinition(
        id=Tag.NECROMANCY,
        label='Necromancy',
        definition=(
            'Raising, summoning, controlling, or commanding the dead or undead through supernatural means is a '
            'substantial ability, practice, or narrative mechanism.'
        ),
    ),
    TagDefinition(
        id=Tag.TOURNAMENT,
        label='Tournament',
        definition='The central plot progresses through organized formal matches or rounds toward a decisive outcome.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.ZOMBIE,
        label='Zombie',
        definition='A major character or recurring population is undead, reanimated, or part of a zombie outbreak.',
    ),
    TagDefinition(
        id=Tag.UNDEAD,
        label='Undead',
        definition=(
            'Undead beings such as reanimated corpses, revenants, liches, or skeletons that exist beyond biological '
            'death are central characters or a substantial recurring population; zombie is a more specific subtype.'
        ),
    ),
    TagDefinition(
        id=Tag.MONSTERS,
        label='Monsters',
        definition=(
            'Creatures explicitly treated as monsters or monstrous beings are a central recurring presence in the '
            'setting, conflict, or cast; isolated creatures or ordinary non-human species do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MONSTER_HUNTING,
        label='Monster Hunting',
        definition='The central characters or organization systematically hunt, kill, or contain dangerous monsters.',
    ),
    TagDefinition(
        id=Tag.PERSECUTION,
        label='Persecution',
        definition=(
            'A population or group is systematically targeted, detained, exploited, suppressed, or harmed because of '
            'its identity or nature, particularly by authorities, institutions, or dominant social groups.'
        ),
    ),
    TagDefinition(
        id=Tag.LIBERATION,
        label='Liberation',
        definition=(
            'Freeing a population, territory, or group from captivity, occupation, slavery, persecution, or oppressive '
            'rule is a substantial objective or narrative development; personal escape alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.PREDATION,
        label='Predation',
        definition=(
            'Sentient beings or populations are regularly hunted, fed upon, or consumed as prey by another species or '
            'group, and this predator-prey relationship substantially shapes the story.'
        ),
    ),
    TagDefinition(
        id=Tag.SOCIAL_ISOLATION,
        label='Social Isolation',
        definition=(
            "A major character's lack of meaningful social connection, exclusion from others, or sustained withdrawal "
            'from relationships substantially shapes their life, development, or the story.'
        ),
    ),
    TagDefinition(
        id=Tag.JOURNEY,
        label='Journey',
        definition=(
            'Extended travel through multiple locations is a substantial part of the narrative, with the '
            'journey itself shaping characters, relationships, discoveries, or progression; incidental '
            'travel does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.COUNTRYSIDE,
        label='Countryside',
        definition=(
            'Rural or sparsely populated life is a substantial recurring setting, and its environment, community, '
            'isolation, or way of life meaningfully shapes the story; brief visits to rural places do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.DISABILITY,
        label='Disability',
        definition=(
            "A major character's physical, sensory, cognitive, developmental, or other disability substantially "
            'shapes their experiences, relationships, identity, accessibility, or circumstances; a temporary injury '
            'or incidental mention does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.EXPLORATION,
        label='Exploration',
        definition=(
            'Discovering or investigating unfamiliar places, regions, environments, or worlds is a substantial goal or '
            'recurring activity; travel through known places alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.REDEMPTION,
        label='Redemption',
        definition=(
            "A major character's sustained attempt to atone for, repair, or move beyond consequential past wrongdoing "
            'substantially shapes their development or relationships.'
        ),
    ),
    TagDefinition(
        id=Tag.TRAUMA,
        label='Trauma',
        definition=(
            "A major character's lasting psychological or emotional effects from a severely distressing past "
            'experience substantially shape their behavior, relationships, or development.'
        ),
    ),
    TagDefinition(
        id=Tag.SUPERNATURAL_ENCOUNTERS,
        label='Supernatural Encounters',
        definition=(
            'Recurring encounters or relationships with supernatural beings or phenomena substantially shape '
            "otherwise ordinary characters' experiences, relationships, or understanding of their world."
        ),
    ),
    TagDefinition(
        id=Tag.DEATHMATCH,
        label='Deathmatch',
        definition=(
            'Structured combat in which participants are expected or required to fight to the death substantially '
            'shapes the competition or conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.BODY_SHARING,
        label='Body Sharing',
        definition=(
            'Two or more distinct minds, identities, or beings simultaneously inhabit or control the same body, and '
            'their shared embodiment substantially shapes the story or relationships; sequential body-swapping alone '
            'does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CLOSED_SOCIETY,
        label='Closed Society',
        definition=(
            'A community or civilization is substantially separated from the wider world by physical barriers, '
            'restricted movement, deliberate seclusion, or limited knowledge of what exists beyond it.'
        ),
    ),
    TagDefinition(
        id=Tag.EXPERIMENTAL_SUBJECTS,
        label='Experimental Subjects',
        definition=(
            'Characters or sentient beings are subjected to scientific, medical, supernatural, or technological '
            'experimentation that substantially affects their abilities, condition, identity, circumstances, or the '
            'story.'
        ),
    ),
    TagDefinition(
        id=Tag.OUTBREAK,
        label='Outbreak',
        definition=(
            'The widespread emergence or transmission of a disease, infection, parasite, or comparable biological '
            "threat substantially shapes the story, society, or characters' circumstances."
        ),
    ),
    TagDefinition(
        id=Tag.VIGILANTES,
        label='Vigilantes',
        definition=(
            'A character or group takes justice or law enforcement into their own hands outside official legal '
            'authority, and this activity substantially drives the story or recurring conflicts.'
        ),
    ),
    TagDefinition(
        id=Tag.DARK,
        label='Dark',
        definition=(
            'A persistently grim, disturbing, threatening, or emotionally heavy atmosphere substantially characterizes '
            'the story, with suffering, violence, dread, moral bleakness, or similarly harsh subject matter shaping '
            'its overall experience.'
        ),
    ),
    TagDefinition(
        id=Tag.PRECOGNITION,
        label='Precognition',
        definition=(
            "Knowledge or perception of future events substantially influences characters' decisions, conflicts, or "
            'attempts to alter those events.'
        ),
    ),
    TagDefinition(
        id=Tag.SECRET_ORGANIZATION,
        label='Secret Organization',
        definition=(
            'A concealed group with shared goals, membership, or operations substantially drives the story; ordinary '
            'organizations or groups whose secrecy is incidental do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ANDROID,
        label='Android',
        definition=(
            'An artificial being with a humanlike physical form substantially participates in the story as a '
            'character, population, or important element of the setting.'
        ),
    ),
    TagDefinition(
        id=Tag.ARTIFICIAL_INTELLIGENCE,
        label='Artificial Intelligence',
        definition=(
            'Artificially created intelligence capable of autonomous reasoning, learning, decision-making, or '
            'personality substantially shapes the story, characters, or conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.GRANTED_POWER,
        label='Granted Power',
        definition=(
            'A major character receives, borrows, channels, or derives supernatural abilities from a distinct external '
            'being or entity, and that relationship is a substantial part of the power system or story.'
        ),
    ),
    TagDefinition(
        id=Tag.HIDDEN_STRENGTH,
        label='Hidden Strength',
        definition=(
            'A major character initially appears weak, ordinary, inexperienced, or otherwise unimpressive, but '
            'possesses substantial pre-existing strength or abilities that are concealed, forgotten, suppressed, '
            'underestimated, or revealed later.'
        ),
    ),
    TagDefinition(
        id=Tag.TRAINING,
        label='Training',
        definition=(
            'Repeated or sustained practice, instruction, conditioning, or deliberate skill development substantially '
            "contributes to a major character's growth, abilities, or progression."
        ),
    ),
    TagDefinition(
        id=Tag.TRIALS,
        label='Trials',
        definition=(
            'Characters must complete a structured sequence of tests, challenges, or ordeals to qualify, advance, gain '
            'access, or achieve an important objective.'
        ),
    ),
    TagDefinition(
        id=Tag.POWER_SYSTEM,
        label='Power System',
        definition=(
            'Supernatural or extraordinary abilities operate through a defined framework of rules, mechanics, '
            'limitations, categories, costs, or progression that characters substantially learn, use, develop, or '
            'strategize around.'
        ),
    ),
    TagDefinition(
        id=Tag.FORBIDDEN_KNOWLEDGE,
        label='Forbidden Knowledge',
        definition=(
            'Knowledge, ideas, discoveries, texts, or fields of inquiry are prohibited, concealed, suppressed, or '
            'dangerous to pursue, and seeking, preserving, uncovering, or spreading them substantially drives the '
            'story.'
        ),
    ),
    TagDefinition(
        id=Tag.IDEOLOGICAL_CONFLICT,
        label='Ideological Conflict',
        definition=(
            'Sustained conflict between substantially different systems of belief, values, doctrines, or worldviews '
            'meaningfully drives major characters, groups, relationships, or events; ordinary disagreement alone does '
            'not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.GENERATIONAL_STORY,
        label='Generational Story',
        definition=(
            'The narrative spans substantial periods across successive generations, eras, or substantially changing '
            'groups of characters, with persistent characters, relationships, institutions, legacies, or conflicts '
            'connecting those periods.'
        ),
    ),
    TagDefinition(
        id=Tag.LEGACY,
        label='Legacy',
        definition=(
            'The lasting influence of past people, relationships, actions, beliefs, or achievements substantially '
            'shapes later characters, generations, or events.'
        ),
    ),
    TagDefinition(
        id=Tag.MORTALITY,
        label='Mortality',
        definition=(
            'Death, finite lifespan, or the contrast between mortal and long-lived existence is a substantial '
            'recurring thematic concern shaping characters, relationships, or the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.SACRIFICE,
        label='Sacrifice',
        definition=(
            'Characters deliberately surrender their life, safety, freedom, abilities, relationships, or something '
            'else of major value for another person, group, objective, or principle, substantially affecting the '
            'narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.POSSESSION,
        label='Possession',
        definition=(
            "A character's body or mind is inhabited, controlled, or substantially influenced from within by another "
            'consciousness, spirit, entity, or supernatural force.'
        ),
    ),
    TagDefinition(
        id=Tag.CURSE,
        label='Curse',
        definition=(
            'A supernatural affliction, condition, restriction, or misfortune imposed upon a character, group, object, '
            'or place substantially affects the story.'
        ),
    ),
    TagDefinition(
        id=Tag.MENTOR_STUDENT_RELATIONSHIP,
        label='Mentor-Student Relationship',
        definition=(
            'A sustained mentor-student relationship in which a more experienced character substantially guides, '
            'teaches, trains, or develops another character.'
        ),
    ),
    TagDefinition(
        id=Tag.RELIGION,
        label='Religion',
        definition=(
            'Religious beliefs, faith, worship, doctrine, institutions, practices, or conflicts substantially shape '
            'the story, characters, society, or setting.'
        ),
    ),
    TagDefinition(
        id=Tag.MASTER_SERVANT,
        label='Master-Servant',
        definition=(
            'A sustained relationship in which one major character formally serves, obeys, or is bound to another as '
            'a master, lord, owner, summoner, or equivalent authority substantially shapes their interactions or the '
            'story.'
        ),
    ),
    TagDefinition(
        id=Tag.CULT,
        label='Cult',
        definition=(
            'A highly controlling, insular, or devotion-centered group organized around a leader, belief system, '
            'supernatural entity, or doctrine substantially shapes the story; a religious or spiritual group alone '
            'does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.BLOODLINE,
        label='Bloodline',
        definition=(
            "Family lineage, ancestry, inherited status, or descent substantially determines major characters' "
            'identities, abilities, relationships, obligations, or conflicts.'
        ),
    ),
    TagDefinition(
        id=Tag.ARTIFACT,
        label='Artifact',
        definition=(
            'A distinctive object or relic with extraordinary historical, supernatural, technological, or symbolic '
            'significance substantially drives characters, abilities, conflict, or the story.'
        ),
    ),
    TagDefinition(
        id=Tag.CAT_AND_MOUSE,
        label='Cat and Mouse',
        definition=(
            'Two or more opposing characters or groups repeatedly attempt to identify, anticipate, expose, capture, '
            'evade, or outmaneuver one another, with their ongoing strategic pursuit substantially driving the story.'
        ),
    ),
    TagDefinition(
        id=Tag.INVESTIGATION,
        label='Investigation',
        definition=(
            'Systematic efforts to uncover facts, identify causes or perpetrators, solve unexplained events, or reveal '
            'concealed information substantially drive the story.'
        ),
    ),
    TagDefinition(
        id=Tag.MIND_CONTROL,
        label='Mind Control',
        definition=(
            "A character can substantially compel, override, alter, or directly control another person's thoughts, "
            'decisions, actions, or behavior through supernatural, technological, or extraordinary means.'
        ),
    ),
    TagDefinition(
        id=Tag.MILITARY_STRATEGY,
        label='Military Strategy',
        definition=(
            'Planning, tactics, command decisions, logistics, battlefield maneuvering, or strategic decision-making '
            'substantially shapes organized warfare and its outcomes.'
        ),
    ),
    TagDefinition(
        id=Tag.POLITICAL_VIOLENCE,
        label='Political Violence',
        definition=(
            'Organized or deliberate violence against governments, institutions, populations, or public targets is '
            'substantially used to pursue, communicate, or advance political, ideological, revolutionary, or social '
            'objectives.'
        ),
    ),
    TagDefinition(
        id=Tag.DEMONS,
        label='Demons',
        definition=(
            'Beings explicitly characterized as demons, devils, or an equivalent supernatural species substantially '
            'feature as characters, populations, or forces in the story.'
        ),
    ),
    TagDefinition(
        id=Tag.INTERSPECIES_RELATIONSHIP,
        label='Interspecies Relationship',
        definition=(
            'A substantial personal, romantic, familial, or otherwise close relationship develops between characters '
            'belonging to meaningfully different species or kinds of beings, with that difference materially affecting '
            'the relationship or story.'
        ),
    ),
    TagDefinition(
        id=Tag.INTERSPECIES_CONFLICT,
        label='Interspecies Conflict',
        definition=(
            'Sustained social, political, violent, or cultural conflict between distinct species or populations '
            'substantially shapes the story.'
        ),
    ),
    TagDefinition(
        id=Tag.SOCIAL_HIERARCHY,
        label='Social Hierarchy',
        definition=(
            'Formal or informal differences in social rank, class, caste, status, or group standing substantially '
            "shape characters' opportunities, relationships, treatment, or conflicts."
        ),
    ),
    TagDefinition(
        id=Tag.IDENTITY_CONFLICT,
        label='Identity Conflict',
        definition=(
            "A major character's struggle to understand, accept, or reconcile important parts of their identity "
            'substantially drives their choices, relationships, or character arc.'
        ),
    ),
    TagDefinition(
        id=Tag.HUMAN_NONHUMAN_HYBRID,
        label='Human-Nonhuman Hybrid',
        definition=(
            'A major character is substantially both human and nonhuman in biology, nature, or identity; merely using '
            'nonhuman powers or temporarily changing form does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.HUMAN_NONHUMAN_CONFLICT,
        label='Human-Nonhuman Conflict',
        definition=(
            'Sustained conflict between humans and a nonhuman population or force substantially shapes the story; '
            'isolated fights against individual creatures do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.HIDDEN_NONHUMAN_SOCIETY,
        label='Hidden Nonhuman Society',
        definition=(
            'A nonhuman population or community secretly exists within or alongside ordinary human society and this '
            'concealment is a substantial part of the setting or conflict; a concealed individual identity alone does '
            'not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.OUTER_SPACE,
        label='Outer Space',
        definition=(
            'Travel, exploration, settlement, or life beyond Earth in outer space is a substantial setting or '
            'recurring part of the story; brief space scenes or a passing reference do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.TRANSFER_STUDENT,
        label='Transfer Student',
        definition=(
            'A major character enters a school or educational setting as a transfer student, and that arrival or '
            'adjustment substantially shapes the story or relationships; incidental transfers do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CAUGHT_BETWEEN_SIDES,
        label='Caught Between Sides',
        definition=(
            'A major character has meaningful identity, loyalty, relationships, or obligations connecting opposing '
            'sides of a sustained conflict, forcing them to navigate competing allegiances or attachments.'
        ),
    ),
    TagDefinition(
        id=Tag.CRAFTING,
        label='Crafting',
        definition=(
            'Designing, building, inventing, or creating useful objects, equipment, materials, devices, or technology '
            'is a substantial recurring activity or means of progression; incidental construction or one-off '
            'creations do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SCIENCE,
        label='Science',
        definition=(
            'Understanding the world through scientific knowledge, experimentation, research, discovery, or '
            'scientific problem-solving substantially drives the story or a major character.'
        ),
    ),
    TagDefinition(
        id=Tag.PUZZLES,
        label='Puzzles',
        definition=(
            'Solving puzzles, riddles, logic problems, mazes, or similar structured intellectual challenges is a '
            'substantial recurring activity or mechanism of conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.ACADEMIC_COMPETITION,
        label='Academic Competition',
        definition=(
            'Academic performance, examinations, grades, rankings, or knowledge-based contests substantially '
            'structure competition between characters or groups.'
        ),
    ),
    TagDefinition(
        id=Tag.WAR,
        label='War',
        definition=(
            'An ongoing, impending, or consequential past war structures the main conflict or stakes; incidental '
            'historical references and isolated battles do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CHILDHOOD_FRIENDS,
        label='Childhood Friends',
        definition=(
            'A childhood friendship, separation and reunion, or enduring bond formed in childhood is central to '
            'the story; a passing biographical mention does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.BETRAYAL,
        label='Betrayal',
        definition=(
            'A consequential act of disloyalty or broken trust materially drives the conflict, relationships, or '
            'character arcs; minor deception or an incidental betrayal does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.BULLYING,
        label='Bullying',
        definition=(
            'Sustained targeted intimidation, harassment, or social cruelty substantially drives the conflict or '
            'character experience; isolated teasing or a passing mention does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.GRIEF,
        label='Grief',
        definition=(
            'Coping with death or another profound, irreversible loss substantially shapes a major character or '
            'drives the story; a loss mentioned only as background does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CRIME,
        label='Crime',
        definition=(
            'Criminal activity, investigation of criminal acts, or life within a criminal underworld substantially '
            'drives the story; isolated crimes that merely initiate or briefly affect the plot do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.GANGS,
        label='Gangs',
        definition=(
            'Street gangs or delinquent groups whose shared identity and ongoing activities involve street conflict, '
            'territorial control, or group criminality substantially drive the story; ordinary friend groups, '
            'isolated delinquency, or a passing mention of a gang do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.RIVALRY,
        label='Rivalry',
        definition=(
            'A sustained competitive or adversarial relationship between characters meaningfully drives their goals, '
            'development, or conflicts; brief competition or ordinary opposition does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.COMING_OF_AGE,
        label='Coming of Age',
        definition=(
            "A major character's maturation into greater emotional, social, or personal independence is a substantial "
            'part of the story; simply having young protagonists does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.FAMILY,
        label='Family',
        definition=(
            'Bonds or conflicts among relatives, such as parent-child, sibling, or intergenerational relationships, '
            'substantially drive the story; incidental family references and deliberately formed found-family bonds '
            'alone do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.NINJA,
        label='Ninja',
        definition='Ninja or shinobi identity, training, or operations are central to the story.',
    ),
    TagDefinition(
        id=Tag.APOCALYPSE,
        label='Apocalypse',
        definition=(
            'An imminent or unfolding catastrophic event threatens civilization or the world, and preventing, '
            'surviving, '
            'or responding to it drives the narrative; stories set only after the collapse are post-apocalyptic.'
        ),
    ),
    TagDefinition(
        id=Tag.POST_APOCALYPTIC,
        label='Post-Apocalyptic',
        definition='The story takes place after civilization has undergone a major catastrophic collapse.',
    ),
    TagDefinition(
        id=Tag.ENVIRONMENTAL_COLLAPSE,
        label='Environmental Collapse',
        definition=(
            'Severe deterioration of the natural environment, climate, ecosystems, or habitability substantially '
            "shapes society, characters' circumstances, or the central conflict; ordinary environmental concerns "
            'or a world merely recovering after collapse do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.URBAN_SETTING,
        label='Urban Setting',
        definition=(
            'Life in a city or other densely built urban environment substantially shapes the setting, characters, '
            'conflicts, or recurring story; incidental scenes in a city do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CYBERPUNK,
        label='Cyberpunk',
        definition=(
            'Advanced technology, surveillance, augmentation, corporate or institutional power, inequality, '
            'alienation, or human-technology conflict substantially shapes the setting or narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.CULTIVATION,
        label='Cultivation',
        definition=(
            'Characters develop supernatural power through a structured spiritual or martial cultivation system.'
        ),
    ),
    TagDefinition(
        id=Tag.ALIENS,
        label='Aliens',
        definition=(
            'Extraterrestrial beings, civilizations, or contact with life originating beyond the world are a central '
            'source of setting, conflict, or character relationships; ordinary supernatural creatures do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MODERN_KNOWLEDGE,
        label='Modern Knowledge',
        definition=(
            'A character applies knowledge, methods, or technology from a modern society to materially affect a less '
            'developed or otherwise unfamiliar world; merely arriving from another era or world does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.BASKETBALL,
        label='Basketball',
        definition='Basketball competition, training, or team development is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.SOCCER,
        label='Soccer',
        definition='Soccer competition, training, or team development is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.TENNIS,
        label='Tennis',
        definition='Tennis competition, training, or player development is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.BASEBALL,
        label='Baseball',
        definition='Baseball competition, training, or player development is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.VOLLEYBALL,
        label='Volleyball',
        definition='Volleyball competition, training, or player development is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.CYCLING,
        label='Cycling',
        definition='Cycling competition, training, or rider development is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.BADMINTON,
        label='Badminton',
        definition='Badminton competition, training, or player development is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.ARCHERY,
        label='Archery',
        definition='Archery training or organized competition is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.MARKSMANSHIP,
        label='Marksmanship',
        definition=(
            'Firearm aiming, shooting accuracy, or marksmanship training and competition substantially shape a '
            'character or story; incidental gun use does not qualify.'
        ),
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.RUNNING,
        label='Running',
        definition='Running-based training or organized competition is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.AMERICAN_FOOTBALL,
        label='American Football',
        definition='American football training, teams, or organized competition is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.RUGBY,
        label='Rugby',
        definition='Rugby training, teams, or organized competition is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.SWIMMING,
        label='Swimming',
        definition='Swimming competition, training, or athlete development is central to the story.',
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.SOCIAL_DEDUCTION,
        label='Social Deduction',
        definition=(
            'Determining which member or members of an established group are secretly culprits, impostors, traitors, '
            'or enemies through reasoning about their identities, claims, motives, or actions is a major recurring '
            'narrative element.'
        ),
    ),
    TagDefinition(
        id=Tag.REGRESSION,
        label='Regression',
        definition='A character returns to an earlier point in their life with future knowledge and changes events.',
    ),
    TagDefinition(
        id=Tag.TIME_LOOP,
        label='Time Loop',
        definition=(
            'A bounded period repeatedly resets after a trigger, allowing retained knowledge to change later '
            'iterations.'
        ),
    ),
    TagDefinition(
        id=Tag.TIME_LEAP,
        label='Time Leap',
        definition=(
            "Deliberately traveling or transferring oneself or one's consciousness between distinct points in time is "
            'a substantial recurring narrative mechanism, without requiring a repeating reset cycle or a persistent '
            'restart from an earlier life stage.'
        ),
    ),
    TagDefinition(
        id=Tag.GAMBLING,
        label='Gambling',
        definition='High-stakes gambling or wagering games drive the central conflict and strategic progression.',
    ),
    TagDefinition(
        id=Tag.REVENGE,
        label='Revenge',
        definition="A desire for retribution is the protagonist's central motivation and drives the narrative.",
    ),
    TagDefinition(
        id=Tag.LEVELING,
        label='Leveling',
        definition=(
            'Explicit levels, stats, ranks, experience, or comparable quantified progression are a central mechanism '
            'of character advancement.'
        ),
    ),
    TagDefinition(
        id=Tag.DUNGEON,
        label='Dungeon',
        definition=(
            'Exploring, clearing, surviving, or repeatedly operating within dungeon-like environments is a major '
            'recurring element.'
        ),
    ),
    TagDefinition(
        id=Tag.POLITICAL,
        label='Political',
        definition=(
            'Political power, governance, diplomacy, succession, or factional maneuvering substantially drives the '
            'narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.KINGDOM_BUILDING,
        label='Kingdom Building',
        definition=(
            'Establishing, expanding, governing, or developing a kingdom or polity is a substantial recurring part of '
            'the narrative; ordinary political intrigue without state-building does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ASSASSIN,
        label='Assassin',
        definition='Assassination, professional killers, or assassin training is a major recurring story element.',
    ),
    TagDefinition(
        id=Tag.CREATURE_TAMING,
        label='Creature Taming',
        definition=(
            'Collecting, raising, training, or forming structured partnerships with creatures that accompany or fight '
            'alongside characters is central to the story.'
        ),
    ),
    TagDefinition(
        id=Tag.ABILITY_BATTLES,
        label='Ability Battles',
        definition=(
            'Combat substantially revolves around distinct character-specific abilities whose explicit rules, '
            'constraints, counters, or strategic interactions materially determine fights, distinct from generic '
            'raw-power or martial-arts clashes.'
        ),
    ),
    TagDefinition(
        id=Tag.HEIST,
        label='Heist',
        definition=(
            'Planning and executing elaborate schemes to steal, acquire, or recover valuable targets through '
            'deception, '
            'infiltration, or coordinated operations is central to the story.'
        ),
    ),
    TagDefinition(
        id=Tag.TREASURE_HUNTING,
        label='Treasure Hunting',
        definition=(
            'Searching for and competing to locate hidden treasure or valuable objects through clues, maps, or '
            'exploration is central to the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.PIRATES,
        label='Pirates',
        definition='Pirate crews, piracy, or a pirate identity and way of life are central to the story.',
    ),
    TagDefinition(
        id=Tag.CARD_BATTLING,
        label='Card Battling',
        definition=(
            'Competitive card battles, using decks of combatants, abilities, or resources to defeat opponents under '
            'a structured game ruleset, are central to the story.'
        ),
    ),
    TagDefinition(
        id=Tag.PSYCHIC,
        label='Psychic',
        definition=(
            'Psychic or extrasensory abilities such as telekinesis, telepathy, or clairvoyance are central to major '
            'characters or the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.MEMORY_LOSS,
        label='Memory Loss',
        definition=(
            "Loss, suppression, or inability to retain significant memories substantially shapes a major character's "
            'identity, relationships, motivations, or the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.EXORCISM,
        label='Exorcism',
        definition=(
            'Exorcising, purifying, sealing, dispelling, or otherwise spiritually removing supernatural entities or '
            'corruption is a central activity or conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.SUPERHERO,
        label='Superhero',
        definition=(
            'Superheroes, supervillains, or a superhero-style society or ecosystem of extraordinary identities, public '
            'or criminal personas, and organized hero-villain conflict substantially structure the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.ESPIONAGE,
        label='Espionage',
        definition=(
            'Intelligence gathering, infiltration, covert operations, or maintaining undercover identities for '
            'intelligence purposes is central to the story.'
        ),
    ),
    TagDefinition(
        id=Tag.SPY,
        label='Spy',
        definition=(
            'A spy or espionage agent is a central character, and their covert intelligence work, cover identity, or '
            'double life substantially drives the story.'
        ),
    ),
    TagDefinition(
        id=Tag.TRANSFORMATION,
        label='Transformation',
        definition=(
            'Assuming a distinct empowered identity or alternate bodily form through an explicit transformation '
            'mechanism is central to the story, without the transformation representing acquisition of a fundamentally '
            'monstrous or non-human nature.'
        ),
    ),
    TagDefinition(
        id=Tag.REBELLION,
        label='Rebellion',
        definition=(
            'Organized resistance or uprising against an established government, occupying power, or ruling authority '
            'is central to the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.SYSTEM,
        label='System',
        definition=(
            'A major character interacts with an explicit game-like framework exposing stats, skills, levels, quests, '
            'classes, inventories, achievements, or similar structured rules.'
        ),
    ),
    TagDefinition(
        id=Tag.VIRTUAL_REALITY,
        label='Virtual Reality',
        definition="Immersive virtual or simulated reality is a central setting and source of the story's conflicts.",
    ),
    TagDefinition(
        id=Tag.AUGMENTED_REALITY,
        label='Augmented Reality',
        definition=(
            'Technology overlays interactive digital content onto the physical world and is central to the story.'
        ),
    ),
    TagDefinition(
        id=Tag.ESPORTS,
        label='Esports',
        definition=(
            'Organized competitive video gaming, professional players, teams, leagues, or tournaments are central to '
            'the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.FOUND_FAMILY,
        label='Found Family',
        definition=(
            'A central, enduring group of otherwise unrelated characters develops a family-like bond through shared '
            'experiences, mutual care, and commitment.'
        ),
    ),
    TagDefinition(
        id=Tag.MAHJONG,
        label='Mahjong',
        definition=(
            "Playing or competing in mahjong is a central recurring activity driving the narrative or characters' "
            'goals.'
        ),
    ),
    TagDefinition(
        id=Tag.SHOGI,
        label='Shogi',
        definition=(
            "Playing or competing in shogi is a central recurring activity driving the narrative or characters' goals."
        ),
    ),
    TagDefinition(
        id=Tag.GO,
        label='Go',
        definition=(
            "Playing or competing in Go is a central recurring activity driving the narrative or characters' goals."
        ),
    ),
    TagDefinition(
        id=Tag.ADVENTURING_PARTY,
        label='Adventuring Party',
        definition=(
            'A persistent group of characters who adventure together as a coordinated party substantially structures '
            "the narrative's exploration, quests, combat, or progression."
        ),
    ),
    TagDefinition(
        id=Tag.CONSPIRACY,
        label='Conspiracy',
        definition=(
            'A hidden coordinated plan by powerful individuals or organizations substantially drives the narrative, '
            'conflict, or investigation.'
        ),
    ),
    TagDefinition(
        id=Tag.BOXING,
        label='Boxing',
        definition=(
            'Competitive boxing matches, training, or ring competition substantially structure the narrative and '
            'character development.'
        ),
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.TABLE_TENNIS,
        label='Table Tennis',
        definition=(
            'Competitive table tennis (ping pong) matches, club activities, or tournaments are central to the story.'
        ),
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.FIGURE_SKATING,
        label='Figure Skating',
        definition=(
            'Competitive or exhibition figure skating routines, choreography, and ice rink training substantially '
            'drive the narrative.'
        ),
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.BATTLE_ROYALE,
        label='Battle Royale',
        definition=(
            'An explicit, rule-bound elimination contest where participants are forced or incentivized to eliminate '
            'or kill one another until a single victor or surviving group remains.'
        ),
    ),
    TagDefinition(
        id=Tag.DEATH_GAME,
        label='Death Game',
        definition=(
            'Characters participate in a rule-bound game, contest, or series of trials in which death is an intended '
            'or substantial consequence of losing, failing, or violating the rules.'
        ),
    ),
    TagDefinition(
        id=Tag.BOUNTY_HUNTER,
        label='Bounty Hunter',
        definition=(
            'Tracking, apprehending, or claiming rewards on criminal bounties or fugitives serves as a primary '
            'profession and episodic plot driver for central characters.'
        ),
    ),
    TagDefinition(
        id=Tag.MERCENARY,
        label='Mercenary',
        definition=(
            'A major character or group performs armed combat or dangerous security work for payment outside regular '
            'state military service, and this work substantially shapes the story; military service or bounty hunting '
            'alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.YOKAI,
        label='Yokai',
        definition=(
            'Yōkai, ayakashi, or closely equivalent Japanese folkloric supernatural beings substantially drive the '
            'setting, characters, or narrative, distinct from generic western spirits or abstract deities.'
        ),
    ),
    TagDefinition(
        id=Tag.STEAMPUNK,
        label='Steampunk',
        definition=(
            'Steam-powered machinery, clockwork engineering, or retro-futuristic Victorian industrial technology '
            "fundamentally defines the fictional world's infrastructure, vehicles, or weapons."
        ),
    ),
    TagDefinition(
        id=Tag.VICTORIAN,
        label='Victorian',
        definition=(
            'The story is substantially set in or modeled on Victorian-era society, with its period culture, '
            'institutions, technology, or social conditions meaningfully shaping the setting or narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.BODY_SWAP,
        label='Body Swap',
        definition=(
            'Two or more characters swap physical bodies, or exchange consciousnesses between bodies, as a central '
            'recurring narrative device or primary source of interpersonal conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.GOLF,
        label='Golf',
        definition=('Competitive or recreational golf serves as the primary athletic focus and narrative driver.'),
    ),
    TagDefinition(
        id=Tag.RAKUGO,
        label='Rakugo',
        definition=(
            'Traditional Japanese rakugo (solo comedic or dramatic monologue storytelling) serves as a central '
            'discipline, career path, or focal art form for primary characters.'
        ),
    ),
    TagDefinition(
        id=Tag.PRISON_SETTING,
        label='Prison Setting',
        definition=(
            'A prison, penal institution, detention facility, or equivalent carceral environment serves as a primary '
            'recurring setting and materially structures the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.CAPTIVITY,
        label='Captivity',
        definition=(
            'A major character or group is involuntarily confined, imprisoned, detained, held hostage, or otherwise '
            'prevented from freely leaving by an outside person, group, or system, and that condition or efforts to '
            'end it substantially shape the story; brief capture or ordinary isolation does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.AVIATION,
        label='Aviation',
        definition=(
            'Piloting, designing, operating, or pursuing atmospheric aviation substantially drives the narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.ASTRONAUT,
        label='Astronaut',
        definition=(
            'Astronaut training, professional space operations, or crewed spaceflight substantially drives the '
            'narrative.'
        ),
    ),
    TagDefinition(
        id=Tag.FAKE_RELATIONSHIP,
        label='Fake Relationship',
        definition=(
            'Two or more characters enter into an explicit mutual agreement or deception to pretend to be romantic '
            'partners or a married couple to third parties.'
        ),
    ),
    TagDefinition(
        id=Tag.JUDO,
        label='Judo',
        definition=('Competitive or traditional judo serves as the primary athletic focus and narrative driver.'),
    ),
    TagDefinition(
        id=Tag.KENDO,
        label='Kendo',
        definition=('Competitive or traditional kendo serves as the primary athletic focus and narrative driver.'),
    ),
    TagDefinition(
        id=Tag.ALCHEMY,
        label='Alchemy',
        definition=(
            'Transmutation, chemical or material synthesis, potion brewing, or pseudo-scientific matter conversion '
            'serves as a central discipline and narrative mechanic.'
        ),
    ),
    TagDefinition(
        id=Tag.MUSICAL_BAND,
        label='Musical Band',
        definition=(
            'Forming, practicing, and performing in a collaborative contemporary musical band (such as a rock, indie, '
            'pop, metal, or concert/brass ensemble) is the central structural engine of the plot and character '
            'development.'
        ),
    ),
    TagDefinition(
        id=Tag.LEGAL,
        label='Legal',
        definition=(
            'Formal judicial proceedings, courtroom trials, legal debates, or defense attorney and prosecutor casework '
            'materially structure the investigation and narrative resolution.'
        ),
    ),
    TagDefinition(
        id=Tag.LAWYERS,
        label='Lawyers',
        definition=(
            'Lawyers or attorneys are central characters, and their legal practice, cases, or professional '
            'relationships '
            'substantially drive the story; a legal dispute without lawyer characters as a focus does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.WORK_LIFE,
        label='Work Life',
        definition=(
            "Characters' recurring workplace routines, professional responsibilities, and coworker relationships "
            'substantially shape the story; a job used only as background does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CAREER_AMBITION,
        label='Career Ambition',
        definition=(
            "A major character's sustained pursuit of a chosen vocation or professional achievement substantially "
            'drives their goals, development, or the narrative; a job or passing aspiration mentioned only as '
            'background does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.AFTERLIFE,
        label='Afterlife',
        definition=(
            'An afterlife, limbo, purgatory, or underworld realm serves as a central ongoing setting and '
            'substantially structures character goals, judgments, or transitions.'
        ),
    ),
    TagDefinition(
        id=Tag.SPIRIT_WORLD,
        label='Spirit World',
        definition=(
            'A distinct realm or plane primarily associated with souls, spirits, or other incorporeal beings '
            'substantially shapes the setting, travel, characters, or conflict; a story merely set after death does '
            'not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MELANCHOLIC,
        label='Melancholic',
        definition=(
            'A persistent atmosphere of quiet sorrow, loneliness, impermanence, or bittersweet yearning '
            '(mono no aware) consistently permeates the aesthetic, character reflections, and narrative tone.'
        ),
    ),
    TagDefinition(
        id=Tag.BLEAK,
        label='Bleak',
        definition=(
            'An oppressive, unforgiving world where moral compromise is mandatory, triumph is Pyrrhic or fleeting, '
            'and suffering, brutality, or fatalism fundamentally structures the narrative environment.'
        ),
    ),
    TagDefinition(
        id=Tag.NOIR,
        label='Noir',
        definition=(
            'A crime-centered story shaped by moral ambiguity, compromised characters, corruption, and fatalistic '
            'atmosphere; crime alone or a generally bleak tone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.LIFESTYLE_CHANGE,
        label='Lifestyle Change',
        definition=(
            'A character undergoes a substantial and sustained change to their everyday way of living, routines, '
            'social environment, responsibilities, or living circumstances, and adapting to that new life is a '
            'meaningful part of the story.'
        ),
    ),
    TagDefinition(
        id=Tag.GODS,
        label='Gods',
        definition=(
            "Gods or godlike divine beings are central characters or a substantial source of the story's setting, "
            'conflict, or mythology; incidental worship or religious references do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ROYALTY,
        label='Royalty',
        definition=(
            'A royal identity, succession, court position, or duties of a monarch or royal family substantially shape '
            'the characters or story; incidental royal titles or appearances do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SWORDSMANSHIP,
        label='Swordsmanship',
        definition=(
            'Sword-based combat, fighting technique, training, or mastery is a substantial recurring element of the '
            'story or its major characters; incidental or occasional sword use does not qualify.'
        ),
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.BODYGUARDS,
        label='Bodyguards',
        definition=(
            'Protecting a specific person through a bodyguard or close-protection role is a central character duty, '
            'relationship, or recurring source of conflict; general security work or incidental protection does not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MEDIEVAL,
        label='Medieval',
        definition=(
            'A medieval-era or medieval-inspired society, including its institutions, technology, and social '
            'structures, is central to the setting or story; castles or medieval aesthetics alone do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.PERSON_IN_A_STRANGE_WORLD,
        label='Person in a Strange World',
        definition=(
            'A major character must navigate an unfamiliar world, society, culture, or environment substantially '
            'different from what they know.'
        ),
    ),
    TagDefinition(
        id=Tag.GENIUS_PROTAGONIST,
        label='Genius Protagonist',
        definition=(
            "The protagonist's exceptional intelligence, knowledge, technical expertise, or problem-solving ability "
            'is a defining trait and substantially drives the story; ordinary intelligence or competence does not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.STRATEGIC_PROTAGONIST,
        label='Strategic Protagonist',
        definition=(
            'The protagonist characteristically overcomes major conflicts through planning, tactics, manipulation, '
            'deception, or anticipating opponents; occasional cleverness does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MIND_GAMES,
        label='Mind Games',
        definition=(
            'Psychological contests of deception, deduction, manipulation, or strategic outthinking between opposing '
            'characters are a central recurring structure of the conflict; isolated clever schemes do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CHILD_PROTAGONIST,
        label='Child Protagonist',
        definition=(
            'A child is the protagonist or a central viewpoint character, and their young age meaningfully shapes '
            'the story, relationships, or challenges; incidental child characters do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ADULT_PROTAGONIST,
        label='Adult Protagonist',
        definition=(
            'An adult is the protagonist or a central viewpoint character, and adult responsibilities or life '
            'experience meaningfully shape the story, relationships, or challenges; incidental adult characters '
            'do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MALE_PROTAGONIST,
        label='Male Protagonist',
        definition=(
            'One or more principal protagonists are explicitly identified as male; do not infer gender from names, '
            'appearance, or voice alone.'
        ),
    ),
    TagDefinition(
        id=Tag.FEMALE_PROTAGONIST,
        label='Female Protagonist',
        definition=(
            'One or more principal protagonists are explicitly identified as female; do not infer gender from names, '
            'appearance, or voice alone.'
        ),
    ),
    TagDefinition(
        id=Tag.NON_HUMAN_PROTAGONIST,
        label='Non-Human Protagonist',
        definition=(
            'The protagonist is inherently non-human or belongs to a non-human species, and that nature is central '
            'to the premise or character perspective; a human who only later transforms is covered by other tags.'
        ),
    ),
    TagDefinition(
        id=Tag.ENSEMBLE_CAST,
        label='Ensemble Cast',
        definition=(
            'The story distributes substantial narrative focus across multiple co-protagonists or comparably central '
            'characters, rather than primarily following one lead with supporting characters.'
        ),
    ),
    TagDefinition(
        id=Tag.WHIMSICAL,
        label='Whimsical',
        definition=(
            'A dreamlike, offbeat, or fairytale-like atmosphere where eccentric logic, magical realism, or playful '
            'absurdity governs the world rather than grounded or hard-magic rules.'
        ),
    ),
    TagDefinition(
        id=Tag.PHILOSOPHICAL,
        label='Philosophical',
        definition=(
            'Abstract inquiries into epistemology, metaphysics, ethics, free will, the nature of consciousness, '
            'or human existence directly structure the central narrative conflicts and character reflections.'
        ),
    ),
    TagDefinition(
        id=Tag.THRILLER,
        label='Thriller',
        definition=(
            'Sustained suspense, uncertainty, escalating danger, and anticipation drive the story experience; '
            'incidental '
            'suspense or danger alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.AGRICULTURE,
        label='Agriculture / Farming',
        definition=(
            'Farming, crop cultivation, animal husbandry, or agricultural community life is a sustained setting or '
            'activity; incidental gardens, food, or rural scenery do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.BILLIARDS,
        label='Billiards',
        definition=(
            'Playing or competing in cue sports such as pool or carom billiards is a central recurring activity.'
        ),
    ),
    TagDefinition(
        id=Tag.COOKING,
        label='Cooking',
        definition=(
            'Preparing food through cooking technique, practice, or competition is a sustained central activity; '
            'cooking competitions qualify, while eating or food appreciation alone does not.'
        ),
    ),
    TagDefinition(
        id=Tag.COOKING_COMPETITION,
        label='Cooking Competition',
        definition=(
            'Organized cooking contests, judged rounds, or rival chefs competing are central recurring story '
            'structures; ordinary cooking without competition does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.BAKING,
        label='Baking',
        definition=(
            'Baking breads, pastries, cakes, or other baked goods is a central sustained activity, craft, or '
            'competition; incidental baking does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.RESTAURANT_CAFE,
        label='Restaurant / Cafe',
        definition=(
            'A restaurant, cafe, diner, food stall, or similar eating or drinking establishment is a sustained '
            'primary setting, and its work, ownership, or community life shapes the story; incidental visits do not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.GYMNASTICS,
        label='Gymnastics',
        definition=(
            'Gymnastics training, routines, competition, or performance substantially drives the story or character '
            'development.'
        ),
    ),
    TagDefinition(
        id=Tag.HOCKEY,
        label='Hockey',
        definition=('Organized hockey play, training, competition, or team life is a sustained focus of the story.'),
    ),
    TagDefinition(
        id=Tag.ICE_SKATING,
        label='Ice Skating',
        definition=(
            'Ice skating practice or performance substantially structures the story, apart from '
            'figure-skating-specific '
            'competition and choreography.'
        ),
    ),
    TagDefinition(
        id=Tag.MOUNTAINEERING,
        label='Mountaineering',
        definition=(
            'Climbing mountains or undertaking sustained alpine expeditions is a central activity or narrative goal.'
        ),
    ),
    TagDefinition(
        id=Tag.SCUBA_DIVING,
        label='Scuba Diving',
        definition=(
            'Underwater diving with breathing equipment, including training, exploration, or dive operations, is a '
            'sustained narrative activity.'
        ),
    ),
    TagDefinition(
        id=Tag.SKATEBOARDING,
        label='Skateboarding',
        definition=(
            'Skateboarding practice, tricks, competition, or skateboarding culture substantially drives the story.'
        ),
    ),
    TagDefinition(
        id=Tag.SKIING,
        label='Skiing',
        definition=('Skiing practice, competition, instruction, or ski-area life is a sustained focus of the story.'),
    ),
    TagDefinition(
        id=Tag.SUMO,
        label='Sumo',
        definition=(
            'Sumo training, stable life, tournaments, or professional competition substantially drives the story.'
        ),
    ),
    TagDefinition(
        id=Tag.SURFING,
        label='Surfing',
        definition=('Surfing practice, competition, or surf-community life is a sustained focus of the story.'),
    ),
    TagDefinition(
        id=Tag.TRACK_AND_FIELD,
        label='Track and Field',
        definition=(
            'Track-and-field training or competition, such as running, jumping, or throwing events, is a sustained '
            'focus of the story.'
        ),
    ),
    TagDefinition(
        id=Tag.WATER_POLO,
        label='Water Polo',
        definition=(
            'Water polo training, team play, or competition substantially structures the story or character '
            'development.'
        ),
    ),
    TagDefinition(
        id=Tag.WRESTLING,
        label='Wrestling',
        definition=(
            'Wrestling training, bouts, competition, or professional wrestling performance is a sustained focus of the '
            'story.'
        ),
    ),
    TagDefinition(
        id=Tag.WEIGHTLIFTING,
        label='Weightlifting',
        definition=(
            'Weightlifting training or competition, including strength development and lifting events, substantially '
            'drives the story; incidental strength training does not qualify.'
        ),
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.REVERSE_ISEKAI,
        label='Reverse Isekai',
        definition=(
            'A character or group from another world enters and adapts to an otherwise ordinary or modern world, and '
            'that cross-world displacement is a sustained premise or conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.TRANSMIGRATION,
        label='Transmigration',
        definition=(
            "A person's consciousness or soul transfers into another body or life, and navigating that new identity "
            'or status is a central recurring premise; ordinary reincarnation without this transfer dynamic does not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.TRANSPORTED_INTO_FICTION,
        label='Transported into Fiction',
        definition=(
            'A character is transported, reincarnated, transmigrated, or otherwise placed into the world of a novel, '
            'book, story, comic, or other fictional work that they or the narrative recognize as fiction.'
        ),
    ),
    TagDefinition(
        id=Tag.EPISODIC,
        label='Episodic',
        definition=(
            'The story is predominantly structured as self-contained episodes or installments, each resolving its '
            'own main situation while contributing to any broader continuity.'
        ),
    ),
    TagDefinition(
        id=Tag.ANTHOLOGY,
        label='Anthology',
        definition=(
            'A collection of independent or loosely connected short stories, vignettes, or standalone works by '
            'different or single creators, rather than a continuous narrative arc.'
        ),
    ),
    TagDefinition(
        id=Tag.SERIALIZED,
        label='Serialized',
        definition=(
            'The story is predominantly structured around a continuous narrative that develops across multiple '
            'episodes or installments, with later parts relying on events or character development established earlier.'
        ),
    ),
    TagDefinition(
        id=Tag.PROCEDURAL,
        label='Procedural',
        definition=(
            'A recurring process such as investigations, cases, missions, or systematic problem-solving drives the '
            'story, with the process itself central beyond any single case or outcome.'
        ),
    ),
    TagDefinition(
        id=Tag.OCCULT,
        label='Occult',
        definition=(
            'Esoteric rites, hidden supernatural practices, or occult investigation substantially drive the story; '
            'generic supernatural beings or ordinary magic alone do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.TOWER_CLIMBING,
        label='Tower Climbing',
        definition=(
            'Ascending a structured tower through floors, trials, or staged challenges is a central objective or '
            'recurring progression mechanic.'
        ),
    ),
    TagDefinition(
        id=Tag.DANCING,
        label='Dancing',
        definition=(
            'Dance practice, choreography, performance, or competition is a sustained focus of the story; incidental '
            'dancing or music performance alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CALLIGRAPHY,
        label='Calligraphy',
        definition=(
            'Calligraphy practice, artistic development, teaching, or competition substantially drives the story or '
            'character development.'
        ),
    ),
    TagDefinition(
        id=Tag.CAMPING,
        label='Camping',
        definition=(
            'Camping, camp life, or recurring outdoor overnight trips are a central setting or activity; a single '
            'incidental camping scene does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.FENCING,
        label='Fencing',
        definition=(
            'Fencing training, bouts, club life, or competition substantially structures the story or character '
            'development.'
        ),
    ),
    TagDefinition(
        id=Tag.HIDDEN_IDENTITY,
        label='Secret Identity',
        definition=(
            'A character deliberately conceals a consequential alternate identity, role, or affiliation, and '
            'maintaining or exposing that secret is a recurring source of conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.WEAK_TO_STRONG,
        label='Weak to Strong',
        definition=(
            'A protagonist or central group begins notably disadvantaged in capability or status and undergoes '
            'sustained development into greater strength, competence, or influence.'
        ),
    ),
    TagDefinition(
        id=Tag.OVERPOWERED_PROTAGONIST,
        label='Overpowered Protagonist',
        definition=(
            'The protagonist begins with or quickly gains overwhelming capability relative to most opponents, and '
            "that power imbalance shapes recurring conflicts or the story's appeal."
        ),
    ),
    TagDefinition(
        id=Tag.DYSTOPIAN,
        label='Dystopian',
        definition=(
            'An oppressive or severely dysfunctional society, often shaped by authoritarian control, systemic '
            'inequality, or degraded living conditions, is central to the setting and conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.UTOPIAN,
        label='Utopian',
        definition=(
            'An idealized society organized around unusually harmonious, just, or flourishing conditions is central '
            'to the setting or narrative, including stories that examine the costs or fragility of that ideal.'
        ),
    ),
    TagDefinition(
        id=Tag.FIREFIGHTER,
        label='Firefighter',
        definition=(
            'Firefighting, fire-rescue operations, or the professional or volunteer life of firefighters substantially '
            'drives the story; incidental fires or rescue scenes do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MERCHANT,
        label='Merchant',
        definition=(
            'A central character earns a living or pursues major goals through buying, selling, trading, or running a '
            'business, and commerce meaningfully shapes recurring plots or relationships.'
        ),
    ),
    TagDefinition(
        id=Tag.MURDER_MYSTERY,
        label='Murder Mystery',
        definition=(
            'Solving or investigating a homicide is a central mystery, with clues, suspects, or revelations driving '
            'the investigation; incidental murders in a broader crime or action story do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SERIAL_KILLER,
        label='Serial Killer',
        definition=(
            'A serial killer or a series of related murders committed across separate incidents is a central recurring '
            'character, threat, or conflict; multiple unrelated or incidental murders do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.UNDERCOVER,
        label='Undercover',
        definition=(
            'A character conceals their real allegiance or purpose while embedded in another group or organization, '
            'and maintaining their cover or advancing the covert mission drives recurring conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.ALTERNATE_HISTORY,
        label='Alternate History',
        definition=(
            'A major counterfactual divergence from real history produces a changed historical timeline or world '
            'state central to the setting or plot; Historical plus Fantasy alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ANTIHERO,
        label='Antihero',
        definition=(
            'The narrative protagonist lacks conventional heroic morality or methods while still functioning as the '
            'central protagonist, and this tension meaningfully shapes their goals, relationships, or character arc.'
        ),
    ),
    TagDefinition(
        id=Tag.ACADEMY,
        label='Academy',
        definition=(
            'An institution specifically dedicated to specialized training (such as magic, hero work, military, '
            'mecha, or martial arts) is central to the story through instruction, evaluation, or cohort life; an '
            'ordinary school setting alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SCHOOL_CLUB,
        label='School Club',
        definition=(
            'Participation in a school club, its activities, membership, or internal goals substantially drives '
            'the story; a club mentioned only as background does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.PROPHECY,
        label='Prophecy',
        definition=(
            'A prophecy or foretelling materially drives characters, conflict, or plot through its interpretation, '
            'fulfillment, prevention, or resistance; incidental references to fate do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SEALED_POWER,
        label='Sealed Power',
        definition=(
            "A character's significant abilities or supernatural power are deliberately sealed, suppressed, or "
            'locked away, and the restriction or its release materially shapes recurring conflict or progression.'
        ),
    ),
    TagDefinition(
        id=Tag.SUMMONING,
        label='Summoning',
        definition=(
            'Calling a supernatural being, spirit, creature, or entity into presence through magic or another '
            'deliberate mechanism is a recurring or central power; transport of people into another world alone is '
            'covered by Summoned to Another World.'
        ),
    ),
    TagDefinition(
        id=Tag.CONTRACT,
        label='Contract',
        definition=(
            'A character enters a consequential agreement with a supernatural or nonhuman being, exchanging service, '
            'power, access, protection, a wish, a familiar bond, or another benefit under meaningful terms or '
            'obligations. The agreement may involve a pact, curse, blessing, ritual, divine bargain, or sacrifice as '
            'its terms or price; these are facets of the contract rather than separate tags.'
        ),
    ),
    TagDefinition(
        id=Tag.SUMMONED_TO_ANOTHER_WORLD,
        label='Summoned to Another World',
        definition=(
            'A person or group is deliberately called from their world into a distinct other world by magic, ritual, '
            'or another summoning mechanism, and that displacement is central to the premise or plot.'
        ),
    ),
    TagDefinition(
        id=Tag.TRAPPED_IN_GAME,
        label='Trapped in a Game',
        definition=(
            'Characters become unable to leave an active video game or game-like virtual environment, and escape or '
            'survival within it is a central ongoing conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.GAME_WORLD_BECOMES_REALITY,
        label='Game World Becomes Reality',
        definition=(
            'Rules, entities, or progression systems from a game manifest in or transform the ordinary real world, '
            'and this incursion is central to the story; merely entering a virtual game does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.WORLD_HOPPING,
        label='World Hopping',
        definition=(
            'Characters repeatedly travel between distinct worlds or realities, with movement between them serving as '
            'a recurring story structure rather than a one-time displacement.'
        ),
    ),
    TagDefinition(
        id=Tag.FINANCIAL_HARDSHIP,
        label='Financial Hardship',
        definition=(
            "Poverty, debt, or difficulty meeting basic material needs substantially drives characters' choices, "
            'relationships, or conflicts; incidental money troubles or differences in social rank alone do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.NATURAL_DISASTER,
        label='Natural Disaster',
        definition=(
            'A natural disaster such as an earthquake, tsunami, flood, or volcanic eruption, or its aftermath, '
            'substantially drives the story; civilization-wide collapse is not required, and an incidental disaster '
            'mentioned only as background does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ARRANGED_MARRIAGE,
        label='Arranged Marriage',
        definition=(
            'A marriage selected, negotiated, or imposed by family members or other outside parties substantially '
            'shapes a central relationship or conflict, whether the prospective spouses consent or are coerced; '
            'pretending to be a couple alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.COHABITATION,
        label='Cohabitation',
        definition=(
            'Sharing a home and adjusting to life together substantially shapes central relationships or conflicts; '
            'incidental roommates or relatives merely residing in the same home do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SERIOUS_ILLNESS,
        label='Serious Illness',
        definition=(
            "Living with a serious, chronic, or terminal illness substantially shapes a major character's life, "
            'relationships, or choices; medical work, a temporary injury, or mortality in general alone does not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MARRIED_LIFE,
        label='Married Life',
        definition=(
            'The ongoing relationship, shared routines, or responsibilities of spouses are a central premise or '
            'sustained focus; a wedding, engagement, or marriage mentioned only as background does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.FISHING,
        label='Fishing',
        definition=(
            'Fishing as a sustained activity, livelihood, learning process, or competition is central to the story; '
            'an incidental catch or fishing trip does not qualify.'
        ),
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.KARUTA,
        label='Karuta',
        definition=(
            'Karuta play, training, competition, or player development is central to the story, involving recognition '
            'of recited poems or phrases and rapid retrieval of the corresponding cards.'
        ),
        standalone_qualification=True,
    ),
    TagDefinition(
        id=Tag.MEMORY_MANIPULATION,
        label='Memory Manipulation',
        definition=(
            'Deliberately altering, erasing, implanting, storing, or transferring memories through supernatural, '
            'technological, or extraordinary means substantially shapes identities, relationships, or conflicts; '
            'ordinary forgetting or memory loss without such intervention does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CLASSICAL_MUSIC,
        label='Classical Music',
        definition=(
            'Classical music study, composition, rehearsal, performance, or competition is a sustained central '
            'activity shaping character development or the narrative; incidental background music or a briefly '
            'mentioned musical interest does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.CYBERNETICS,
        label='Cybernetics',
        definition=(
            'Cybernetic implants, prostheses, artificial body systems, or integration between biological beings '
            'and machinery substantially shape characters, abilities, identity, or society.'
        ),
    ),
    TagDefinition(
        id=Tag.MEDIA_PRODUCTION,
        label='Media Production',
        definition=(
            'Creating, producing, publishing, or professionally developing media such as animation, manga/comics, '
            "film, television, video games, or recorded music substantially drives the narrative, characters' work, "
            'or ambitions.'
        ),
    ),
    TagDefinition(
        id=Tag.FRIENDSHIP,
        label='Friendship',
        definition=(
            'Forming, maintaining, testing, or changing enduring peer friendships is a sustained central relationship '
            'focus or source of character development; incidental friends, romantic attraction alone, or cooperating '
            'in a single mission do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.COMMUNITY_LIFE,
        label='Community Life',
        definition=(
            'An ongoing network of local residents, neighbors, or community members, and their shared customs, '
            'support, involvement, or tensions, substantially structures the story; a town as scenery, an incidental '
            'crowd, or one family alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.PARALLEL_WORLDS,
        label='Parallel Worlds',
        definition=(
            'Coexisting alternate versions of a world, timeline, or its inhabitants, and their correspondence, '
            'interaction, or consequences, substantially structure the narrative; a single unrelated fantasy '
            'destination, counterfactual historical setting alone, or a repeating time reset does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.DREAM_WORLDS,
        label='Dream Worlds',
        definition=(
            'Dreams, sleeping minds, or a shared dream realm function as experienced narrative spaces whose '
            'inhabitants, access, rules, or interaction with waking reality substantially drive the story; '
            'aspirations, ordinary nightmares, dreamlike aesthetics, or travel during sleep to an independently '
            'real world alone do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.RECONCILIATION,
        label='Reconciliation',
        definition=(
            'Repairing a substantially damaged or estranged interpersonal relationship is a significant narrative '
            'focus.'
        ),
    ),
    TagDefinition(
        id=Tag.DRAGONS,
        label='Dragons',
        definition=(
            'Dragons are a major species, character type, subject, or persistent element of the work; a brief dragon '
            'encounter, boss, title or name reference, or a work such as Dragon Ball does not qualify by itself.'
        ),
    ),
    TagDefinition(
        id=Tag.WITCH,
        label='Witch',
        definition=(
            'Witches, witch society, or being a witch is a major character identity, premise, or persistent world '
            'element; generic magic users do not automatically qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.DINOSAURS,
        label='Dinosaurs',
        definition=(
            'Dinosaurs are major characters, creatures, subjects, or a persistent part of the setting or premise; '
            'brief appearances, fossils, or references are insufficient.'
        ),
    ),
    TagDefinition(
        id=Tag.UNDERWATER_SETTING,
        label='Underwater Setting',
        definition=(
            'A substantial portion of the narrative or world exists underwater, such as an underwater civilization, '
            'settlement, realm, or persistent environment; swimming, scuba diving, submarines, ocean travel, or brief '
            'underwater visits alone do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.UNDERGROUND_SETTING,
        label='Underground Setting',
        definition=(
            'A substantial portion of the narrative or world exists beneath the surface, such as an underground '
            'civilization, settlement, city, colony, or persistent environment; criminal undergrounds, underground '
            'fighting, music or resistance, and merely visiting caves or dungeons do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.PHOTOGRAPHY,
        label='Photography',
        definition=(
            'Photography itself is a central subject, recurring activity, artistic pursuit, narrative mechanism, or '
            'defining premise; merely having a photographer or photojournalist character is insufficient when '
            'photography does not structure the story.'
        ),
    ),
    TagDefinition(
        id=Tag.JOURNALISM,
        label='Journalism',
        definition=(
            'Journalism or reporting itself is a central subject, recurring activity, investigative mechanism, or '
            'defining workplace or premise; merely having a journalist character is insufficient.'
        ),
    ),
    TagDefinition(
        id=Tag.CLONING,
        label='Cloning',
        definition=(
            'Cloning is recurring, plot-relevant, or substantially defines a character, conflict, or premise; '
            'incidental mentions of clones are insufficient.'
        ),
    ),
    TagDefinition(
        id=Tag.ENSLAVEMENT,
        label='Enslavement',
        definition=(
            'Ownership, forced servitude, slavery, or escape from slavery materially shapes the premise, character '
            'arc, relationship, or conflict.'
        ),
    ),
    TagDefinition(
        id=Tag.ABANDONMENT,
        label='Abandonment',
        definition=(
            'A character being deliberately abandoned or deserted is a meaningful recurring premise, formative event, '
            'or character conflict; ordinary separation or someone simply being absent does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ACTS_OF_TERROR,
        label='Acts of Terror',
        definition=(
            'Deliberate large-scale or targeted violence or intimidation intended to terrorize a population or advance '
            'an ideological, political, or organizational objective; generic violence, crime, or destruction does '
            'not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ABUSIVE_TREATMENT,
        label='Abusive Treatment',
        definition=(
            'Recurring or significant cruel, harmful, degrading, coercive, or controlling treatment, including '
            'physical, emotional, psychological, verbal, familial, or institutional abuse; incidental hostility, '
            'ordinary conflict, isolated violence, or general villainy is insufficient. Distinct from bullying, '
            'persecution, captivity, enslavement, trauma, and abandonment.'
        ),
    ),
    TagDefinition(
        id=Tag.PARTNER_BATTLING,
        label='Partner Battling',
        definition=(
            'Combat or competitive battling is substantially performed by an autonomous creature, monster, spirit, '
            'or other entity partnered with a participant, rather than primarily by the participant directly; the '
            'partner has meaningful agency and is not merely a weapon or tool. Pokémon, conventional Digimon, and '
            'Zatch Bell are canonical examples.'
        ),
    ),
    TagDefinition(
        id=Tag.TOY_BATTLING,
        label='Toy Battling',
        definition=(
            'Combat or competition is substantially performed through specialized toys, toy-like objects, or physical '
            'battle devices operated by participants; the object or device is the defining battle mechanic rather '
            'than an ordinary weapon or innate ability. Beyblade, B-Daman, Crush Gear, and Bottleman are canonical '
            'examples.'
        ),
    ),
    TagDefinition(
        id=Tag.DYSFUNCTIONAL_FAMILY,
        label='Dysfunctional Family',
        definition=(
            'A troubled or unhealthy family dynamic is a major recurring focus, involving persistent conflict, '
            'neglect, abuse, estrangement, manipulation, or other damaging relationships between family members.'
        ),
    ),
    TagDefinition(
        id=Tag.ELEMENTAL_POWERS,
        label='Elemental Powers',
        definition=(
            'Characters regularly wield supernatural abilities based on natural elements such as fire, water, earth, '
            'wind, lightning, ice, or similar elemental forces; visually elemental attacks alone do not qualify '
            'unless elemental manipulation is an established ability.'
        ),
    ),
    TagDefinition(
        id=Tag.FRAMED_FOR_A_CRIME,
        label='Framed for a Crime',
        definition=(
            'A major character is falsely accused or deliberately framed for a crime or serious wrongdoing, and '
            'dealing with the accusation or its consequences is a significant part of the story.'
        ),
    ),
    TagDefinition(
        id=Tag.HACKING,
        label='Hacking',
        definition=(
            'Computer hacking, cybersecurity intrusion, system exploitation, or unauthorized manipulation of digital '
            'systems is a major recurring activity or plot mechanism; ordinary computer use does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.HISTORICAL_FIGURES,
        label='Historical Figures',
        definition=(
            'Identifiable real historical people materially appear as characters, including fictionalized, summoned, '
            'reincarnated, gender-swapped, or alternate-history versions of them; historical settings alone do not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.KIDNAPPING,
        label='Kidnapping',
        definition=(
            'Abduction or kidnapping is a major plot element, such as a significant character being abducted, an '
            'abduction driving a major arc, or kidnapping occurring repeatedly; brief or incidental captures do not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.LONELINESS,
        label='Loneliness',
        definition=(
            "Persistent loneliness, emotional isolation, or a character's struggle to form meaningful connections "
            'is a major recurring emotional theme; simply being alone or socially independent does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MONSTER_OF_THE_WEEK,
        label='Monster of the Week',
        definition=(
            'The story repeatedly follows an episodic structure in which the protagonists confront a different '
            'monster, creature, villain, supernatural threat, or equivalent opponent in successive episodes or arcs.'
        ),
    ),
    TagDefinition(
        id=Tag.MOTORSPORT,
        label='Motorsport',
        definition=(
            'Competitive racing involving motorized land vehicles is a major recurring focus, including automobile, '
            'kart, motorcycle, circuit, street, rally, and similar motor-vehicle racing; excludes horse racing, '
            'cycling, aircraft racing, and toy racing.'
        ),
    ),
    TagDefinition(
        id=Tag.ORPHAN,
        label='Orphan',
        definition=(
            'A major protagonist has lost both parents, was abandoned by them, or otherwise grows up without parental '
            'guardians, and this background meaningfully informs their circumstances, identity, or story; a deceased '
            'parent alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SECOND_CHANCE,
        label='Second Chance',
        definition=(
            'A major character receives a meaningful opportunity to redo, rebuild, or fundamentally change a life '
            'that previously went wrong. This may result from reincarnation, regression, recovery, release, '
            'relocation, or another major life reset, but the renewed opportunity must be thematically important.'
        ),
    ),
    TagDefinition(
        id=Tag.SIBLINGS,
        label='Siblings',
        definition=(
            'The relationship, bond, conflict, or shared journey between siblings is a major recurring focus; merely '
            'having a sibling does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SOCIAL_ANXIETY,
        label='Social Anxiety',
        definition=(
            'A major character experiences persistent anxiety, fear, or severe discomfort in social interaction or '
            'social evaluation, and overcoming or living with this difficulty is a recurring part of the story; '
            'ordinary shyness does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SPLIT_PERSONALITY,
        label='Split Personality',
        definition=(
            'A major character possesses two or more distinct personalities, identities, or recurring alternate '
            'personas that meaningfully affect their behavior and the story; disguises, acting, body sharing, and '
            'ordinary changes in demeanor do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.TEEN_PROTAGONIST,
        label='Teen Protagonist',
        definition=(
            'One or more major protagonists are teenagers, approximately ages 13-19, for a substantial portion of '
            'the story; high-school protagonists normally qualify unless an explicitly different age is established.'
        ),
    ),
    TagDefinition(
        id=Tag.URBAN_LEGEND,
        label='Urban Legend',
        definition=(
            'Urban legends, contemporary folklore, rumors of supernatural phenomena, or locally circulated '
            'mysterious stories are a major recurring element of the plot or world; general supernatural activity '
            'alone does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.WEREWOLVES,
        label='Werewolves',
        definition=(
            'Werewolves or comparable humans who transform into wolf-like supernatural beings are materially '
            'important to the story, world, or recurring cast; ordinary wolves, beastfolk, and unrelated shapeshifters '
            'do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.GUILDS,
        label='Guilds',
        definition=(
            'A formal guild or guild-like organization is a major recurring part of the story, with characters '
            'joining, working for, competing through, managing, or interacting with guilds as an important part of '
            'the setting or progression; mere organizations, clubs, parties, or factions do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SPIRIT_MANIFESTATION,
        label='Spirit Manifestation',
        definition=(
            'Characters manifest supernatural entities, spirits, avatars, or projections intrinsically linked to '
            'them that regularly function as combat abilities or supernatural powers; the manifested entity is bound '
            'to or an extension of its user rather than an independently acquired battling partner.'
        ),
    ),
    TagDefinition(
        id=Tag.LAW_ENFORCEMENT,
        label='Law Enforcement',
        definition=(
            'Police officers, law-enforcement agencies, or comparable official public-security organizations and '
            'their work are a major recurring focus; merely interacting with police, being investigated, committing '
            'crimes, or having isolated police characters does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ADOPTION,
        label='Adoption',
        definition=(
            'Adoption, foster care, or an adoptive parent-child relationship is a major part of a principal '
            "character's background, family structure, or ongoing story; merely being an orphan, being raised "
            'temporarily by someone else, or informally treating friends as family does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.FAIRIES,
        label='Fairies',
        definition=(
            'Fairies, faeries, or comparable supernatural fairy folk are materially important to the story, world, or '
            'recurring cast; incidental fairy imagery, fairy tales, nicknames, or characters merely described as '
            'fairy-like do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.GHOSTS,
        label='Ghosts',
        definition=(
            'Ghosts or the lingering spirits of deceased beings are materially important to the story, world, or '
            'recurring cast; generic spirits, supernatural beings, yokai, metaphorical ghosts, organization names, or '
            'brief hauntings do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ANGELS,
        label='Angels',
        definition=(
            'Angels or comparable celestial beings are materially important to the story, world, or recurring cast; '
            'characters merely described as angelic, angel-themed names or organizations, symbolic angels, and '
            'unrelated beings called “Angels” do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.UNREQUITED_LOVE,
        label='Unrequited Love',
        definition=(
            'One or more principal characters experience sustained, unreciprocated romantic feelings that materially '
            'drive interpersonal tension, emotional conflict, or character growth; brief crushes or background '
            'admirers do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.FORBIDDEN_ROMANCE,
        label='Forbidden Romance',
        definition=(
            'A central romantic relationship violates social, familial, factional, religious, or institutional taboos '
            'or rules, creating sustained secrecy, persecution, or conflict; ordinary parental disapproval or minor '
            'embarrassment does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ENEMIES_TO_LOVERS,
        label='Enemies to Lovers',
        definition=(
            'Two characters who begin as genuine adversaries, combatants, or members of opposing factions gradually '
            'develop a central romantic bond; mild bickering between classmates or friendly rivals does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.AGE_GAP_ROMANCE,
        label='Age Gap Romance',
        definition=(
            'A central romantic relationship features a significant, story-relevant age or life-stage difference '
            'between the partners that shapes their dynamic or social perception; immortal beings who look and act '
            'like peers without age-gap framing do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.HEARTWARMING,
        label='Heartwarming',
        definition=(
            'The work sustains a warm, emotionally uplifting, tender, or comforting atmosphere centered on kindness, '
            'empathy, healing, or supportive human connection; isolated sweet moments in an otherwise harsh or '
            'action-driven story do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SATIRE,
        label='Satire',
        definition=(
            'The work systematically uses irony, exaggeration, or pointed ridicule to critique social institutions, '
            'politics, media, cultural norms, or genre conventions; ordinary slapstick or isolated jokes do not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.ABSURDIST,
        label='Absurdist',
        definition=(
            'The work relies on surreal, illogical, or extreme deadpan nonsense where bizarre, rule-defying '
            'situations are central to the humor or worldview; standard exaggeration or occasional gag scenes do not '
            'qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.BITTERSWEET,
        label='Bittersweet',
        definition=(
            'The narrative blends genuine warmth, affection, or hope with poignant loss, impermanence, parting, or '
            'lingering emotional ache; purely bleak tragedies or purely cheerful stories do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.TRAGEDY,
        label='Tragedy',
        definition=(
            'The narrative centers on irreversible catastrophe, fatal flaws, or doomed circumstances leading to '
            'profound loss, ruin, or death; incidental character deaths or backstory sadness alone do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SLOW_LIFE,
        label='Slow Life',
        definition=(
            'A protagonist intentionally steps away from high-stakes conflict, heroism, or corporate exhaustion to '
            'pursue a peaceful, low-stress everyday routine in a rural, frontier, or fantasy setting; ordinary slice '
            'of life without a retreat or slow-living premise does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.SPACE_OPERA,
        label='Space Opera',
        definition=(
            'A large-scale science-fiction narrative set across star systems or spacefaring civilizations involving '
            'interstellar politics, space fleets, or galactic conflict; stories merely set on a single spaceship or '
            'station without broader interstellar scope do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.GLADIATOR,
        label='Gladiator',
        definition=(
            'Arena combat where captives, slaves, prisoners, or professional fighters battle for spectacle, survival, '
            'or freedom is a central recurring element; standard sporting tournaments do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.STOIC_PROTAGONIST,
        label='Stoic Protagonist',
        definition=(
            'A principal protagonist is defined by extreme emotional restraint, deadpan composure, or aloof '
            'detachment that consistently shapes their interactions, humor, or problem-solving; temporarily serious '
            'characters do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.THEATER,
        label='Theater',
        definition=(
            'Stage acting, theatrical troupes, musicals, opera, or dramatic stage production is a central activity or '
            'setting; a single school festival play does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.PAINTING_DRAWING,
        label='Painting & Drawing',
        definition=(
            'Painting, drawing, illustration, sketching, or fine-art creation is a central activity, academic focus, '
            'or character pursuit; incidental art club membership does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.MANGA_ANIME_CREATION,
        label='Manga & Anime Creation',
        definition=(
            'Writing, drawing, animating, producing, or publishing manga, anime, or light novels is a central '
            'workplace or creative focus; characters who merely read manga or watch anime do not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.VOICE_ACTING,
        label='Voice Acting',
        definition=(
            'Voice acting (seiyuu) performance, studio recording, and the voice-acting industry are a central focus '
            'of the story or cast.'
        ),
    ),
    TagDefinition(
        id=Tag.APOTHECARY,
        label='Apothecary',
        definition=(
            'Herbalism, potion or medicine compounding, pharmacology, poison analysis, or apothecary work is a '
            'central profession or recurring craft; generic healing magic or hospital surgery does not qualify.'
        ),
    ),
    TagDefinition(
        id=Tag.NOSTALGIC,
        label='Nostalgic',
        definition=(
            'A wistful, reflective atmosphere centered on memories of youth, bygone eras, fading traditions, '
            'hometowns, or the passage of time substantially shapes the emotional tone; merely being set in the '
            'past does not qualify.'
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
    tags: Iterable[TagDefinition] = TAG_REGISTRY.definitions,
) -> dict[int, tuple[str, ...]]:
    """Return deterministic tag assignments for IDs present in the catalogue."""
    available_ids = set(anime_ids)
    result: dict[int, set[str]] = {}
    for assignment in assignments:
        for anime_id in assignment.anime_ids:
            if anime_id in available_ids:
                result.setdefault(anime_id, set()).update(assignment.tag_ids)
    order = {tag.id: index for index, tag in enumerate(tags)}
    return {anime_id: tuple(sorted(values, key=order.__getitem__)) for anime_id, values in result.items()}


def validate_tags_against_taxonomy(tags: Iterable[TagDefinition], taxonomy: Mapping[str, Iterable[str]]) -> None:
    """Reject Kelbrum tags that duplicate source taxonomy values."""
    source_values = {value.casefold() for values in taxonomy.values() for value in values}
    seen_ids: set[str] = set()
    for tag in tags:
        if not tag.id or tag.id in seen_ids:
            raise ValueError(f'duplicate or empty tag ID: {tag.id!r}')
        if tag.label.casefold() in source_values:
            raise ValueError(f'tag overlaps source taxonomy: {tag.label}')
        seen_ids.add(tag.id)


def _build_tag_salience_mapping() -> dict[str, float]:
    mapping: dict[str, float] = {}
    for tag in Tag:
        tag_value = tag.value
        if tag in NARRATIVE_POLICY_TAGS:
            mapping[tag_value] = 0.0
        elif tag in PERSONA_CAST_TAGS:
            mapping[tag_value] = TagSalienceTier.PERSONA_CAST.value
        elif tag in CORE_HOOK_TAGS:
            mapping[tag_value] = TagSalienceTier.CORE_HOOK.value
        elif tag in TONE_ATMOSPHERE_TAGS:
            mapping[tag_value] = TagSalienceTier.TONE_ATMOSPHERE.value
        elif tag in SETTING_BACKDROP_TAGS:
            mapping[tag_value] = TagSalienceTier.SETTING_BACKDROP.value
        else:
            mapping[tag_value] = TagSalienceTier.MOTIF_ORGANISM.value
    return mapping


TAG_SALIENCE_MAPPING: Final[dict[str, float]] = _build_tag_salience_mapping()


def get_tag_salience(tag_id: str) -> float:
    """Return explicit narrative salience weight for any tag."""
    return TAG_SALIENCE_MAPPING.get(tag_id, TagSalienceTier.MOTIF_ORGANISM.value)
