"""Curated additions to source themes that are missing from catalogue records."""

from functools import cache

import msgspec

from config import derive_payload_identity


class ThemeCorrection(msgspec.Struct, frozen=True):
    """Themes to add to a validated set of catalogue entries."""

    anime_ids: tuple[int, ...]
    themes: tuple[str, ...]
    remove_themes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.anime_ids or any(anime_id <= 0 for anime_id in self.anime_ids):
            raise ValueError('theme correction IDs must be positive')
        if not self.themes or any(not theme.strip() for theme in self.themes):
            raise ValueError('theme correction names cannot be empty')
        if any(not theme.strip() for theme in self.remove_themes):
            raise ValueError('theme removal names cannot be empty')


class ThemeCorrectionRegistry(msgspec.Struct, frozen=True):
    """Versioned typed curation resource owned by processing."""

    version: str
    corrections: tuple[ThemeCorrection, ...]

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError('theme correction registry version cannot be empty')

    def identity(self) -> str:
        """Return the deterministic identity of this curated resource."""
        return derive_payload_identity(self)


THEME_CORRECTIONS_VERSION = 'theme-corrections-v1'

_THEME_CORRECTION_DATA: tuple[tuple[tuple[int, ...], tuple[str, ...]], ...] = (
    # Delinquents: Yuu☆Yuu☆Hakusho (392), Yuuyake Banchou (12765), Glass no Kamen desu ga (17707),
    # Rainbow (6114), School Rumble (24).
    ((392, 12765, 17707, 6114, 24), ('Delinquents',)),
    # Showbiz: Mahou no Stage Fancy Lala (604), Eikyuu Kazoku (1106), Skip Beat! (4722).
    ((604, 1106, 4722), ('Showbiz',)),
    # Medical: Nurse Angel Ririka SOS (616).
    ((616,), ('Medical',)),
    # Crossdressing: Hakuouki Movie 1 (13117), Junlin Chengxia (34724).
    ((13117, 34724), ('Crossdressing',)),
    # High Stakes Game: Xue Se Cang Qiong (36762).
    ((36762,), ('High Stakes Game',)),
    # Reverse Harem: Hakuouki (6895), Hekketsuroku (9065), Movie 1 (13117), Movie 2 (13119).
    ((6895, 9065, 13117, 13119), ('Reverse Harem',)),
    # Love Polygon: Kannazuki no Miko (143).
    ((143,), ('Love Polygon',)),
    # Villainess: Gekai Elise (54632).
    ((54632,), ('Villainess',)),
    # Survival: Mirai Shounen Conan (302), Turn A Gundam (95), Wonderful Days (548).
    ((302, 95, 548), ('Survival',)),
    # Combat Sports: Shijou Saikyou no Deshi Kenichi (1559).
    ((1559,), ('Combat Sports',)),
    # Martial Arts: Grappler Baki (287, 551).
    ((287, 551), ('Martial Arts',)),
    # Isekai: Kyouryuu Boukenki Jura Tripper (2487).
    ((2487,), ('Isekai',)),
    # Reincarnation: Juubee-chan (635), Babel Nisei (1664, 1666), Juushin Enbu (2772).
    ((635, 1664, 1666, 2772), ('Reincarnation',)),
    # Samurai: Otogizoushi (525), Jubei-chan (635), Laughing Under the Clouds (21743),
    # Ninja Girl & Samurai Master (32829, 34978).
    ((525, 635, 21743, 32829, 34978), ('Samurai',)),
    # Otaku Culture: Kuragehime (8129).
    ((8129,), ('Otaku Culture',)),
    # Performing Arts: Interstella5555 (731), Yuri!!! on Ice (32995), Ginban Kaleidoscope (476).
    ((731, 32995, 476), ('Performing Arts',)),
    # Vampire: Vampiyan Kids (3290), UQ Holder! (33478), Vampire Holmes (28929).
    ((3290, 33478, 28929), ('Vampire',)),
    # Magical Gender Shift: Ranma ½: Chou Musabetsu Kessen! (1010).
    ((1010,), ('Magical Gender Shift',)),
    # Gourmet: Cooking Master Boy (110), Oishinbo (1093), Mister Ajikko (3437), and related titles through
    # Fermat Kitchen (60697).
    (
        (
            28,
            110,
            1093,
            3437,
            6586,
            8123,
            24629,
            28171,
            32828,
            33447,
            34012,
            39194,
            40957,
            41556,
            48779,
            48804,
            52701,
            57325,
            60697,
        ),
        ('Gourmet',),
    ),
    # Mythology: My Neighbor Totoro (523), The Eccentric Family (34792).
    ((523, 34792), ('Mythology',)),
    # Slice of Life and Iyashikei: My Neighbor Totoro (523).
    ((523,), ('Slice of Life', 'Iyashikei')),
    # Iyashikei: Hotarubi no Mori e (10408).
    ((10408,), ('Iyashikei',)),
    # Iyashikei: Barakamon (22789).
    ((22789,), ('Iyashikei',)),
    # Mythology and Anthropomorphic: Pom Poko (1030).
    ((1030,), ('Mythology', 'Anthropomorphic')),
    # Anthropomorphic and Childcare: Leafie (12917).
    ((12917,), ('Anthropomorphic', 'Childcare')),
    # Anthropomorphic and Mythology: Ponyo (2890).
    ((2890,), ('Anthropomorphic', 'Mythology')),
    # Anthropomorphic: Animal Crossing: The Movie (2950).
    ((2950,), ('Anthropomorphic',)),
    # Anthropomorphic and Mythology: Summer Days with Coo (2848).
    ((2848,), ('Anthropomorphic', 'Mythology')),
    # Childcare and Mythology: Wolf Children (8598).
    ((8598,), ('Childcare', 'Mythology')),
    # Childcare: Mirai (36936).
    ((36936,), ('Childcare',)),
    # Childcare: Akachan to Boku (1485).
    ((1485,), ('Childcare',)),
    # Mythology and Iyashikei: Natsume's Book of Friends (4081).
    ((4081,), ('Mythology', 'Iyashikei')),
    # Mythology: Spirited Away (199).
    ((199,), ('Mythology',)),
    # Workplace and Iyashikei: Kiki's Delivery Service (512).
    ((512,), ('Workplace', 'Iyashikei')),
    # Iyashikei: Arrietty (7711).
    ((7711,), ('Iyashikei',)),
    # Iyashikei: Mushishi (457), Hakumei and Mikochi (36094), Non Non Biyori (17549).
    ((457, 36094, 17549), ('Iyashikei',)),
    # Historical: Ninjaboy Rantaro (1199), Kamen no Ninja Akakage (13769).
    ((1199, 13769), ('Historical',)),
    # Space: Galaxy Angel Z (652), Galaxy Angel A (653).
    ((652, 653), ('Space',)),
    # School: Suzuka (390).
    ((390,), ('School',)),
    # Space: Space Pirate Captain Harlock (1000), Angel Links (1226), Uchuu Majin Daikengou (10224).
    ((1000, 1226, 10224), ('Space',)),
    # Detective: Layton Mystery Tanteisha (37023), Cuticle Detective Inaba (15109),
    # Sakon the Ventriloquist (2204).
    ((37023, 15109, 2204), ('Detective',)),
)

THEME_CORRECTION_REGISTRY = ThemeCorrectionRegistry(
    THEME_CORRECTIONS_VERSION,
    tuple(ThemeCorrection(anime_ids=anime_ids, themes=themes) for anime_ids, themes in _THEME_CORRECTION_DATA),
)
MANUAL_THEME_ADDITIONS = THEME_CORRECTION_REGISTRY.corrections


@cache
def theme_correction_registry_identity() -> str:
    """Return the cached identity of processing theme corrections."""
    return THEME_CORRECTION_REGISTRY.identity()
