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
    # Mythology: Princess Mononoke (164), A Letter to Momo (10389).
    ((164, 10389), ('Mythology',)),
    # Urban Fantasy and Super Power: Dandadan (57334).
    ((57334,), ('Urban Fantasy', 'Super Power')),
    # Time Travel: Steins;Gate Movie (11577), Zipang (29), The Girl Who Leapt Through Time (2236).
    ((11577, 29, 2236), ('Time Travel',)),
    # Detective: Kindaichi Case Files (2076), Gosick (8425).
    ((2076, 8425), ('Detective',)),
    # Historical and Samurai: Rurouni Kenshin: Trust & Betrayal (44).
    ((44,), ('Historical', 'Samurai')),
    # Military: Attack on Titan Season 3 Part 2 (38524).
    ((38524,), ('Military',)),
    # Team Sports: Slam Dunk (170).
    ((170,), ('Team Sports',)),
    # Detective: Poirot & Marple (244), Cinderella Boy (301), Loki Ragnarok (335), Spiral (341).
    ((244, 301, 335, 341), ('Detective',)),
    # Martial Arts: Bamboo Blade (649).
    ((649,), ('Martial Arts',)),
    # Medical: Ray The Animation (2396).
    ((2396,), ('Medical',)),
    # Racing: IGPX: Immortal Grand Prix (1409).
    ((1409,), ('Racing',)),
    # Space: Galaxy Angel (383), Galaxy Angel 4 (655).
    ((383, 655), ('Space',)),
    # Time Travel: Doraemon Movie 25 (2656), Dorami-chan (2639), Yattodetaman (4154), Time Travel Tondekeman! (2820).
    ((2656, 2639, 4154, 2820), ('Time Travel',)),
    # Detective: City Hunter 2 (1471), City Hunter '91 (1473), Kindaichi Returns (22817),
    # Kamisama no Memochou (10568), Strange+ (21067), Hamatora (20689).
    ((1471, 1473, 22817, 10568, 21067, 20689), ('Detective',)),
    # Music: Kaikan Phrase (861).
    ((861,), ('Music',)),
    # Martial Arts: Taekwon Dongja Maruchi Arachi (14821).
    ((14821,), ('Martial Arts',)),
    # Workplace: Wala! Pyeon-uijeom The Animation (17106).
    ((17106,), ('Workplace',)),
    # Racing: Initial D Second Stage (21).
    ((21,), ('Racing',)),
    # Historical: Meiji Tokyo Renka Movie 1 (29855).
    ((29855,), ('Historical',)),
    # Super Power: Busou Renkin (1536), Yozakura Quartet (4548), Black Bullet (20787), Saint October (1724).
    ((1536, 4548, 20787, 1724), ('Super Power',)),
    # Detective: Henjin no Salad Bowl (55877), Arne no Jikenbo (60255),
    # Toumei Otoko to Ningen Onna (60395), Mata Korosarete... Tantei-sama (62964).
    ((55877, 60255, 60395, 62964), ('Detective',)),
    # Music: Tari Tari (19840).
    ((19840,), ('Music',)),
    # Martial Arts: Mutsu Enmei Ryuu Gaiden (1381).
    ((1381,), ('Martial Arts',)),
    # Workplace: Kindan Joshi (45596).
    ((45596,), ('Workplace',)),
    # Time Travel: Stand By Me Doraemon (21469), Gan Gan Ganko-chan (34488), Li Xianji (44531), MIRU (55727).
    ((21469, 34488, 44531, 55727), ('Time Travel',)),
    # Super Power: Gakuen Senki Muryou (1179), Closers (32152), High Card (49154).
    ((1179, 32152, 49154), ('Super Power',)),
    # High Stakes Game: Eden of the East (5630).
    ((5630,), ('High Stakes Game',)),
    # Otaku Culture: Choukadou Girl 1/6 (38226).
    ((38226,), ('Otaku Culture',)),
    # School: Boys Be... (105), Wind: A Breath of Heart (623), Goldfish Warning! (727).
    ((105, 623, 727), ('School',)),
    # Workplace: Patrol-kun (3458), Kakuriyo no Yadomeshi (36754), Okko's Inn (37433).
    ((3458, 36754, 37433), ('Workplace',)),
    # Time Travel: El Cantare no Rekishikan (3496), Junod (9525), Dasshutsu Gasshapon (15971),
    # Gongnyong (16780), Million Arthur (37555), Uchuu no Hou (37915).
    ((3496, 9525, 15971, 16780, 37555, 37915), ('Time Travel',)),
    # Music: Love Live! (14807).
    ((14807,), ('Music',)),
    # Super Power: Mondaiji (15315).
    ((15315,), ('Super Power',)),
    # Performing Arts: Glass no Kamen desu ga (17707).
    ((17707,), ('Performing Arts',)),
    # Mythology: DanMachi (28121).
    ((28121,), ('Mythology',)),
    # Historical: Cike Nie Yinniang (45781), Fengyu Lang Qiao (48023), Akai Inei (59279),
    # Fengyu Lang Qiao: Kunlun Mo Lei (59367), Fengyu Lang Qiao: Bishamonten (59368), Imomushi (59704).
    ((45781, 48023, 59279, 59367, 59368, 59704), ('Historical',)),
    # Time Travel: Kaiketsu Zorori Movie: ZZ no Himitsu (35074).
    ((35074,), ('Time Travel',)),
    # Time Travel: Doraemon Movie 05 (2662), Crayon Shin-chan Movie 18 (8369),
    # Nekketsu Uchuujin (8935), Tsuyoshi no Time Machine (10943), Tonari no Tamageta-kun (20233).
    ((2662, 8369, 8935, 10943, 20233), ('Time Travel',)),
    # Detective: Nanako SOS (3619), Norakuro-kun (16393).
    ((3619, 16393), ('Detective',)),
    # Martial Arts: Robot Taekwon V (10763).
    ((10763,), ('Martial Arts',)),
    # Detective: Futakoi Alternative (126).
    ((126,), ('Detective',)),
    # School: High School Mystery: Gakuen Nanafushigi (9882), Ore Monogatari!! (28297).
    ((9882, 28297), ('School',)),
    # Historical: Ashita Genki ni Nare!: Hanbun no Satsumaimo (17493).
    ((17493,), ('Historical',)),
    # Pets: Kanojo to Kanojo no Neko (1004).
    ((1004,), ('Pets',)),
    # Childcare: Chocotto Sister (1258), Amaama to Inazuma (32901).
    ((1258, 32901), ('Childcare',)),
    # Visual Arts: Bakuman. (7674), Bakuman. 2nd Season (10030), Bakuman. 3rd Season (12365),
    # Eizouken ni wa Te wo Dasu na! (39792).
    ((7674, 10030, 12365, 39792), ('Visual Arts',)),
    # Mythology: Natsume Yuujinchou San (9843), Natsume Yuujinchou Roku (34534).
    ((9843, 34534), ('Mythology',)),
    # Music: Kono Oto Tomare! 2nd Season (38839).
    ((38839,), ('Music',)),
    # Workplace: Servant x Service (15689), Nami yo Kiitekure (40510).
    ((15689, 40510), ('Workplace',)),
    # Gourmet: Toriko (10033), Kakuriyo no Yadomeshi (36754), Isekai Izakaya: Koto Aitheria no Nobu (34420),
    # Emiya-san Chi no Kyou no Gohan (37033), Rokuhoudou Yotsuiro Biyori (36508).
    ((10033, 36754, 34420, 37033, 36508), ('Gourmet',)),
    # Racing: Uma Musume: Pretty Derby Season 3 (53524).
    ((53524,), ('Racing',)),
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
