"""Curated additions to source themes that are missing from catalogue records."""

MANUAL_THEME_ADDITIONS: tuple[tuple[tuple[int, ...], tuple[str, ...]], ...] = (
    # Delinquents: Yuu☆Yuu☆Hakusho (392), Yuuyake Banchou (12765),
    # Glass no Kamen desu ga (17707), Rainbow (6114), School Rumble (24).
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
    # Samurai: Otogizoushi (525), Jubei-chan (635),
    # Laughing Under the Clouds (21743), Ninja Girl & Samurai Master (32829, 34978).
    ((525, 635, 21743, 32829, 34978), ('Samurai',)),
    # Otaku Culture: Kuragehime (8129).
    ((8129,), ('Otaku Culture',)),
    # Performing Arts: Interstella5555 (731), Yuri!!! on Ice (32995), Ginban Kaleidoscope (476).
    ((731, 32995, 476), ('Performing Arts',)),
    # Vampire: Vampiyan Kids (3290), UQ Holder! (33478), Vampire Holmes (28929).
    ((3290, 33478, 28929), ('Vampire',)),
    # Magical Gender Shift: Ranma ½: Chou Musabetsu Kessen! (1010).
    ((1010,), ('Magical Gender Shift',)),
    # Gourmet: Cooking Master Boy (110), Oishinbo (1093), Mister Ajikko (3437),
    # Cooking Papa (8123), Yumeiro Pâtissière (6586), Koufuku Graffiti (24629),
    # Sweetness & Lightning (32828), Isekai Shokudou (34012, 48804),
    # True Cooking Master Boy (39194, 40957), Piace (33447),
    # Maiko-san Chi no Makanai-san (41556), Deaimon (48779),
    # Delicious in Dungeon (52701), Ramen Akaneko (57325), Fermat Kitchen (60697),
    # Yakitate!! Japan (28), Food Wars! (28171).
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
    # My Neighbor Totoro (523): forest spirit and fantastical woodland creatures are central.
    ((523, 34792), ('Mythology',)),
    # My Neighbor Totoro (523): quiet rural everyday life and restorative atmosphere are central.
    ((523,), ('Slice of Life', 'Iyashikei')),
    # Hotarubi no Mori e (10408): a quiet, restorative supernatural drama.
    ((10408,), ('Iyashikei',)),
    # Barakamon (22789): rural community life and personal restoration are central.
    ((22789,), ('Iyashikei',)),
    # Pom Poko (1030): tanuki society, shapeshifting, and folklore are central.
    ((1030,), ('Mythology', 'Anthropomorphic')),
    # Leafie (12917): an anthropomorphic animal story centered on raising a duckling.
    ((12917,), ('Anthropomorphic', 'Childcare')),
    # Ponyo (2890): an anthropomorphic supernatural child/fish story.
    ((2890,), ('Anthropomorphic', 'Mythology')),
    # Animal Crossing: The Movie (2950): an anthropomorphic animal community is central.
    ((2950,), ('Anthropomorphic',)),
    # Summer Days with Coo (2848): a kappa story rooted in Japanese folklore.
    ((2848,), ('Anthropomorphic', 'Mythology')),
    # Wolf Children (8598): raising children and folklore are central.
    ((8598,), ('Childcare', 'Mythology')),
    # Mirai (36936): sibling and childcare relationships drive the story.
    ((36936,), ('Childcare',)),
    # Akachan to Boku (1485): an older sibling caring for a younger child is central.
    ((1485,), ('Childcare',)),
    # Natsume's Book of Friends (4081): yokai folklore and restorative supernatural stories are central.
    ((4081,), ('Mythology', 'Iyashikei')),
    # Spirited Away (199): Japanese mythological beings shape the story.
    ((199,), ('Mythology',)),
    # Kiki's Delivery Service (512): delivery work and restorative daily life are central.
    ((512,), ('Workplace', 'Iyashikei')),
    # Arrietty (7711): quiet restorative domestic life is a substantial theme.
    ((7711,), ('Iyashikei',)),
    # Mushishi (457), Hakumei and Mikochi (36094), and Non Non Biyori (17549): restorative daily life.
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
