"""Typed, feature-owned curated tag assignments."""

from functools import cache

import msgspec

from config import derive_payload_identity
from features.tags import TagAssignment, TagId

TAG_ASSIGNMENTS_VERSION = 'tag-assignments-v1'


class TagAssignmentRegistry(msgspec.Struct, frozen=True):
    """Versioned assignment resource consumed by feature assembly."""

    version: str
    assignments: tuple[TagAssignment, ...]

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError('tag assignment registry version cannot be empty')
        known_tag_ids = {tag_id.value for tag_id in TagId}
        unknown_tag_ids = {
            tag_id for assignment in self.assignments for tag_id in assignment.tag_ids if tag_id not in known_tag_ids
        }
        if unknown_tag_ids:
            raise ValueError(f'unknown tag IDs: {sorted(unknown_tag_ids)}')
        for assignment in self.assignments:
            if not assignment.anime_ids:
                raise ValueError('tag assignments must contain at least one anime ID')

    def identity(self) -> str:
        """Return the deterministic identity of this curated resource."""
        return derive_payload_identity(self)


MANUAL_TAG_ASSIGNMENTS: tuple[TagAssignment, ...] = (
    TagAssignment(
        # Space Brothers and its films (12431, 17573, 22583, 53938), Planetes (329), Moonlight Mile (1941, 2929),
        # Rocket Girls (1942).
        anime_ids=(12431, 17573, 22583, 53938, 329, 1941, 2929, 1942),
        tag_ids=(TagId.ASTRONAUT,),
    ),
    TagAssignment(
        # Ajin (31580, 30868, 30869, 30870, 33253), Undead Unluck (52741, 63177).
        anime_ids=(31580, 30868, 30869, 30870, 33253, 52741, 63177),
        tag_ids=(TagId.IMMORTALITY,),
    ),
    TagAssignment(
        # Mugen no Juunin (4151, 39806), To Your Eternity (41025, 49709, 54703).
        anime_ids=(4151, 39806, 41025, 49709, 54703),
        tag_ids=(TagId.IMMORTALITY,),
    ),
    TagAssignment(
        # One Piece (21), Fairy Tail (6702), Spy x Family franchise (50265, 50602, 53887, 53888, 59027),
        # Buddy Daddies (53411).
        anime_ids=(21, 6702, 50265, 50602, 53887, 53888, 59027, 53411),
        tag_ids=(TagId.FOUND_FAMILY,),
    ),
    TagAssignment(
        # Cowboy Bebop (1).
        anime_ids=(1,),
        tag_ids=(TagId.FOUND_FAMILY,),
    ),
    TagAssignment(
        # Akagi (658), Saki (5671, 10884, 16123), Touhai (57796).
        anime_ids=(658, 5671, 10884, 16123, 57796),
        tag_ids=(TagId.MAHJONG,),
    ),
    TagAssignment(
        # Shion no Ou (2562), 3-gatsu no Lion (31646, 35180), Ryuuou no Oshigoto! (35905).
        anime_ids=(2562, 31646, 35180, 35905),
        tag_ids=(TagId.SHOGI,),
    ),
    TagAssignment(
        # Hikaru no Go (135).
        anime_ids=(135,),
        tag_ids=(TagId.GO,),
    ),
    TagAssignment(
        # DanMachi (28121, 37347, 40454, 47164, 53111, 57066).
        anime_ids=(28121, 37347, 40454, 47164, 53111, 57066),
        tag_ids=(TagId.DUNGEON, TagId.ADVENTURING_PARTY),
    ),
    TagAssignment(
        # Grimgar (31859), Goblin Slayer (37349, 39576, 47160), Handyman Saitou (50854).
        anime_ids=(31859, 37349, 39576, 47160, 50854),
        tag_ids=(TagId.ADVENTURING_PARTY,),
    ),
    TagAssignment(
        # Frieren (52991, 59978), Dungeon Meshi (52701, 59068).
        anime_ids=(52991, 59978, 52701, 59068),
        tag_ids=(TagId.ADVENTURING_PARTY,),
    ),
    TagAssignment(
        # KonoSuba (30831, 32937, 49458, 61203).
        anime_ids=(30831, 32937, 49458, 61203),
        tag_ids=(TagId.ADVENTURING_PARTY,),
    ),
    TagAssignment(
        # Lazarus (56038).
        anime_ids=(56038,),
        tag_ids=(TagId.CONSPIRACY,),
    ),
    TagAssignment(
        # Cowboy Bebop: The Movie (5); Innocence (468); Ergo Proxy (790); Patlabor 2 (1095).
        anime_ids=(5, 468, 790, 1095),
        tag_ids=(TagId.CONSPIRACY,),
    ),
    TagAssignment(
        # A.I.C.O. Incarnation (36039), Ling Yu (36291), Jue Ji (39116), Can Ci Pin (40885),
        # Xian Feng Jianyu Lu (42291), An Jie Shen Shi (45195), Shengsi Huifang (47231),
        # Chi Yan Jinyiwei (49432), Feng Huo Zhan Ji (55746), Free Fire Daybreak (58849),
        # Sanguo Sha (59183), Juan Siliang 3rd Season (59631), Douzhan Tianxia (60797),
        # Qi Guo Yinhe (61635), Cheng Huang Lu (64375).
        anime_ids=(
            36039,
            36291,
            39116,
            40885,
            42291,
            45195,
            47231,
            49432,
            55746,
            58849,
            59183,
            59631,
            60797,
            61635,
            64375,
        ),
        tag_ids=(TagId.CONSPIRACY,),
    ),
    TagAssignment(
        # Cultivation-focused donghua and fantasy series.
        anime_ids=(45997, 46821, 48116, 48502, 50633, 51492, 52180, 52597, 54631),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # 009-1 (1583), Chocolate Underground (5238), Idol Jihen (34028), Sui Tang Heroes (44178),
        # Youan Xiao Jing de Gui (56589), Sanguo Di Yi Bu (64675).
        anime_ids=(1583, 5238, 34028, 44178, 56589, 64675),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Mobile Suit Gundam (80), Zeta Gundam (85), Victory Gundam (89), Gundam Wing (90), Gundam X (92),
        # Gundam SEED (93), Gundam SEED Destiny (94), Turn A Gundam (95), Gundam 00 (2581, 3927),
        # Gundam Unicorn RE:0096 (32792), Iron-Blooded Orphans (31251, 33051), Gundam Hathaway (37765),
        # Witch from Mercury (49828, 53199).
        anime_ids=(80, 85, 89, 90, 92, 93, 94, 95, 2581, 3927, 32792, 31251, 33051, 37765, 49828, 53199),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Gundam Hathaway (37765), Iron-Blooded Orphans (31251, 33051).
        anime_ids=(37765, 31251, 33051),
        tag_ids=(TagId.REBELLION,),
    ),
    TagAssignment(
        # Gundam X (92).
        anime_ids=(92,),
        tag_ids=(TagId.POST_APOCALYPTIC,),
    ),
    TagAssignment(
        # Gundam Wing (90).
        anime_ids=(90,),
        tag_ids=(TagId.REBELLION,),
    ),
    TagAssignment(
        # Gundam SEED Destiny (94).
        anime_ids=(94,),
        tag_ids=(TagId.REVENGE,),
    ),
    TagAssignment(
        # Turn A Gundam (95).
        anime_ids=(95,),
        tag_ids=(TagId.POST_APOCALYPTIC,),
    ),
    TagAssignment(
        # Gundam 00 Second Season (3927).
        anime_ids=(3927,),
        tag_ids=(TagId.CONSPIRACY,),
    ),
    TagAssignment(
        # Mahouka Koukou no Rettousei (20785).
        anime_ids=(20785,),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # Mahouka Koukou no Rettousei: Raihousha-hen (40497).
        anime_ids=(40497,),
        tag_ids=(TagId.ABILITY_BATTLES, TagId.ESPIONAGE),
    ),
    TagAssignment(
        # Mahouka Koukou no Rettousei 3rd Season (50713).
        anime_ids=(50713,),
        tag_ids=(TagId.POLITICS, TagId.CONSPIRACY),
    ),
    TagAssignment(
        # Super Crooks (48453).
        anime_ids=(48453,),
        tag_ids=(TagId.HEIST, TagId.ABILITY_BATTLES, TagId.SUPERHERO),
    ),
    TagAssignment(
        # Tokyo Ghoul (22319), Ajin TV entries (31580, 33253),
        # Parasyte (22535), Kemonozume (1454), Pupa (19315), Attack on Titan (16498),
        # Kabaneri (28623), Inuyashiki (34542), Fool Night (64459), Chainsaw Man (44511),
        # Kaiju No. 8 (52588).
        anime_ids=(22319, 31580, 33253, 22535, 1454, 19315, 16498, 28623, 34542, 64459, 44511, 52588),
        tag_ids=(TagId.MONSTERIZATION,),
    ),
    TagAssignment(
        # Kaiju No. 8 (52588).
        anime_ids=(52588,),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Gargantia on the Verdurous Planet (16524).
        anime_ids=(16524,),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Beyond the Boundary (18153).
        anime_ids=(18153,),
        tag_ids=(TagId.MONSTERIZATION, TagId.MONSTER_HUNTING),
    ),
    TagAssignment(
        # Bouken Ou Beet (8); Bouken Ou Beet Excellion (1123); Vampire Hunter D (732);
        # Vampire Hunter D: Bloodlust (543).
        anime_ids=(8, 543, 732, 1123),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Mushibugyou (17505).
        anime_ids=(17505,),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Kengan Ashura (36903), The God of High School (41353), Shaman King (154),
        # Juni Taisen: Zodiac War (35076), Record of Ragnarok entries (44942, 49618,
        # 55454, 61200).
        anime_ids=(36903, 41353, 154, 35076, 44942, 49618, 55454, 61200),
        tag_ids=(TagId.TOURNAMENT,),
    ),
    TagAssignment(
        # Zombie-Loan (2404), Zom 100: Bucket List of the Dead (54112),
        # Kabaneri (28623), The Empire of Corpses (28625).
        anime_ids=(2404, 54112, 28623, 28625),
        tag_ids=(TagId.ZOMBIE,),
    ),
    TagAssignment(
        # Himiko-den (360); Kaibutsu Oujo (2130); Biohazard: Degeneration (3446); Shikabane Hime: Aka (4581).
        anime_ids=(360, 2130, 3446, 4581),
        tag_ids=(TagId.ZOMBIE,),
    ),
    TagAssignment(
        # Zombie-Loan (2404), Kabaneri (28623), Attack on Titan (16498), Bleach (269).
        anime_ids=(2404, 28623, 16498, 269),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Hell's Paradise: Jigokuraku (46569).
        anime_ids=(46569,),
        tag_ids=(TagId.NINJA, TagId.MONSTER_HUNTING),
    ),
    TagAssignment(
        # God Eater (27631).
        anime_ids=(27631,),
        tag_ids=(TagId.MONSTERIZATION, TagId.MONSTER_HUNTING),
    ),
    TagAssignment(
        # Blue Exorcist (9919, 11737, 33506, 53889, 58516, 59226).
        anime_ids=(9919, 11737, 33506, 53889, 58516, 59226),
        tag_ids=(TagId.MONSTERIZATION, TagId.MONSTER_HUNTING),
    ),
    TagAssignment(
        # Deca-Dence (40056).
        anime_ids=(40056,),
        tag_ids=(TagId.MONSTERIZATION, TagId.POST_APOCALYPTIC),
    ),
    TagAssignment(
        # The Master of Diabolism (37208, 38450, 40434, 40435).
        anime_ids=(37208, 38450, 40434, 40435),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Wo de Tian Jie Nu You (36455).
        anime_ids=(36455,),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Douluo Dalu (37150, 37822, 51836, 61748), Xingchen Bian (38491, 41528),
        # Fanren Xiu Xian Zhuan (41219), Wu Dong Qian Kun (42266, 60541), Jue Shi Wu Hun (43626),
        # Shen Wu Tianzun (59327), Ling Wu Dalu (59410), Man Huang Xian Jie (59951),
        # Jiang Ye (60571), Mo Tian Ji (61566).
        anime_ids=(
            37150,
            37822,
            51836,
            61748,
            38491,
            41528,
            41219,
            42266,
            60541,
            43626,
            59327,
            59410,
            59951,
            60571,
            61566,
        ),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Wo de Tian Jie Nu You (36455), Chuan Shu Zijiu Zhinan (38990), Shanhe Jian Xin (44196),
        # Da Wang Rao Ming (44406, 60597), Shendao Dizun (59915), Tianming Da Zhuzai (60766),
        # Taigu Zhan Hun (61420), Tianyuan (61612), Wan Ren Zhi Shang (61642), Shuangsheng Wu Hun (61657).
        anime_ids=(36455, 38990, 44196, 44406, 60597, 59915, 60766, 61420, 61612, 61642, 61657),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Dororo adaptations (5760, 37520).
        anime_ids=(5760, 37520),
        tag_ids=(TagId.MONSTER_HUNTING, TagId.MONSTERIZATION),
    ),
    TagAssignment(
        # Naruto/Boruto (20, 442, 936, 1735, 2144, 2472, 4437,
        # 6325, 8246, 10589, 10659, 10686, 12979, 13667, 16870, 28755, 34566,
        # 54687, 54688), Shinobi no Ittoki (51098), Basilisk (67, 35964).
        anime_ids=(
            20,
            442,
            936,
            1735,
            2144,
            2472,
            4437,
            6325,
            8246,
            10589,
            10659,
            10686,
            12979,
            13667,
            16870,
            28755,
            34566,
            54687,
            54688,
            51098,
            67,
            35964,
        ),
        tag_ids=(TagId.NINJA,),
    ),
    TagAssignment(
        # Ninja Scroll (617, 618), Nabari no Ou (3655), Ninja vs. Gokudo (61067),
        # Flame of Recca (238), Ninja Slayer (23605), Ninja Kamui (56285), Under Ninja
        # (49766), Brave 10 (11241), Blackfox (37498), Ninkuu (912), The Dagger of
        # Kamui (496), Jubei-chan (635), Laughing Under the Clouds (21743), Batman
        # Ninja (36517), Ninja Girl & Samurai Master (32829, 34978), Ninja Collection
        # (42260), Black Torch (61169), Himawari! (910).
        anime_ids=(
            617,
            618,
            3655,
            61067,
            238,
            23605,
            56285,
            49766,
            11241,
            37498,
            912,
            496,
            635,
            21743,
            36517,
            32829,
            34978,
            42260,
            61169,
            910,
        ),
        tag_ids=(TagId.NINJA,),
    ),
    TagAssignment(
        # Kagaku Ninja-tai Gatchaman (2389); Ninja Senshi Tobikage (3059); Gatchaman Movie (3153).
        anime_ids=(2389, 3059, 3153),
        tag_ids=(TagId.NINJA,),
    ),
    TagAssignment(
        # Kuroko's Basketball (11771, 16894, 24415, 31658, 32869, 32870, 32871),
        # Ahiru no Sora (37403).
        anime_ids=(11771, 16894, 24415, 31658, 32869, 32870, 32871, 37403),
        tag_ids=(TagId.BASKETBALL,),
    ),
    TagAssignment(
        # Blue Lock (49596, 54865, 54866, 60076, 60775, 62589), Inazuma Eleven
        # (5231, 9032, 10507, 10999, 13261, 15785, 18097, 24347, 33733, 34178,
        # 38235, 59709, 59710), Aoashi (49052, 61603), Captain Tsubasa
        # (1614, 1674, 2116, 2118, 2119, 2120, 2121, 36934, 54803), Days (32494).
        anime_ids=(
            49596,
            54865,
            54866,
            60076,
            60775,
            62589,
            5231,
            9032,
            10507,
            10999,
            13261,
            15785,
            18097,
            24347,
            33733,
            34178,
            38235,
            59709,
            59710,
            49052,
            61603,
            1614,
            1674,
            2116,
            2118,
            2119,
            2120,
            2121,
            36934,
            54803,
            32494,
        ),
        tag_ids=(TagId.SOCCER,),
    ),
    TagAssignment(
        # Baby Steps (21185, 27663), The Prince of Tennis (22, 814, 815, 11371,
        # 38882, 41842, 50099, 55570), Aim for the Ace! (311, 313, 8542).
        anime_ids=(
            21185,
            27663,
            22,
            814,
            815,
            11371,
            38882,
            41842,
            50099,
            55570,
            311,
            313,
            8542,
        ),
        tag_ids=(TagId.TENNIS,),
    ),
    TagAssignment(
        # Slam Dunk (170, 1764, 1861, 2498, 2499, 45649), Buzzer Beater
        # (406, 2684).
        anime_ids=(170, 1764, 1861, 2498, 2499, 45649, 406, 2684),
        tag_ids=(TagId.BASKETBALL,),
    ),
    TagAssignment(
        # Dear Boys (292).
        anime_ids=(292,),
        tag_ids=(TagId.BASKETBALL,),
    ),
    TagAssignment(
        # Giant Killing (7661).
        anime_ids=(7661,),
        tag_ids=(TagId.SOCCER,),
    ),
    TagAssignment(
        # Baseball series including Major, One Outs, Big Windup!, and Cross Game.
        anime_ids=(627, 558, 1842, 3226, 5028, 5029, 7655, 36565, 40504, 5040, 2159, 7720, 5941),
        tag_ids=(TagId.BASEBALL,),
    ),
    TagAssignment(
        # Whistle! (183).
        anime_ids=(183,),
        tag_ids=(TagId.SOCCER,),
    ),
    TagAssignment(
        # Offside (5200), Soccer Fever (10774), Top Striker (3438), Blue Legend Shoot!
        # (1327, 2682), Fight! Kickers (3053).
        anime_ids=(5200, 10774, 3438, 1327, 2682, 3053),
        tag_ids=(TagId.SOCCER,),
    ),
    TagAssignment(
        # Haikyu!! (20583, 28891, 29755, 30364, 32935, 35110, 35111,
        # 38883, 40776, 52742, 58967).
        anime_ids=(20583, 28891, 29755, 30364, 32935, 35110, 35111, 38883, 40776, 52742, 58967),
        tag_ids=(TagId.VOLLEYBALL,),
    ),
    TagAssignment(
        # 2.43: Seiin High School Boys Volleyball Team (40679), Harukana Receive (35983),
        # Attacker You! (3081, 11919), Attack No.1 (1550).
        anime_ids=(40679, 35983, 3081, 11919, 1550),
        tag_ids=(TagId.VOLLEYBALL,),
    ),
    TagAssignment(
        # Yowamushi Pedal (18179, 24277, 25755, 30413, 30790, 31783, 33302,
        # 35789, 35880, 50552), Over Drive (2112).
        anime_ids=(18179, 24277, 25755, 30413, 30790, 31783, 33302, 35789, 35880, 50552, 2112),
        tag_ids=(TagId.CYCLING,),
    ),
    TagAssignment(
        # Hoop Days (292), Basquash! (5675), Breakers (40850), Basketball Whirlwind
        # (47809, 61475), Left-Hand Layup! (51288, 62338).
        anime_ids=(292, 5675, 40850, 47809, 61475, 51288, 62338),
        tag_ids=(TagId.BASKETBALL,),
    ),
    TagAssignment(
        # Hungry Heart: Wild Striker (17), The Knight in the Area (11697), Galaxy Kickoff!!
        # (12875), Clean Freak! Aoyama-kun (34825), Futsal Boys!!!!! (40488), Farewell,
        # My Dear Cramer (42774, 42798), Shoot! Goal to the Future (50379).
        anime_ids=(17, 11697, 12875, 34825, 40488, 42774, 42798, 50379),
        tag_ids=(TagId.SOCCER,),
    ),
    TagAssignment(
        # H2 (386), Touch (1065), Princess Nine (1846), Play Ball (3768), Dokaben (3825),
        # Taishou Baseball Girls (5141), Ace of Diamond (18689, 30230), Battery (32947),
        # Captain (9905).
        anime_ids=(386, 1065, 1846, 3768, 3825, 5141, 18689, 30230, 32947, 9905),
        tag_ids=(TagId.BASEBALL,),
    ),
    TagAssignment(
        # Attack on Tomorrow (4339), Attack No.1 (1970) (9163).
        anime_ids=(4339, 9163),
        tag_ids=(TagId.VOLLEYBALL,),
    ),
    TagAssignment(
        # Minami Kamakura High School Girls Cycling Club (31422).
        anime_ids=(31422,),
        tag_ids=(TagId.CYCLING,),
    ),
    TagAssignment(
        # Ao no Hako (57181, 61323), also known as Blue Box.
        anime_ids=(57181, 61323),
        tag_ids=(TagId.BADMINTON, TagId.BASKETBALL),
    ),
    TagAssignment(
        # Hanebado! (37259), Ryman's Club (50185), and Love All Play (49556).
        anime_ids=(37259, 50185, 49556),
        tag_ids=(TagId.BADMINTON,),
    ),
    TagAssignment(
        # TAMAYOMI: The Baseball Girls (39966).
        anime_ids=(39966,),
        tag_ids=(TagId.BASEBALL,),
    ),
    TagAssignment(
        # Free!: Free! (18507), Eternal Summer (22265), Starting Days (30415),
        # Timeless Medley films (33845, 35191), Take Your Marks (35198), Dive to the Future
        # (36704), Road to the World (39014), and The Final Stroke films (38400, 48830).
        anime_ids=(18507, 22265, 30415, 33845, 35191, 35198, 36704, 39014, 38400, 48830),
        tag_ids=(TagId.SWIMMING,),
    ),
    TagAssignment(
        # Sabikui Bisco (48414, 56008), Trigun (6), Fist of the North Star entries
        # (967, 4549, 56646, 62987), Casshern Sins (4981), and Blame! (32086).
        anime_ids=(48414, 56008, 6, 967, 4549, 56646, 62987, 4981, 32086),
        tag_ids=(TagId.POST_APOCALYPTIC,),
    ),
    TagAssignment(
        # Planetarian: Storyteller of the Stars (33190), Girls' Last Tour (35838),
        # NieR:Automata Ver1.1a (51105), Sand Land (53882), and Touring After the Apocalypse (61072).
        anime_ids=(33190, 35838, 51105, 53882, 61072),
        tag_ids=(TagId.POST_APOCALYPTIC,),
    ),
    TagAssignment(
        # Rokka no Yuusha (28497), Subete ga F ni Naru (28621), and Death Note (1535, 2994).
        anime_ids=(28497, 28621, 1535, 2994),
        tag_ids=(TagId.SOCIAL_DEDUCTION,),
    ),
    TagAssignment(
        # Classroom of the Elite (35507, 51096, 51180, 59708, 64463).
        anime_ids=(35507, 51096, 51180, 59708, 64463),
        tag_ids=(TagId.SOCIAL_DEDUCTION,),
    ),
    TagAssignment(
        # Danganronpa (16592, 32189, 33028).
        anime_ids=(16592, 32189, 33028),
        tag_ids=(TagId.SOCIAL_DEDUCTION,),
    ),
    TagAssignment(
        # Tomodachi Game (50273), Talentless Nana (41619), and The Ones Within (37926).
        anime_ids=(50273, 41619, 37926),
        tag_ids=(TagId.SOCIAL_DEDUCTION,),
    ),
    TagAssignment(
        # Gnosia (60427).
        anime_ids=(60427,),
        tag_ids=(TagId.SOCIAL_DEDUCTION, TagId.TIME_LOOP),
    ),
    TagAssignment(
        # Erased (31043).
        anime_ids=(31043,),
        tag_ids=(TagId.REGRESSION,),
    ),
    TagAssignment(
        # Tokyo Revengers (42249, 50608, 54918, 59088), Steins;Gate (9253), The Girl Who Leapt Through Time (2236).
        anime_ids=(42249, 50608, 54918, 59088, 9253, 2236),
        tag_ids=(TagId.TIME_LEAP,),
    ),
    TagAssignment(
        # Kaiji (3002, 10271) and Kakegurui (34933, 37086, 50339).
        anime_ids=(3002, 10271, 34933, 37086, 50339),
        tag_ids=(TagId.GAMBLING,),
    ),
    TagAssignment(
        # Akagi (658), One Outs (5040), Tetsuya (3369), Pachislo Kizoku Gin (7960),
        # Death Parade (28223), Bus Gamer (3389), and Touhai (57796).
        anime_ids=(658, 5040, 3369, 7960, 28223, 3389, 57796),
        tag_ids=(TagId.GAMBLING,),
    ),
    TagAssignment(
        # Mardock Scramble trilogy (8100, 10624, 12053).
        anime_ids=(8100, 10624, 12053),
        tag_ids=(TagId.GAMBLING,),
    ),
    TagAssignment(
        # Liar Game (62331).
        anime_ids=(62331,),
        tag_ids=(TagId.GAMBLING,),
    ),
    TagAssignment(
        # Tomodachi Game (50273).
        anime_ids=(50273,),
        tag_ids=(TagId.GAMBLING,),
    ),
    TagAssignment(
        # Legend of the Galactic Heroes: Die Neue These (31433, 36369, 36370,
        # 36371, 42886, 51805).
        anime_ids=(31433, 36369, 36370, 36371, 42886, 51805),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Code Geass original and recap films (1575, 2904, 34438, 34439, 34440).
        anime_ids=(1575, 2904, 34438, 34439, 34440),
        tag_ids=(TagId.POLITICS, TagId.REVENGE, TagId.REBELLION),
    ),
    TagAssignment(
        # Code Geass: Akito the Exiled entries (8888, 15197, 15199, 15201, 30711).
        anime_ids=(8888, 15197, 15199, 15201, 30711),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Code Geass: Lelouch of the Re;surrection (34437).
        anime_ids=(34437,),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Code Geass: Rozé of the Recapture (56835).
        anime_ids=(56835,),
        tag_ids=(TagId.POLITICS, TagId.REBELLION),
    ),
    TagAssignment(
        # Gundam F91 (88); Mobile Suit Gundam I (1090); Romeo x Juliet (1699);
        # Taiyou no Kiba Dougram (2257); Juusenki L-Gaim (2598).
        anime_ids=(88, 1090, 1699, 2257, 2598),
        tag_ids=(TagId.REBELLION,),
    ),
    TagAssignment(
        # Blue Exorcist meaningful (9919, 11737, 33506, 53889, 58516, 59226).
        anime_ids=(9919, 11737, 33506, 53889, 58516, 59226),
        tag_ids=(TagId.EXORCISM,),
    ),
    TagAssignment(
        # Twin Star Exorcists (32105) and D.Gray-man (1482, 32370).
        anime_ids=(32105, 1482, 32370),
        tag_ids=(TagId.EXORCISM,),
    ),
    TagAssignment(
        # Haunted Junction (646); Honoo no Mirage (1019); Kishin Douji Zenki (1573);
        # Jigoku Sensei Nube (2012); Mononoke (2246); GS Mikami (2400); GS Mikami: Gokuraku Daisakusen!! (3037).
        anime_ids=(646, 1019, 1573, 2012, 2246, 2400, 3037),
        tag_ids=(TagId.EXORCISM,),
    ),
    TagAssignment(
        # Shounen Onmyouji (1557); Tokyo Ravens (16011); Garo: Guren no Tsuki (28537);
        # Onmyouji (53151); Saikyou Onmyouji no Isekai Tenseiki (50932);
        # Onmyou Kaiten Re:Birth (61150); Jipin Tian Shi (62781).
        anime_ids=(1557, 16011, 28537, 50932, 53151, 61150, 62781),
        tag_ids=(TagId.EXORCISM,),
    ),
    TagAssignment(
        # Jujutsu Kaisen (40748, 48561, 51009, 57658, 59654, 63824).
        anime_ids=(40748, 48561, 51009, 57658, 59654, 63824),
        tag_ids=(TagId.EXORCISM,),
    ),
    TagAssignment(
        # Mob Psycho 100 (32182, 37510, 50172).
        anime_ids=(32182, 37510, 50172),
        tag_ids=(TagId.EXORCISM,),
    ),
    TagAssignment(
        # Dandadan (57334, 60543, 62516).
        anime_ids=(57334, 60543, 62516),
        tag_ids=(TagId.EXORCISM, TagId.PSYCHIC, TagId.TRANSFORMATION),
    ),
    TagAssignment(
        # D.N.Angel (61); Akazukin Chacha (103); Viewtiful Joe (278);
        # Mahou no Princess Minky Momo (518); Bishoujo Senshi Sailor Moon (530);
        # Futari wa Precure (603); Digimon Frontier (1132).
        anime_ids=(61, 103, 278, 518, 530, 603, 1132),
        tag_ids=(TagId.TRANSFORMATION,),
    ),
    TagAssignment(
        # Nurarihyon no Mago (7592, 10049).
        anime_ids=(7592, 10049),
        tag_ids=(TagId.TRANSFORMATION,),
    ),
    TagAssignment(
        # Mob Psycho 100 (32182, 37510, 50172), Akira (47), and From the New World (13125).
        anime_ids=(32182, 37510, 50172, 47, 13125),
        tag_ids=(TagId.PSYCHIC,),
    ),
    TagAssignment(
        # Elfen Lied (226).
        anime_ids=(226,),
        tag_ids=(TagId.PSYCHIC,),
    ),
    TagAssignment(
        # Akira (47).
        anime_ids=(47,),
        tag_ids=(TagId.POST_APOCALYPTIC,),
    ),
    TagAssignment(
        # Wonderful Days (548); Hokuto no Ken (967); Kikou Souseiki Mospeada (3670);
        # Koukaku no Regios (4186); Shangri-La (5220); Evangelion: 3.0 (3785).
        anime_ids=(548, 967, 3670, 3785, 4186, 5220),
        tag_ids=(TagId.POST_APOCALYPTIC,),
    ),
    TagAssignment(
        # Mirai Shounen Conan (302).
        anime_ids=(302,),
        tag_ids=(TagId.POST_APOCALYPTIC,),
    ),
    TagAssignment(
        # Cyberpunk: Edgerunners (42310); Ghost in the Shell (43); Stand Alone Complex (467, 801);
        # Psycho-Pass (13601); Ergo Proxy (790); Serial Experiments Lain (339); Texhnolyze (26);
        # Mardock Scramble (8100, 10624, 12053); BLAME! Movie (32086); Armitage III (492, 493);
        # Appleseed (54, 2969, 22677).
        anime_ids=(
            26,
            43,
            54,
            339,
            39539,
            40529,
            467,
            492,
            493,
            790,
            801,
            2969,
            8100,
            10624,
            12053,
            13601,
            22677,
            32086,
            42310,
        ),
        tag_ids=(TagId.CYBERPUNK,),
    ),
    TagAssignment(
        # The Disastrous Life of Saiki K. (33255, 34612, 40542).
        anime_ids=(33255, 34612, 40542),
        tag_ids=(TagId.PSYCHIC,),
    ),
    TagAssignment(
        # A Certain Magical Index entries (4654, 8937, 11743, 36432) and
        # A Certain Scientific Railgun entries (6213, 16049, 38481, 61012).
        anime_ids=(4654, 8937, 11743, 36432, 6213, 16049, 38481, 61012),
        tag_ids=(TagId.PSYCHIC,),
    ),
    TagAssignment(
        # Assassination Classroom (24833, 30654).
        anime_ids=(24833, 30654),
        tag_ids=(TagId.ASSASSIN,),
    ),
    TagAssignment(
        # Phantom: Requiem for the Phantom (5682).
        anime_ids=(5682,),
        tag_ids=(TagId.ASSASSIN,),
    ),
    TagAssignment(
        # Black Cat (68); Gunslinger Girl (134); Noir (272); Weiss Kreuz (447); Kamui no Ken (496).
        anime_ids=(68, 134, 272, 447, 496),
        tag_ids=(TagId.ASSASSIN,),
    ),
    TagAssignment(
        # Akame ga Kill! (22199): Night Raid, political uprising, and regime change.
        anime_ids=(22199,),
        tag_ids=(TagId.ASSASSIN, TagId.POLITICS, TagId.REBELLION),
    ),
    TagAssignment(
        # Spy Classroom (51252, 54947), Spy x Family (50265, 50602, 53887,
        # 53888, 59027), and Joker Game (31405).
        anime_ids=(51252, 54947, 50265, 50602, 53887, 53888, 59027, 31405),
        tag_ids=(TagId.ESPIONAGE,),
    ),
    TagAssignment(
        # Princess Principal (35240, 37807, 41140, 41141, 57093, 57094, 57095).
        anime_ids=(35240, 37807, 41140, 41141, 57093, 57094, 57095),
        tag_ids=(TagId.ESPIONAGE,),
    ),
    TagAssignment(
        # Golden Kamuy (36028, 37989, 40059, 50528, 55772).
        anime_ids=(36028, 37989, 40059, 50528, 55772),
        tag_ids=(TagId.TREASURE_HUNTING,),
    ),
    TagAssignment(
        # One Piece main series and meaningful films (21, 459, 460, 461, 462, 463, 464, 465,
        # 2107, 3848, 4155, 12859, 31490, 38234, 50410, 64858, 64859).
        anime_ids=(21, 459, 460, 461, 462, 463, 464, 465, 2107, 3848, 4155, 12859, 31490, 38234, 50410, 64858, 64859),
        tag_ids=(TagId.TREASURE_HUNTING, TagId.PIRATES),
    ),
    TagAssignment(
        # Tanken Driland (14333); Dragon Collection (22733); Bogeul Bogeul Bomulseon (29886);
        # Xiong Chumo: Qihuan Kongjian (37100); Meitantei Conan Movie 27 (56785).
        anime_ids=(14333, 22733, 29886, 37100, 56785),
        tag_ids=(TagId.TREASURE_HUNTING,),
    ),
    TagAssignment(
        # Kingdom (12031, 17389, 40682, 50160, 53223, 61517).
        anime_ids=(12031, 17389, 40682, 50160, 53223, 61517),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # The Genius Prince's Guide (47159), How a Realist Hero Rebuilt the Kingdom (41710, 49930),
        # The Twelve Kingdoms (153), and Yona of the Dawn (25013).
        anime_ids=(47159, 41710, 49930, 153, 25013),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # That Time I Got Reincarnated as a Slime (37430).
        anime_ids=(37430,),
        tag_ids=(TagId.POLITICS, TagId.SYSTEM),
    ),
    TagAssignment(
        # Solo Leveling (52299, 58567, 59841, 64546).
        anime_ids=(52299, 58567, 59841, 64546),
        tag_ids=(TagId.SYSTEM, TagId.LEVELING, TagId.DUNGEON, TagId.NECROMANCY),
    ),
    TagAssignment(
        # Sword Art Online (11757).
        anime_ids=(11757,),
        tag_ids=(TagId.LEVELING, TagId.DUNGEON, TagId.VIRTUAL_REALITY),
    ),
    TagAssignment(
        # Sword Art Online Alternative: Gun Gale Online (36475, 55994).
        # Shangri-La Frontier (52347, 58572, 61338), and BOFURI (38790, 41514).
        anime_ids=(36475, 55994, 52347, 58572, 61338, 38790, 41514),
        tag_ids=(TagId.VIRTUAL_REALITY,),
    ),
    TagAssignment(
        # .hack//Sign (48); .hack//Tasogare no Udewa Densetsu (298); .hack//Roots (873);
        # Dragon Drive (296); Log Horizon (17265); Detective Conan Movie 6 (1365).
        anime_ids=(48, 296, 298, 873, 1365, 17265),
        tag_ids=(TagId.VIRTUAL_REALITY,),
    ),
    TagAssignment(
        # Dennou Coil (2164), Sword Art Online the Movie: Ordinal Scale (31765), and
        # Yurei Deco (51092).
        anime_ids=(2164, 31765, 51092),
        tag_ids=(TagId.AUGMENTED_REALITY,),
    ),
    TagAssignment(
        # The King's Avatar: main series and meaningful film entries
        # (33926, 37932, 40080, 49559, 62244).
        anime_ids=(33926, 37932, 40080, 49559, 62244),
        tag_ids=(TagId.ESPORTS,),
    ),
    TagAssignment(
        # Bokura no Ame-iro Protocol (55894); Cheng Ye Xiao He (61634).
        anime_ids=(55894, 61634),
        tag_ids=(TagId.ESPORTS,),
    ),
    TagAssignment(
        # The Silver Guardian (32936, 35757).
        anime_ids=(32936, 35757),
        tag_ids=(TagId.DUNGEON, TagId.VIRTUAL_REALITY),
    ),
    TagAssignment(
        # GATE: Thus the JSDF Fought There! (28907).
        anime_ids=(28907,),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Pokémon TV (527, 1564, 1565, 9107, 14093, 17115, 17873,
        # 19291, 31592, 34034, 40351, 53874, 53876).
        anime_ids=(527, 1564, 1565, 9107, 14093, 17115, 17873, 19291, 31592, 34034, 40351, 53874, 53876),
        tag_ids=(TagId.CREATURE_TAMING,),
    ),
    TagAssignment(
        # Digimon TV (552, 1313, 859, 1132, 8624, 10444, 11385,
        # 33314, 41074, 49515, 61269).
        anime_ids=(552, 1313, 859, 1132, 8624, 10444, 11385, 33314, 41074, 49515, 61269),
        tag_ids=(TagId.CREATURE_TAMING,),
    ),
    TagAssignment(
        # Dinosaur King TV (3576, 5725).
        anime_ids=(3576, 5725),
        tag_ids=(TagId.CREATURE_TAMING,),
    ),
    TagAssignment(
        # Hunter x Hunter entries (136, 11061) and JoJo's Bizarre Adventure entries
        # (14719, 20899, 26055, 31933, 37991, 48661, 51367, 53273, 61469).
        anime_ids=(136, 11061, 14719, 20899, 26055, 31933, 37991, 48661, 51367, 53273, 61469),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # Jujutsu Kaisen entries (40748, 48561, 51009, 57658, 59654, 63824).
        anime_ids=(40748, 48561, 51009, 57658, 59654, 63824),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # Bungo Stray Dogs entries (31478, 32867, 34944, 38003, 50330, 54898).
        anime_ids=(31478, 32867, 34944, 38003, 50330, 54898),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # My Hero Academia entries (31964, 33486, 36456, 36896, 38408, 39565, 41587,
        # 44200, 49918, 54789, 56196, 60098).
        anime_ids=(31964, 33486, 36456, 36896, 38408, 39565, 41587, 44200, 49918, 54789, 56196, 60098),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # My Hero Academia (31964, 33486, 36456, 36896, 38408, 39565,
        # 41587, 44200, 49918, 54789, 56196, 60098).
        anime_ids=(31964, 33486, 36456, 36896, 38408, 39565, 41587, 44200, 49918, 54789, 56196, 60098),
        tag_ids=(TagId.SUPERHERO,),
    ),
    TagAssignment(
        # Tiger & Bunny (9941, 12015, 12017, 41595, 52291); One Punch Man (30276, 34134, 52807, 63193);
        # The Reflection (34449); SHY (53237); Zetman (11837).
        anime_ids=(9941, 11837, 12015, 12017, 30276, 34134, 34449, 41595, 52291, 52807, 53237, 63193),
        tag_ids=(TagId.SUPERHERO,),
    ),
    TagAssignment(
        # Zatch Bell! (250).
        anime_ids=(250,),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # Undead Unluck entries (52741, 63177).
        anime_ids=(52741, 63177),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # Reborn! (1604).
        anime_ids=(1604,),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # Busou Renkin (1536); Kekkaishi (1606); Darker than Black (2025); Yozakura Quartet (4548).
        anime_ids=(1536, 1606, 2025, 4548),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # Soul Eater (3588): DWMA teams hunt corrupted souls and combat supernatural threats.
        anime_ids=(3588,),
        tag_ids=(TagId.ABILITY_BATTLES, TagId.MONSTER_HUNTING),
    ),
    TagAssignment(
        # Gachiakuta (59062).
        anime_ids=(59062,),
        tag_ids=(TagId.ABILITY_BATTLES, TagId.MONSTER_HUNTING),
    ),
    TagAssignment(
        # Berserk core adaptations (33, 10218, 12113, 12115, 32379, 34055, 52976).
        anime_ids=(33, 10218, 12113, 12115, 32379, 34055, 52976),
        tag_ids=(TagId.REVENGE, TagId.MONSTER_HUNTING),
    ),
    TagAssignment(
        # Claymore (1818).
        anime_ids=(1818,),
        tag_ids=(TagId.MONSTERIZATION, TagId.MONSTER_HUNTING, TagId.REVENGE),
    ),
    TagAssignment(
        # The Kingdoms of Ruin (54362).
        anime_ids=(54362,),
        tag_ids=(TagId.REVENGE, TagId.ABILITY_BATTLES, TagId.POLITICS),
    ),
    TagAssignment(
        # Magi: The Labyrinth of Magic (14513).
        anime_ids=(14513,),
        tag_ids=(TagId.ABILITY_BATTLES, TagId.DUNGEON),
    ),
    TagAssignment(
        # Magi: The Kingdom of Magic (18115), Magi: Sinbad no Bouken (31741).
        anime_ids=(18115, 31741),
        tag_ids=(TagId.ABILITY_BATTLES, TagId.DUNGEON),
    ),
    TagAssignment(
        # Arifureta (36882, 40507).
        anime_ids=(36882, 40507),
        tag_ids=(TagId.DUNGEON,),
    ),
    TagAssignment(
        # Cardfight!! Vanguard (9539, 13145, 15611, 21729, 23991, 27815, 31196, 32802, 34077, 36022, 37476, 39244,
        # 40167, 41283, 42516, 48862, 49819, 49820, 52079, 54142, 54143, 54144, 54145, 62649, 63938),
        # Selector WIXOSS (22273, 24037, 31280, 33197, 34607, 41521), Shadowverse (40506, 50060, 54854, 57614),
        # Build Divide (48776, 48777), Yu-Gi-Oh! (550, 481, 482, 1894, 2006, 3972, 6951, 10015, 15489,
        # 21639, 28771, 34866, 40145, 50607).
        anime_ids=(
            9539,
            13145,
            15611,
            21729,
            23991,
            27815,
            31196,
            32802,
            34077,
            36022,
            37476,
            39244,
            40167,
            41283,
            42516,
            48862,
            49819,
            49820,
            52079,
            54142,
            54143,
            54144,
            54145,
            62649,
            63938,
            22273,
            24037,
            31280,
            33197,
            34607,
            41521,
            40506,
            50060,
            54854,
            57614,
            48776,
            48777,
            550,
            481,
            482,
            1894,
            2006,
            3972,
            6951,
            10015,
            15489,
            21639,
            28771,
            34866,
            40145,
            50607,
        ),
        tag_ids=(TagId.CARD_BATTLING,),
    ),
    TagAssignment(
        # Duel Masters (1685, 4443, 4444); Bakugan Battle Brawlers (2156, 5337, 7334, 10330).
        anime_ids=(1685, 2156, 4443, 4444, 5337, 7334, 10330),
        tag_ids=(TagId.CARD_BATTLING,),
    ),
    TagAssignment(
        # High Card (49154, 54869, 58531).
        anime_ids=(49154, 54869, 58531),
        tag_ids=(TagId.ABILITY_BATTLES,),
    ),
    TagAssignment(
        # Lupin III (1412, 1425, 1426, 1416, 1419, 1430, 1432, 1433,
        # 1435, 18429, 27947, 35857, 40082, 49040, 53109).
        anime_ids=(1412, 1425, 1426, 1416, 1419, 1430, 1432, 1433, 1435, 18429, 27947, 35857, 40082, 49040, 53109),
        tag_ids=(TagId.HEIST,),
    ),
    TagAssignment(
        # Great Pretender and Razbliuto (40052, 57184), Magic Kaito 1412 (25517), and Cat's Eye (2043).
        anime_ids=(40052, 57184, 25517, 2043),
        tag_ids=(TagId.HEIST,),
    ),
    TagAssignment(
        # Outbreak Company (19369).
        anime_ids=(19369,),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Overlord (29803, 35073, 37675, 48895).
        anime_ids=(29803, 35073, 37675, 48895),
        tag_ids=(TagId.POLITICS, TagId.NATION_BUILDING, TagId.NECROMANCY),
    ),
    TagAssignment(
        # That Time I Got Reincarnated as a Slime (37430).
        anime_ids=(37430,),
        tag_ids=(TagId.NATION_BUILDING,),
    ),
    TagAssignment(
        # How a Realist Hero Rebuilt the Kingdom (41710, 49930).
        anime_ids=(41710, 49930),
        tag_ids=(TagId.NATION_BUILDING,),
    ),
    TagAssignment(
        # Re:Zero (31240, 36286, 38414, 39587, 42203, 54857, 61316) and
        # Summer Time Rendering (47194)..
        anime_ids=(31240, 36286, 38414, 39587, 42203, 54857, 61316, 47194),
        tag_ids=(TagId.TIME_LOOP,),
    ),
    TagAssignment(
        # Higurashi no Naku Koro ni Kai (1889).
        anime_ids=(1889,),
        tag_ids=(TagId.TIME_LOOP,),
    ),
    TagAssignment(
        # Golden Time (17895), Amnesia (15085), One Week Friends (21327),
        # ef: A Tale of Memories (2924), Tasogare Otome x Amnesia (12445), and Kanon (1530).
        anime_ids=(17895, 15085, 21327, 2924, 12445, 1530),
        tag_ids=(TagId.MEMORY_LOSS,),
    ),
    TagAssignment(
        # Tsurune (36653, 43556, 52826).
        anime_ids=(36653, 43556, 52826),
        tag_ids=(TagId.ARCHERY,),
    ),
    TagAssignment(
        # Fusha no Sha (7477); Kaichuu! (9205).
        anime_ids=(7477, 9205),
        tag_ids=(TagId.ARCHERY,),
    ),
    TagAssignment(
        # Kaze ga Tsuyoku Fuiteiru (37965), Prince of Stride (31559).
        anime_ids=(37965, 31559),
        tag_ids=(TagId.RUNNING,),
    ),
    TagAssignment(
        # Eyeshield 21 (15).
        anime_ids=(15,),
        tag_ids=(TagId.AMERICAN_FOOTBALL,),
    ),
    TagAssignment(
        # All Out!! (31588).
        # Try Knights (39527); number24 (39583).
        anime_ids=(31588, 39527, 39583),
        tag_ids=(TagId.RUGBY,),
    ),
    TagAssignment(
        # Dead Mount Death Play (53613, 54743).
        anime_ids=(53613, 54743),
        tag_ids=(TagId.NECROMANCY,),
    ),
    TagAssignment(
        # Haibane Renmei (387).
        anime_ids=(387,),
        tag_ids=(TagId.MEMORY_LOSS,),
    ),
    TagAssignment(
        # .hack//Sign (48); El Cazador de la Bruja (2030); Shinseikiden Mars (1712).
        anime_ids=(48, 1712, 2030),
        tag_ids=(TagId.MEMORY_LOSS,),
    ),
    TagAssignment(
        # Tomb Raider King (63316).
        anime_ids=(63316,),
        tag_ids=(TagId.DUNGEON, TagId.REGRESSION, TagId.REVENGE, TagId.TREASURE_HUNTING),
    ),
    TagAssignment(
        # Lord of Mysteries (49818).
        anime_ids=(49818,),
        tag_ids=(TagId.ABILITY_BATTLES, TagId.LEVELING),
    ),
    TagAssignment(
        # Master of Epic: The Animation Age (1885).
        anime_ids=(1885,),
        tag_ids=(TagId.LEVELING,),
    ),
    TagAssignment(
        # Ranking of Kings (40834).
        anime_ids=(40834,),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Tenmaku no Jaadugar (61483).
        anime_ids=(61483,),
        tag_ids=(TagId.POLITICS, TagId.REVENGE),
    ),
    TagAssignment(
        # Nippon Sangoku (63375).
        anime_ids=(63375,),
        tag_ids=(TagId.POLITICS, TagId.NATION_BUILDING, TagId.POST_APOCALYPTIC),
    ),
    TagAssignment(
        # Peace Maker Kurogane (161); Jigoku Shoujo (228); Gankutsuou (239);
        # Escaflowne (393); Tokkou (916).
        anime_ids=(161, 228, 239, 393, 916),
        tag_ids=(TagId.REVENGE,),
    ),
    TagAssignment(
        # Arslan Senki (28249, 31821).
        anime_ids=(28249, 31821),
        tag_ids=(TagId.POLITICS, TagId.REBELLION),
    ),
    TagAssignment(
        # Tearmoon Empire (52962), Tsuyokute New Saga (53397), Yarinaoshi Reijou (55150).
        anime_ids=(52962, 53397, 55150),
        tag_ids=(TagId.REGRESSION,),
    ),
    TagAssignment(
        # Hajime no Ippo (263, 5258, 19647), Ashita no Joe (2402, 2920, 2921, 2922),
        # Megalo Box (36563, 40729), Eiji (6076), Ring ni Kakero 1 (23), Ganbare Genki (3213), Levius (39574).
        anime_ids=(263, 5258, 19647, 2402, 2920, 2921, 2922, 36563, 40729, 6076, 23, 3213, 39574),
        tag_ids=(TagId.BOXING,),
    ),
    TagAssignment(
        # Ping Pong the Animation (22135), Shakunetsu no Takkyuu Musume (33031), Baise Shandian (51333, 64653).
        anime_ids=(22135, 33031, 51333, 64653),
        tag_ids=(TagId.TABLE_TENNIS,),
    ),
    TagAssignment(
        # Yuri!!! on Ice (32995), Ginban Kaleidoscope (476), Medalist (55318, 61335),
        # Skate-Leading Stars (40786), Pretty Rhythm: Aurora Dream (10257).
        anime_ids=(32995, 476, 55318, 61335, 40786, 10257),
        tag_ids=(TagId.FIGURE_SKATING,),
    ),
    TagAssignment(
        # Fate/Zero (10087), Fate/stay night (356, 22297, 28701), Fate/Apocrypha (34662),
        # Mirai Nikki (10620), Btooom! (14345), Juuni Taisen (35076), Basilisk (67),
        # Xue Se Cang Qiong (36762), Dansai Bunri no Crime Edge (16355), Mahou Shoujo Ikusei Keikaku (33003).
        anime_ids=(10087, 356, 22297, 28701, 34662, 10620, 14345, 35076, 67, 36762, 16355, 33003),
        tag_ids=(TagId.BATTLE_ROYALE,),
    ),
    TagAssignment(
        # Cowboy Bebop (1), Black Cat (68), Seihou Bukyou Outlaw Star (400),
        # Solty Rei (152), Porco Rosso (416), El Cazador de la Bruja (2030), Hyper Police (1180).
        anime_ids=(1, 68, 400, 152, 416, 2030, 1180),
        tag_ids=(TagId.BOUNTY_HUNTER,),
    ),
    TagAssignment(
        # Natsume Yuujinchou (4081, 5300, 10379, 11665, 32983, 34591, 36538, 42894, 55823),
        # Mononoke (2246), Mushishi (457), Kamisama Hajimemashita (14713, 25681), Nurarihyon no Mago (7592),
        # Princess Mononoke (164), Kekkaishi (1606), Tenpou Ibun: Ayakashi Ayashi (1587),
        # Shounen Onmyouji (1557), Dororon Enma-kun (1337), Gegege no Kitarou (2165, 37140).
        anime_ids=(
            4081,
            5300,
            10379,
            11665,
            32983,
            34591,
            36538,
            42894,
            55823,
            2246,
            457,
            14713,
            25681,
            7592,
            164,
            1606,
            1587,
            1557,
            1337,
            2165,
            37140,
        ),
        tag_ids=(TagId.YOKAI,),
    ),
    TagAssignment(
        # Last Exile (97, 10336), Steamboy (565), Princess Principal (35240), Koutetsujou no Kabaneri (28623),
        # Sakura Wars (561), Clockwork Planet (32407), Karakuri Kiden: Hiwou Senki (3935).
        anime_ids=(97, 10336, 565, 35240, 28623, 561, 32407, 3935),
        tag_ids=(TagId.STEAMPUNK,),
    ),
    TagAssignment(
        # Weiqi Shaonian 2 (19839).
        anime_ids=(19839,),
        tag_ids=(TagId.GO,),
    ),
    TagAssignment(
        # Soredemo Ayumu wa Yosetekuru (45653).
        anime_ids=(45653,),
        tag_ids=(TagId.SHOGI,),
    ),
    TagAssignment(
        # All You Need Is Kill (61192).
        anime_ids=(61192,),
        tag_ids=(TagId.TIME_LOOP,),
    ),
    TagAssignment(
        # Hoshiai no Sora (37972), Tennis no Oujisama Movie 2 (10731).
        anime_ids=(37972, 10731),
        tag_ids=(TagId.TENNIS,),
    ),
    TagAssignment(
        # Rinkai! (54859).
        anime_ids=(54859,),
        tag_ids=(TagId.CYCLING,),
    ),
    TagAssignment(
        # Emerald no Wa (58941).
        anime_ids=(58941,),
        tag_ids=(TagId.BADMINTON,),
    ),
    TagAssignment(
        # Nige Jouzu no Wakagimi (54724).
        anime_ids=(54724,),
        tag_ids=(TagId.ARCHERY,),
    ),
    TagAssignment(
        # Ga-Rei: Zero (4725), D.Gray-man (1482), Fukigen na Mononokean (32696), Kyoukai no Rinne (28423).
        anime_ids=(4725, 1482, 32696, 28423),
        tag_ids=(TagId.EXORCISM,),
    ),
    TagAssignment(
        # Your Name. (32281), Kokoro Connect (11887), Yamada-kun to 7-nin no Majo (28677),
        # No Doubt In Us (41221), J<=>M (63697).
        anime_ids=(32281, 11887, 28677, 41221, 63697),
        tag_ids=(TagId.BODY_SWAP,),
    ),
    TagAssignment(
        # Sword Art Online: Alicization (36474), Infinite Dendrogram (38909),
        # Kyuukyoku Shinka shita Full Dive RPG (44276).
        anime_ids=(36474, 38909, 44276),
        tag_ids=(TagId.VIRTUAL_REALITY,),
    ),
    TagAssignment(
        # Accel World (11759), Battle Spirits: Heroes (11017).
        anime_ids=(11759, 11017),
        tag_ids=(TagId.AUGMENTED_REALITY,),
    ),
    TagAssignment(
        # The King's Avatar Specials (37078).
        anime_ids=(37078,),
        tag_ids=(TagId.ESPORTS,),
    ),
    TagAssignment(
        # Saijaku Tamer wa Gomi Hiroi no Tabi wo Hajimemashita. (53590), Merc Storia (37232).
        anime_ids=(53590, 37232),
        tag_ids=(TagId.CREATURE_TAMING,),
    ),
    TagAssignment(
        # Susume, Karolina. (37684).
        anime_ids=(37684,),
        tag_ids=(TagId.SHOGI,),
    ),
    TagAssignment(
        # Teekyuu (15125), Usakame (32454).
        anime_ids=(15125, 32454),
        tag_ids=(TagId.TENNIS,),
    ),
    TagAssignment(
        # PistStar (13359).
        anime_ids=(13359,),
        tag_ids=(TagId.CYCLING,),
    ),
    TagAssignment(
        # Dan Doh!! (234), Pro Golfer Saru (16650), Birdie Wing (50248, 52229),
        # Oi! Tonbo (55194, 59175), Rising Impact (57487), Sorairo Utility (58066).
        anime_ids=(234, 16650, 50248, 52229, 55194, 59175, 57487, 58066),
        tag_ids=(TagId.GOLF,),
    ),
    TagAssignment(
        # Showa Genroku Rakugo Shinju (28735, 33095), Joshiraku (12679),
        # My Master Has No Tail (49533), Akane-banashi (62164), Rakugo Tennyo Oyui (2244).
        anime_ids=(28735, 33095, 12679, 49533, 62164, 2244),
        tag_ids=(TagId.RAKUGO,),
    ),
    TagAssignment(
        # Rainbow (6114), Deadman Wonderland (6880), Nanbaka (30016, 34414),
        # JoJo's Bizarre Adventure: Stone Ocean (48661, 51367),
        # Naruto Shippuden the Movie 5: Blood Prison (10589).
        anime_ids=(6114, 6880, 30016, 34414, 48661, 51367, 10589),
        tag_ids=(TagId.PRISON_SETTING,),
    ),
    TagAssignment(
        # The Wind Rises (16662), Porco Rosso (416), Blue Thermal (49665),
        # The Sky Crawlers (3089), The Princess and the Pilot (9000),
        # The Magnificent Kotobuki (38301), Yomigaeru Sora: Rescue Wings (798).
        anime_ids=(16662, 416, 49665, 3089, 9000, 38301, 798),
        tag_ids=(TagId.AVIATION,),
    ),
    TagAssignment(
        # Nisekoi: False Love (18897, 27787), Oreshura (14749),
        # Wolf Girl & Black Prince (23673).
        anime_ids=(18897, 27787, 14749, 23673),
        tag_ids=(TagId.FAKE_RELATIONSHIP,),
    ),
    TagAssignment(
        # Yawara! (691, 2008), Judo Boy (4439), "Ippon" again! (49376).
        anime_ids=(691, 2008, 4439, 49376),
        tag_ids=(TagId.JUDO,),
    ),
    TagAssignment(
        # Bamboo Blade (2986), My Name Is Teppei (3827), Musashi no Ken (4062).
        anime_ids=(2986, 3827, 4062),
        tag_ids=(TagId.KENDO,),
    ),
    TagAssignment(
        # Fullmetal Alchemist franchise (121, 430, 5114, 9135), Buso Renkin (1536),
        # Atelier Escha & Logy (21167), Atelier Ryza (54760),
        # Management of a Novice Alchemist (49849).
        anime_ids=(121, 430, 5114, 9135, 1536, 21167, 54760, 49849),
        tag_ids=(TagId.ALCHEMY,),
    ),
    TagAssignment(
        # The Empire of Corpses (28625), Throne of Seal: The Crownless God (61508).
        anime_ids=(28625, 61508),
        tag_ids=(TagId.NECROMANCY,),
    ),
    TagAssignment(
        # Kumo Desu ga, Nani ka? (37984).
        anime_ids=(37984,),
        tag_ids=(TagId.SYSTEM, TagId.LEVELING),
    ),
    TagAssignment(
        # BOFURI (38790, 41514).
        anime_ids=(38790, 41514),
        tag_ids=(TagId.SYSTEM, TagId.LEVELING),
    ),
    TagAssignment(
        # Slime Taoshite 300-nen (40586, 50738).
        anime_ids=(40586, 50738),
        tag_ids=(TagId.LEVELING,),
    ),
    TagAssignment(
        # Bokutachi no Remake (40904).
        anime_ids=(40904,),
        tag_ids=(TagId.REGRESSION,),
    ),
    TagAssignment(
        # Fights Break Sphere / Battle Through The Heavens (36491, 36561, 37176,
        # 38436, 39178, 44412, 47548, 49701, 51038, 51039).
        anime_ids=(36491, 36561, 37176, 38436, 39178, 44412, 47548, 49701, 51038, 51039),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Swallowed Star (44218, 49571, 56523, 56524, 59939, 62726).
        anime_ids=(44218, 49571, 56523, 56524, 59939, 62726),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Martial Universe (39024, 49570, 57183, 62249, 62717).
        anime_ids=(39024, 49570, 57183, 62249, 62717),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Stellar Transformation (49386, 50667, 51769, 60787, 62718).
        anime_ids=(49386, 50667, 51769, 60787, 62718),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # A Will Eternal (41923, 49574, 56215, 62248).
        anime_ids=(41923, 49574, 56215, 62248),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Apotheosis (52949, 57264, 62703, 64624).
        anime_ids=(52949, 57264, 62703, 64624),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Perfect World (47405, 58797, 62723).
        anime_ids=(47405, 58797, 62723),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Renegade Immortal (55809, 60279), Shrouding the Heavens (51289, 63606).
        anime_ids=(55809, 60279, 51289, 63606),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Verified standalone and serialized cultivation donghua (42950, 44065,
        # 44073, 45169, 48684, 49742, 49952, 50430, 50521, 50538, 50636, 50925,
        # 51131, 51191, 51390, 51457, 51490, 51898, 52178, 52522, 53618, 54021,
        # 54065, 54123, 54437, 54737, 54931, 55684, 56716, 56717, 56774, 56958,
        # 57469, 57613, 59557, 59593, 59762, 60066, 60233, 60249, 60526, 60574,
        # 60583, 61212, 61565, 61610, 61654, 61659, 61678, 61929, 62262, 62480,
        # 62544, 62659, 62707, 62730, 62742, 62743, 62952, 62954, 62990, 63360,
        # 63416, 63439, 63485, 63995, 64384, 64444, 64450, 64454, 64710, 64738).
        anime_ids=(
            42950,
            44065,
            44073,
            45169,
            48684,
            49742,
            49952,
            50430,
            50521,
            50538,
            50636,
            50925,
            51131,
            51191,
            51390,
            51457,
            51490,
            51898,
            52178,
            52522,
            53618,
            54021,
            54065,
            54123,
            54437,
            54737,
            54931,
            55684,
            56716,
            56717,
            56774,
            56958,
            57469,
            57613,
            59557,
            59593,
            59762,
            60066,
            60233,
            60249,
            60526,
            60574,
            60583,
            61212,
            61565,
            61610,
            61654,
            61659,
            61678,
            61929,
            62262,
            62480,
            62544,
            62659,
            62707,
            62730,
            62742,
            62743,
            62952,
            62954,
            62990,
            63360,
            63416,
            63439,
            63485,
            63995,
            64384,
            64444,
            64450,
            64454,
            64710,
            64738,
        ),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Zombie Land Saga (37976, 40174, 50159), School-Live! (24765),
        # Resident Evil (42976, 54398), Seoul Station (34048),
        # Calamity of the Zombie Girl (37735), My Daughter is a Zombie (51685),
        # Murder Mystery of the Dead (59892), Zombie Brother (30412),
        # Zo Zo Zo Zombie-kun (34817, 41686).
        anime_ids=(
            37976,
            40174,
            50159,
            24765,
            42976,
            54398,
            34048,
            37735,
            51685,
            59892,
            30412,
            34817,
            41686,
        ),
        tag_ids=(TagId.ZOMBIE,),
    ),
    TagAssignment(
        # Space Pirate Captain Harlock (1000), Black Lagoon (889, 1519), Mars Daybreak (1086).
        anime_ids=(1000, 889, 1519, 1086),
        tag_ids=(TagId.PIRATES,),
    ),
    TagAssignment(
        # Cowboy Bebop: The Movie (5), Vampire Hunter D: Bloodlust (543),
        # Rage of Bahamut (21843, 30736), Love of Kill (44516).
        anime_ids=(5, 543, 21843, 30736, 44516),
        tag_ids=(TagId.BOUNTY_HUNTER,),
    ),
    TagAssignment(
        # Darker than Black (2025, 6573), The World's Finest Assassin (47790),
        # Gunslinger Girl (3221), Phantom: Requiem for the Phantom (252),
        # Golgo 13 (4014, 1760), Buddy Daddies (53411), Scissor Seven (38409).
        anime_ids=(2025, 6573, 47790, 3221, 252, 4014, 1760, 53411, 38409),
        tag_ids=(TagId.ASSASSIN,),
    ),
    TagAssignment(
        # Ace of Diamond Act II (38731, 58877, 64505), Oblivion Battery (42829, 56165, 60275),
        # MIX (38098, 52614), Gurazeni (35183, 37990), Cinderella Nine (38091),
        # Star of the Giants / Kyojin no Hoshi (5834, 15875, 16486, 51085),
        # Samurai Giants (9916), Kurokan (29603), Drucker in the Dugout (9693),
        # Tribe Nine (49969).
        anime_ids=(
            38731,
            58877,
            64505,
            42829,
            56165,
            60275,
            38098,
            52614,
            35183,
            37990,
            38091,
            5834,
            15875,
            16486,
            51085,
            9916,
            29603,
            9693,
            49969,
        ),
        tag_ids=(TagId.BASEBALL,),
    ),
    TagAssignment(
        # Ring ni Kakero 1 (1771, 7793, 10346), Rokudenashi Blues (9077),
        # Heavy (10964), Kimi to Fit Boxing (49664).
        anime_ids=(1771, 7793, 10346, 9077, 10964, 49664),
        tag_ids=(TagId.BOXING,),
    ),
    TagAssignment(
        # Akakichi no Eleven (2316), Ashita e Free Kick (3874), Goal Field Hunter (5217),
        # Forza! Hidemaru (18005), Zuqiu Jianghu (45187), Dragon League (5197).
        anime_ids=(2316, 3874, 5217, 18005, 45187, 5197),
        tag_ids=(TagId.SOCCER,),
    ),
    TagAssignment(
        # Hungry Best 5 (16552), Zero Rise (63325).
        anime_ids=(16552, 63325),
        tag_ids=(TagId.BASKETBALL,),
    ),
    TagAssignment(
        # Dan Doh!! (234).
        anime_ids=(234,),
        tag_ids=(TagId.GOLF,),
    ),
    TagAssignment(
        # Sword Oratoria (32887), DanMachi: Arrow of the Orion (37348),
        # Delicious in Dungeon (52701), Dungeon People (56348),
        # Let This Grieving Soul Retire (58172),
        # I Left My A-Rank Party to Help My Former Students Reach the Dungeon Depths! (59730).
        anime_ids=(32887, 37348, 52701, 56348, 58172, 59730),
        tag_ids=(TagId.DUNGEON,),
    ),
    TagAssignment(
        # Let This Grieving Soul Retire (58172).
        anime_ids=(58172,),
        tag_ids=(TagId.TREASURE_HUNTING,),
    ),
    TagAssignment(
        # Sword Art Online Alternative: Gun Gale Online (36475),
        # Shiboyugi: Playing Death Games to Put Food on the Table (59711, 63819).
        anime_ids=(36475, 59711, 63819),
        tag_ids=(TagId.BATTLE_ROYALE,),
    ),
    TagAssignment(
        # Soul Land 2: The Peerless Tang Clan (51836), Necromancer Isekai (57005).
        anime_ids=(51836, 57005),
        tag_ids=(TagId.NECROMANCY,),
    ),
    TagAssignment(
        # The Strongest Upgrade (61090).
        anime_ids=(61090,),
        tag_ids=(TagId.SYSTEM, TagId.CULTIVATION),
    ),
    TagAssignment(
        # Higurashi (934), The Tatami Galaxy (7785), 7th Time Loop (56352),
        # Lockdown Zone: Lv. X (59505).
        anime_ids=(934, 7785, 56352, 59505),
        tag_ids=(TagId.TIME_LOOP,),
    ),
    TagAssignment(
        # A Returner's Magic Should Be Special (54852, 57612), Doctor Elise (54632),
        # 7th Time Loop (56352).
        anime_ids=(54852, 57612, 54632, 56352),
        tag_ids=(TagId.REGRESSION,),
    ),
    TagAssignment(
        # They Were Eleven (1901), Astra Lost in Space (39198).
        anime_ids=(1901, 39198),
        tag_ids=(TagId.SOCIAL_DEDUCTION,),
    ),
    TagAssignment(
        # More than a Married Couple, but Not Lovers. (50425),
        # 365 Days to the Wedding (55887), Gold Kingdom and Water Kingdom (52186).
        anime_ids=(50425, 55887, 52186),
        tag_ids=(TagId.FAKE_RELATIONSHIP,),
    ),
    TagAssignment(
        # Though I Am an Inept Villainess (61240).
        anime_ids=(61240,),
        tag_ids=(TagId.BODY_SWAP,),
    ),
    TagAssignment(
        # D.N.Angel (61), Jing: King of Bandits (107).
        anime_ids=(61, 107),
        tag_ids=(TagId.HEIST,),
    ),
    TagAssignment(
        # One Piece Film: Gold (31490).
        anime_ids=(31490,),
        tag_ids=(TagId.GAMBLING,),
    ),
    TagAssignment(
        # Demon Slayer franchise (38000, 40456, 47778, 49926, 51019, 55701, 59192, 62546, 62547).
        anime_ids=(
            38000,
            40456,
            47778,
            49926,
            51019,
            55701,
            59192,
            62546,
            62547,
        ),
        tag_ids=(TagId.MONSTER_HUNTING, TagId.MONSTERIZATION),
    ),
    TagAssignment(
        # Goblin Slayer franchise (37349, 39576, 47160).
        anime_ids=(37349, 39576, 47160),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Blood franchise: Blood: The Last Vampire (405), Blood+ (150), Blood-C (10490, 10681).
        anime_ids=(405, 150, 10490, 10681),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # D.Gray-man (1482, 32370).
        anime_ids=(1482, 32370),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Seraph of the End (26243, 28927).
        anime_ids=(26243, 28927),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Tokyo Ghoul sequels (27899, 36511, 37799).
        anime_ids=(27899, 36511, 37799),
        tag_ids=(TagId.MONSTERIZATION,),
    ),
    TagAssignment(
        # Devilman (2252, 35120).
        anime_ids=(2252, 35120),
        tag_ids=(TagId.MONSTERIZATION,),
    ),
    TagAssignment(
        # InuYasha franchise (249, 449, 450, 451, 452, 6811).
        anime_ids=(249, 449, 450, 451, 452, 6811),
        tag_ids=(TagId.YOKAI,),
    ),
    TagAssignment(
        # In/Spectre (39017, 44204).
        anime_ids=(39017, 44204),
        tag_ids=(TagId.YOKAI,),
    ),
    TagAssignment(
        # Toilet-Bound Hanako-kun (39534, 53924, 61339).
        anime_ids=(39534, 53924, 61339),
        tag_ids=(TagId.YOKAI,),
    ),
    TagAssignment(
        # The Morose Mononokean (32696, 37958).
        anime_ids=(32696, 37958),
        tag_ids=(TagId.YOKAI,),
    ),
    TagAssignment(
        # Kemono Jihen (40908).
        anime_ids=(40908,),
        tag_ids=(TagId.YOKAI,),
    ),
    TagAssignment(
        # GeGeGe no Kitaro additions (5688, 6971, 7307, 48426).
        anime_ids=(5688, 6971, 7307, 48426),
        tag_ids=(TagId.YOKAI,),
    ),
    TagAssignment(
        # Youkai Watch (37324, 39277, 48365).
        anime_ids=(37324, 39277, 48365),
        tag_ids=(TagId.YOKAI, TagId.CREATURE_TAMING),
    ),
    TagAssignment(
        # Sword Art Online sequels: SAO II (21881), War of Underworld (39597, 40540),
        # Progressive Movies (42916, 50275).
        anime_ids=(21881, 39597, 40540, 42916, 50275),
        tag_ids=(TagId.VIRTUAL_REALITY,),
    ),
    TagAssignment(
        # Log Horizon sequels: Season 2 (23321), Destruction of the Round Table (41109).
        anime_ids=(23321, 41109),
        tag_ids=(TagId.VIRTUAL_REALITY,),
    ),
    TagAssignment(
        # .hack sequels: .hack//G.U. Trilogy (3269), .hack//The Movie (11375).
        anime_ids=(3269, 11375),
        tag_ids=(TagId.VIRTUAL_REALITY,),
    ),
    TagAssignment(
        # Gunslinger Girl: Il Teatrino (3231), Golgo 13 TV (4039), Canaan (5356), Love of Kill (44516).
        anime_ids=(3231, 4039, 5356, 44516),
        tag_ids=(TagId.ASSASSIN,),
    ),
    TagAssignment(
        # Psycho-Pass franchise: Season 2 (23281), Movie (21339),
        # Sinners of the System (37440, 37441, 37442), Season 3 & Inspector (39491, 40858),
        # Providence (52747).
        anime_ids=(23281, 21339, 37440, 37441, 37442, 39491, 40858, 52747),
        tag_ids=(TagId.CYBERPUNK,),
    ),
    TagAssignment(
        # Ghost in the Shell franchise: 1995 (43), Stand Alone Complex (467, 801),
        # Innocence (468), Solid State Society (1566), Arise (14889, 19191, 19193, 19195, 27411),
        # SAC_2045 (38799, 41750).
        anime_ids=(43, 467, 468, 801, 1566, 14889, 19191, 19193, 19195, 27411, 38799, 41750),
        tag_ids=(TagId.CYBERPUNK,),
    ),
    TagAssignment(
        # Akudama Drive (41433).
        anime_ids=(41433,),
        tag_ids=(TagId.CYBERPUNK,),
    ),
    TagAssignment(
        # Steamboy (2134), Last Exile (97, 10336), Kabaneri of the Iron Fortress (28623),
        # The Empire of Corpses (28625), Clockwork Planet (32447).
        anime_ids=(2134, 97, 10336, 28623, 28625, 32447),
        tag_ids=(TagId.STEAMPUNK,),
    ),
    TagAssignment(
        # Fullmetal Alchemist: Brotherhood (5114), Baccano! (2251),
        # Atelier series: Escha & Logy (21167), Ryza (54760),
        # Management of a Novice Alchemist (49849), The Unaware Atelier Meister (60140).
        anime_ids=(5114, 2251, 21167, 54760, 49849, 60140),
        tag_ids=(TagId.ALCHEMY,),
    ),
    TagAssignment(
        # Tokyo Revengers sequels (49387, 53132), InuYasha (249), Thermae Romae Novae (42984).
        anime_ids=(49387, 53132, 249, 42984),
        tag_ids=(TagId.TIME_LEAP,),
    ),
    TagAssignment(
        # The Big O (567), Solty Rei (152), A Wind Named Amnesia (1793), Eden of The East (5630).
        anime_ids=(567, 152, 1793, 5630),
        tag_ids=(TagId.MEMORY_LOSS,),
    ),
    TagAssignment(
        # DIVE!! (34543).
        anime_ids=(34543,),
        tag_ids=(TagId.SWIMMING,),
    ),
    TagAssignment(
        # Medalist (54617, 63326).
        anime_ids=(54617, 63326),
        tag_ids=(TagId.FIGURE_SKATING,),
    ),
    TagAssignment(
        # Nasu: Summer in Andalusia (1209), Long Riders! (30652).
        anime_ids=(1209, 30652),
        tag_ids=(TagId.CYCLING,),
    ),
    TagAssignment(
        # Rising Impact Season 2 (59497).
        anime_ids=(59497,),
        tag_ids=(TagId.GOLF,),
    ),
    TagAssignment(
        # Bamboo Blade (2811).
        anime_ids=(2811,),
        tag_ids=(TagId.KENDO,),
    ),
    TagAssignment(
        # Mou Ippon! (49828), Yawara! (633).
        anime_ids=(49828, 633),
        tag_ids=(TagId.JUDO,),
    ),
    TagAssignment(
        # Battle Spirits franchise (5082, 6901, 9346, 11017, 14913, 19825, 27737, 32670, 41137, 48810, 58373).
        anime_ids=(5082, 6901, 9346, 11017, 14913, 19825, 27737, 32670, 41137, 48810, 58373),
        tag_ids=(TagId.CARD_BATTLING,),
    ),
    TagAssignment(
        # Future Card Buddyfight franchise (19067, 30039, 32785, 34836, 37611, 37739).
        anime_ids=(19067, 30039, 32785, 34836, 37611, 37739),
        tag_ids=(TagId.CARD_BATTLING,),
    ),
    TagAssignment(
        # Duel Masters franchise (6062, 9282, 10524, 10526, 10527, 10528, 21997, 21999,
        # 23409, 29687, 32582, 32926, 34905, 51037, 58275, 59458, 61119, 64848).
        anime_ids=(
            6062,
            9282,
            10524,
            10526,
            10527,
            10528,
            21997,
            21999,
            23409,
            29687,
            32582,
            32926,
            34905,
            51037,
            58275,
            59458,
            61119,
            64848,
        ),
        tag_ids=(TagId.CARD_BATTLING,),
    ),
    TagAssignment(
        # Touch baseball films: Ace Without A Number (2491), The Farewell Gift (2492),
        # After You Passed By (2493).
        anime_ids=(2491, 2492, 2493),
        tag_ids=(TagId.BASEBALL,),
    ),
    TagAssignment(
        # Throne of Seal cultivation franchise (51335, 52684, 61508, 64460).
        anime_ids=(51335, 52684, 61508, 64460),
        tag_ids=(TagId.CULTIVATION,),
    ),
    TagAssignment(
        # Leveling RPG anime: Black Summoner (51064), Villainess Level 99 (54837),
        # Loner Life in Another World (57891), My Gift Lvl 9999 Unlimited Gacha (60303),
        # Welcome to the Outcast's Restaurant! (60523),
        # My Status as an Assassin Obviously Exceeds the Hero's (61026),
        # Cheat Skill Season 2 (63822).
        anime_ids=(51064, 54837, 57891, 60303, 60523, 61026, 63822),
        tag_ids=(TagId.LEVELING,),
    ),
    TagAssignment(
        # Revenge anime: Ringing Bell (2199), Judo Boy (4439), Shenmue (4524),
        # The Elusive Samurai (54724), Tougen Anki (58811), Gachiakuta (59062),
        # Kagurabachi (64058).
        anime_ids=(2199, 4439, 4524, 54724, 58811, 59062, 64058),
        tag_ids=(TagId.REVENGE,),
    ),
    TagAssignment(
        # Fist of the North Star franchise (1356, 1358, 1773, 2174, 5291),
        # Trigun franchise: Badlands Rumble (4106), Stampede (52093), Stargaze (54863),
        # Dr. Stone franchise (38691, 40852, 48549, 55644, 57592, 61322, 62568),
        # Ergo Proxy (790), Coppelion (9479), Heavenly Delusion (53393),
        # Seraph of the End (26243, 28927), Knights of Sidonia (19775).
        anime_ids=(
            1356,
            1358,
            1773,
            2174,
            5291,
            4106,
            52093,
            54863,
            38691,
            40852,
            48549,
            55644,
            57592,
            61322,
            62568,
            790,
            9479,
            53393,
            26243,
            28927,
            19775,
        ),
        tag_ids=(TagId.POST_APOCALYPTIC,),
    ),
    TagAssignment(
        # That Time I Got Reincarnated as a Slime sequels (39551, 41487, 49877, 53580, 59970, 63129),
        # Log Horizon franchise (17265, 23321, 41109),
        # Dr. Stone franchise (38691, 40852, 48549, 55644, 57592, 61322, 62568),
        # Utawarerumono franchise (856, 30901, 40590).
        anime_ids=(
            39551,
            41487,
            49877,
            53580,
            59970,
            63129,
            17265,
            23321,
            41109,
            38691,
            40852,
            48549,
            55644,
            57592,
            61322,
            62568,
            856,
            30901,
            40590,
        ),
        tag_ids=(TagId.NATION_BUILDING,),
    ),
    TagAssignment(
        # Release the Spyce (37221), Night Raid 1931 (6973).
        anime_ids=(37221, 6973),
        tag_ids=(TagId.ESPIONAGE,),
    ),
    TagAssignment(
        # Baki: The Great Raitai Tournament Saga (39555), Shigurui (2216),
        # Garouden: The Way of the Lone Wolf (58717).
        anime_ids=(39555, 2216, 58717),
        tag_ids=(TagId.TOURNAMENT,),
    ),
    TagAssignment(
        # Tokyo Godfathers (759), Kotaro Lives Alone (49909), Somali and the Forest Spirit (39575),
        # Barakamon (22789), Gintama core franchise (918, 7472, 9969, 15335, 15417, 28977,
        # 34096, 35843, 36838, 37491, 39486).
        anime_ids=(
            759,
            49909,
            39575,
            22789,
            918,
            7472,
            9969,
            15335,
            15417,
            28977,
            34096,
            35843,
            36838,
            37491,
            39486,
        ),
        tag_ids=(TagId.FOUND_FAMILY,),
    ),
    TagAssignment(
        # Slayers franchise (534, 535, 1172, 4028, 5233),
        # Log Horizon (17265, 23321, 41109),
        # Record of Lodoss War: Chronicles of the Heroic Knight (206),
        # Rune Soldier (1164), KonoSuba: Legend of Crimson (38040).
        anime_ids=(534, 535, 1172, 4028, 5233, 17265, 23321, 41109, 206, 1164, 38040),
        tag_ids=(TagId.ADVENTURING_PARTY,),
    ),
    TagAssignment(
        # JoJo's Bizarre Adventure: Stone Ocean Part 3 (53273), Dead Leaves (974).
        anime_ids=(53273, 974),
        tag_ids=(TagId.PRISON_SETTING,),
    ),
    TagAssignment(
        # Suzuka (390).
        anime_ids=(390,),
        tag_ids=(TagId.RUNNING,),
    ),
    TagAssignment(
        # Area 88 TV & Movie (284, 33232), Stratos 4 (421), Allison & Lillia (3549),
        # Girly Air Force (37998), Warlords of Sigrdrifa (41372),
        # The Magnificent Kotobuki spin-off & movie (39589, 41205),
        # The Pilot's Love Song (19117), Dragon Pilot: Hisone and Masotan (36884),
        # Last Exile franchise (97, 10336, 31866), Macross Plus Movie Edition (1211).
        anime_ids=(
            284,
            33232,
            421,
            3549,
            37998,
            41372,
            39589,
            41205,
            19117,
            36884,
            97,
            10336,
            31866,
            1211,
        ),
        tag_ids=(TagId.AVIATION,),
    ),
    TagAssignment(
        # Shoubushi Densetsu Tetsuya (3369).
        anime_ids=(3369,),
        tag_ids=(TagId.MAHJONG,),
    ),
    TagAssignment(
        # Quanzhi Gaoshou: Rongyao Xiao Juchang (60513, 64735),
        # Bokura no Ame-iro Protocol Mini (56869),
        # Lu Shidai (31233, 32543), Glamorous Heroes (36288).
        anime_ids=(60513, 64735, 56869, 31233, 32543, 36288),
        tag_ids=(TagId.ESPORTS,),
    ),
    TagAssignment(
        # Talentless Nana Mini Anime (42831).
        anime_ids=(42831,),
        tag_ids=(TagId.SOCIAL_DEDUCTION,),
    ),
    TagAssignment(
        # Accel World: Infinite∞Burst (31763), Robotics;Notes (13599).
        anime_ids=(31763, 13599),
        tag_ids=(TagId.AUGMENTED_REALITY,),
    ),
    TagAssignment(
        # Xin Weiqi Shaonian (51862).
        anime_ids=(51862,),
        tag_ids=(TagId.GO,),
    ),
    TagAssignment(
        # Cinderella Boy (301), No Doubt In Us 2nd Season (50403).
        anime_ids=(301, 50403),
        tag_ids=(TagId.BODY_SWAP,),
    ),
    TagAssignment(
        # That Time I Got Reincarnated as a Slime sequels (39551, 41487, 53580, 59970, 63129),
        # Death March to the Parallel World Rhapsody (34497),
        # Villainess Level 99 (54837),
        # My Status as an Assassin Obviously Exceeds the Hero's (61026),
        # I Got a Cheat Skill in Another World (52830, 63822),
        # Uglymug, Epicfighter (60316), Reincarnated as a Sword (49891, 53913).
        anime_ids=(
            39551,
            41487,
            53580,
            59970,
            63129,
            34497,
            54837,
            61026,
            52830,
            63822,
            60316,
            49891,
            53913,
        ),
        tag_ids=(TagId.SYSTEM,),
    ),
    TagAssignment(
        # Death March to the Parallel World Rhapsody (34497),
        # I Got a Cheat Skill in Another World (52830),
        # Reincarnated as a Sword (49891, 53913),
        # The Unwanted Undead Adventurer (51648).
        anime_ids=(34497, 52830, 49891, 53913, 51648),
        tag_ids=(TagId.LEVELING,),
    ),
    TagAssignment(
        # The Unwanted Undead Adventurer (51648).
        anime_ids=(51648,),
        tag_ids=(TagId.MONSTERIZATION,),
    ),
    TagAssignment(
        # Arifureta Season 3 (52995),
        # The Strongest Tank's Labyrinth Raids (56845),
        # The Unwanted Undead Adventurer (51648).
        anime_ids=(52995, 56845, 51648),
        tag_ids=(TagId.DUNGEON,),
    ),
    TagAssignment(
        # Darwin's Game (38656), Fate/Zero Season 2 (11741),
        # Fate/stay night: Unlimited Blade Works Movie (6922),
        # Fate/stay night: Heaven's Feel trilogy (25537, 33049, 33050),
        # Fate/Extra: Last Encore (33047, 37651), Platinum End (44961),
        # Mahou Shoujo Ikusei Keikaku: Restart (54344).
        anime_ids=(
            38656,
            11741,
            6922,
            25537,
            33049,
            33050,
            33047,
            37651,
            44961,
            54344,
        ),
        tag_ids=(TagId.BATTLE_ROYALE,),
    ),
    TagAssignment(
        # Rent-a-Girlfriend franchise (40839, 42963, 53050, 59277, 62485, 64484).
        anime_ids=(40839, 42963, 53050, 59277, 62485, 64484),
        tag_ids=(TagId.FAKE_RELATIONSHIP,),
    ),
    TagAssignment(
        # Steins;Gate 0 (30484), Steins;Gate: Load Region of Déjà Vu (11577),
        # Link Click franchise (44074, 49200, 49413, 56752, 61607).
        anime_ids=(30484, 11577, 44074, 49200, 49413, 56752, 61607),
        tag_ids=(TagId.TIME_LEAP,),
    ),
    TagAssignment(
        # Eden of The East movies & recap (6372, 6637, 6927),
        # Brynhildr in the Darkness (21431).
        anime_ids=(6372, 6637, 6927, 21431),
        tag_ids=(TagId.MEMORY_LOSS,),
    ),
    TagAssignment(
        # Gun x Sword (411).
        anime_ids=(411,),
        tag_ids=(TagId.REVENGE,),
    ),
    TagAssignment(
        # Assassination Classroom movies & specials (32863, 33513, 62421).
        anime_ids=(32863, 33513, 62421),
        tag_ids=(TagId.ASSASSIN,),
    ),
    TagAssignment(
        # Princess Principal: Ange Report (36424).
        anime_ids=(36424,),
        tag_ids=(TagId.ESPIONAGE,),
    ),
    TagAssignment(
        # Space Dandy (20057, 23327), Cannon Busters (40256).
        anime_ids=(20057, 23327, 40256),
        tag_ids=(TagId.BOUNTY_HUNTER,),
    ),
    TagAssignment(
        # Eden of The East franchise (5630, 6372, 6637, 6927).
        anime_ids=(5630, 6372, 6637, 6927),
        tag_ids=(TagId.CONSPIRACY,),
    ),
    TagAssignment(
        # Kengan Ashura franchise (40269, 51369, 56704, 58510),
        # Gundam Build Fighters franchise (19319, 24625, 35567, 35982),
        # Megalobox (36563).
        anime_ids=(
            40269,
            51369,
            56704,
            58510,
            19319,
            24625,
            35567,
            35982,
            36563,
        ),
        tag_ids=(TagId.TOURNAMENT,),
    ),
    TagAssignment(
        # Possibly the Greatest Alchemist of All Time (58822, 62469),
        # Management of a Novice Alchemist Mini Anime (53248),
        # The Unaware Atelier Meister Mini Anime & S2 (61411, 62924),
        # The Fake Alchemist (64419).
        anime_ids=(58822, 62469, 53248, 61411, 62924, 64419),
        tag_ids=(TagId.ALCHEMY,),
    ),
    TagAssignment(
        # Free! Character Butai Aisatsu shorts (37858, 37859, 37860).
        anime_ids=(37858, 37859, 37860),
        tag_ids=(TagId.SWIMMING,),
    ),
    TagAssignment(
        # Princess Principal films & specials (36424, 37807, 41140, 41141, 57093, 57094, 57095),
        # Kabaneri of the Iron Fortress films (33519, 33520, 34544),
        # Nadia: The Secret of Blue Water TV & Film (1251, 1252),
        # Metropolis (522), Sakura Wars: The Movie & The Animation (608, 40403),
        # Castle in the Sky (513).
        anime_ids=(
            36424,
            37807,
            41140,
            41141,
            57093,
            57094,
            57095,
            33519,
            33520,
            34544,
            1251,
            1252,
            522,
            608,
            40403,
            513,
        ),
        tag_ids=(TagId.STEAMPUNK,),
    ),
    TagAssignment(
        # Pretty Guardian Sailor Moon franchise (531, 532, 740, 996, 997, 1239, 1240,
        # 14751, 31733, 40024, 40429, 51716),
        # Symphogear franchise (11751, 15793, 21573, 32836, 32843),
        # Tokyo Mew Mew New (41589, 52612, 53097),
        # Shugo Chara! (2923, 5262, 7082),
        # Magical Girl Lyrical Nanoha franchise (76, 77, 1915, 4985, 10153).
        anime_ids=(
            531,
            532,
            740,
            996,
            997,
            1239,
            1240,
            14751,
            31733,
            40024,
            40429,
            51716,
            11751,
            15793,
            21573,
            32836,
            32843,
            41589,
            52612,
            53097,
            2923,
            5262,
            7082,
            76,
            77,
            1915,
            4985,
            10153,
        ),
        tag_ids=(TagId.TRANSFORMATION,),
    ),
    TagAssignment(
        # Higurashi franchise (41006, 48488, 64449).
        anime_ids=(41006, 48488, 64449),
        tag_ids=(TagId.TIME_LOOP,),
    ),
    TagAssignment(
        # The Tatami Time Machine Blues (49590).
        anime_ids=(49590,),
        tag_ids=(TagId.TIME_LEAP,),
    ),
    TagAssignment(
        # Baccano! (2251), Maquia: When the Promised Flower Blooms (35851),
        # Land of the Lustrous (35557), UQ Holder! (33478).
        anime_ids=(2251, 35851, 35557, 33478),
        tag_ids=(TagId.IMMORTALITY,),
    ),
    TagAssignment(
        # One Piece theatrical & franchise entries (2386, 2490, 9999, 16468, 33606, 38419, 57557, 60108),
        # Bodacious Space Pirates TV & Movie (8917, 14817),
        # Space Pirate Captain Harlock franchise (2202, 2203, 2470).
        anime_ids=(
            2386,
            2490,
            9999,
            16468,
            33606,
            38419,
            57557,
            60108,
            8917,
            14817,
            2202,
            2203,
            2470,
        ),
        tag_ids=(TagId.PIRATES,),
    ),
    TagAssignment(
        # Idaten Jump (1316).
        anime_ids=(1316,),
        tag_ids=(TagId.CYCLING,),
    ),
    TagAssignment(
        # Overlord movies (34161, 34428, 48896),
        # First Squad: The Moment of Truth (5178),
        # Corpse Princess: Kuro (5034).
        anime_ids=(34161, 34428, 48896, 5178, 5034),
        tag_ids=(TagId.NECROMANCY,),
    ),
    TagAssignment(
        # Kabaneri of the Iron Fortress movies (33519, 33520, 34544),
        # Corpse Princess: Kuro (5034), Sunday Without God (16009).
        anime_ids=(33519, 33520, 34544, 5034, 16009),
        tag_ids=(TagId.ZOMBIE,),
    ),
    TagAssignment(
        # Overlord movies (34161, 34428, 48896).
        anime_ids=(34161, 34428, 48896),
        tag_ids=(TagId.NATION_BUILDING, TagId.POLITICS),
    ),
    TagAssignment(
        # Beck: Mongolian Chop Squad (57),
        # Bocchi the Rock! franchise (47917, 55357, 61006),
        # K-On! franchise (5680, 7791, 9617), Nana (877),
        # given franchise (39533, 40421, 54791, 58222),
        # Girls Band Cry franchise (55102, 59817, 62550),
        # BanG Dream! core & spin-offs (33573, 37869, 37870, 37873, 39619, 40854,
        # 41462, 41780, 41781, 41782, 49123, 51218, 54959, 57754, 61324, 62270),
        # Show By Rock!! franchise (27441, 32038, 40763, 41520),
        # Sound! Euphonium franchise (27989, 31988, 35678, 39894).
        anime_ids=(
            57,
            47917,
            55357,
            61006,
            5680,
            7791,
            9617,
            877,
            39533,
            40421,
            54791,
            58222,
            55102,
            59817,
            62550,
            33573,
            37869,
            37870,
            37873,
            39619,
            40854,
            41462,
            41780,
            41781,
            41782,
            49123,
            51218,
            54959,
            57754,
            61324,
            62270,
            27441,
            32038,
            40763,
            41520,
            27989,
            31988,
            35678,
            39894,
        ),
        tag_ids=(TagId.MUSICAL_BAND,),
    ),
    TagAssignment(
        # Ace Attorney franchise (31630, 32946, 37490),
        # Wizard Barristers (20053), Babylon (37525).
        anime_ids=(31630, 32946, 37490, 20053, 37525),
        tag_ids=(TagId.LEGAL,),
    ),
    TagAssignment(
        # Angel Beats! (6547), Death Parade & Death Billiards (28223, 14353),
        # Haibane Renmei (387),
        # Hozuki's Coolheadedness franchise (20431, 35075, 37029),
        # Colorful (8142), Descendants of Darkness (553),
        # RIN-NE franchise (28423, 31610, 34106),
        # Hell Girl franchise (228, 1594, 3713, 34966),
        # As Miss Beelzebub Likes. (37716).
        anime_ids=(
            6547,
            28223,
            14353,
            387,
            20431,
            35075,
            37029,
            8142,
            553,
            28423,
            31610,
            34106,
            228,
            1594,
            3713,
            34966,
            37716,
        ),
        tag_ids=(TagId.AFTERLIFE,),
    ),
    TagAssignment(
        # Haibane Renmei (387), Mushishi franchise (457, 21939, 24701),
        # Kino's Journey (486), Girls' Last Tour (35838),
        # Somali and the Forest Spirit (39575), 5 Centimeters per Second (1689),
        # Casshern Sins (4981), Frieren: Beyond Journey's End (52991),
        # Maquia: When the Promised Flower Blooms (35851),
        # The Garden of Words (16782),
        # Violet Evergarden franchise (33352, 37987, 39741),
        # Wolf's Rain (202), Natsume's Book of Friends franchise (4081, 5300,
        # 10379, 11665, 32983, 34591, 36538, 42894, 55823).
        anime_ids=(
            387,
            457,
            21939,
            24701,
            486,
            35838,
            39575,
            1689,
            4981,
            52991,
            35851,
            16782,
            33352,
            37987,
            39741,
            202,
            4081,
            5300,
            10379,
            11665,
            32983,
            34591,
            36538,
            42894,
            55823,
        ),
        tag_ids=(TagId.MELANCHOLIC,),
    ),
    TagAssignment(
        # Titles: Texhnolyze (26), Now and Then, Here and There (160),
        # Berserk core franchise & Golden Age films (33, 10218, 12113, 12115, 32379, 34055, 52976),
        # Bokurano (1690), Devilman: Crybaby (35120),
        # From the New World / Shinsekai yori (13125),
        # Grave of the Fireflies (578), Barefoot Gen (1824).
        anime_ids=(
            26,
            160,
            33,
            10218,
            12113,
            12115,
            32379,
            34055,
            52976,
            1690,
            35120,
            13125,
            578,
            1824,
        ),
        tag_ids=(TagId.BLEAK,),
    ),
    TagAssignment(
        # The Tatami Galaxy (7785), Night Is Short, Walk on Girl (34537),
        # Kyousougiga franchise (10893, 15359, 19703),
        # Humanity Has Declined (10357), Kaiba (3701), Flip Flappers (32979),
        # Dorohedoro S1 & S2 (38668, 57779),
        # Keep Your Hands Off Eizouken! (39792).
        anime_ids=(
            7785,
            34537,
            10893,
            15359,
            19703,
            10357,
            3701,
            32979,
            38668,
            57779,
            39792,
        ),
        tag_ids=(TagId.WHIMSICAL,),
    ),
    TagAssignment(
        # Orb: On the Movements of the Earth (52215),
        # To Your Eternity franchise (41025, 49709, 54703),
        # Attack on Titan core franchise (16498, 25777, 35760, 38524, 40028, 48583),
        # From the New World / Shinsekai yori (13125), Kaiba (3701),
        # Ghost in the Shell franchise (43, 468, 467),
        # Serial Experiments Lain (339), Ergo Proxy (790),
        # Kino's Journey (486, 35079), Girls' Last Tour (35838),
        # Haibane Renmei (387), Psycho-Pass S1 & S2 (13601, 23281),
        # Texhnolyze (26), Bokurano (1690), Neon Genesis Evangelion (30),
        # Mushi-Shi franchise (457, 21939, 24701), Kiznaiver (31798),
        # The Tatami Galaxy (7785).
        anime_ids=(
            52215,
            41025,
            49709,
            54703,
            16498,
            25777,
            35760,
            38524,
            40028,
            48583,
            13125,
            3701,
            43,
            468,
            467,
            339,
            790,
            486,
            35079,
            35838,
            387,
            13601,
            23281,
            26,
            1690,
            30,
            457,
            21939,
            24701,
            31798,
            7785,
        ),
        tag_ids=(TagId.PHILOSOPHICAL,),
    ),
    TagAssignment(
        # Totoro, Kiki, and Ponyo: independently reviewed whimsical works.
        anime_ids=(523, 512, 2890),
        tag_ids=(TagId.WHIMSICAL,),
    ),
    TagAssignment(
        # Totoro, Natsume, and Summer Days with Coo: Japanese spirit/yokai stories.
        anime_ids=(523, 4081, 2848),
        tag_ids=(TagId.YOKAI,),
    ),
    TagAssignment(
        # Busou Renkin: homunculus hunting is a central recurring activity.
        anime_ids=(1536,),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Pandora Hearts (5530).
        anime_ids=(5530,),
        tag_ids=(TagId.CONSPIRACY,),
    ),
    TagAssignment(
        # Tensei Kenja no Isekai Life (47163).
        anime_ids=(47163,),
        tag_ids=(TagId.CREATURE_TAMING,),
    ),
    TagAssignment(
        # Ple Ple Pleiades x Kagejitsu! (57034).
        anime_ids=(57034,),
        tag_ids=(TagId.BODY_SWAP,),
    ),
    TagAssignment(
        # Outlaw Star (400).
        anime_ids=(400,),
        tag_ids=(TagId.FOUND_FAMILY,),
    ),
    TagAssignment(
        # Shukufuku no Campanella (6979), Himekishi-sama no Himo (61015).
        anime_ids=(6979, 61015),
        tag_ids=(TagId.ADVENTURING_PARTY,),
    ),
    TagAssignment(
        # Harmony (28211), ARP Backstage Pass (40137).
        anime_ids=(28211, 40137),
        tag_ids=(TagId.AUGMENTED_REALITY,),
    ),
    TagAssignment(
        # Bokutachi no American Football (53749).
        anime_ids=(53749,),
        tag_ids=(TagId.AMERICAN_FOOTBALL,),
    ),
    TagAssignment(
        # Kore wa Zombie desu ka? (8841, 10790), Yuusha ga Shinda! (51706).
        anime_ids=(8841, 10790, 51706),
        tag_ids=(TagId.NECROMANCY,),
    ),
    TagAssignment(
        # MonHun Nikki Girigiri Airou Mura (8960, 10802).
        anime_ids=(8960, 10802),
        tag_ids=(TagId.MONSTER_HUNTING,),
    ),
    TagAssignment(
        # Divergence Eve (294, 295).
        anime_ids=(294, 295),
        tag_ids=(TagId.MONSTERIZATION,),
    ),
    TagAssignment(
        # RE:Map (34113).
        anime_ids=(34113,),
        tag_ids=(TagId.TIME_LEAP,),
    ),
    TagAssignment(
        # Anime Document: München e no Michi (20237).
        anime_ids=(20237,),
        tag_ids=(TagId.VOLLEYBALL,),
    ),
    TagAssignment(
        # Juushin Liger (4119), Houkago no Pleiades (9911), Happiness Charge Precure! (21407),
        # Tropical-Rouge! Precure Petit (46650).
        anime_ids=(4119, 9911, 21407, 46650),
        tag_ids=(TagId.TRANSFORMATION,),
    ),
    TagAssignment(
        # Zui Qiang Shengji (61090), Shen Zai Jiong Tu (62544), Val x Love (39799).
        anime_ids=(61090, 62544, 39799),
        tag_ids=(TagId.LEVELING,),
    ),
    TagAssignment(
        # Pon no Michi (55397).
        anime_ids=(55397,),
        tag_ids=(TagId.MAHJONG,),
    ),
    TagAssignment(
        # Dragon Ball (223, 892), Ueki no Housoku (479), Kizuna Ichigeki (10016).
        anime_ids=(223, 892, 479, 10016),
        tag_ids=(TagId.TOURNAMENT,),
    ),
    TagAssignment(
        # Life of the Dead (30089), Wo Zai Feitu Shijie Sao Laji (62953).
        anime_ids=(30089, 62953),
        tag_ids=(TagId.ZOMBIE,),
    ),
    TagAssignment(
        # Fantasista Doll (15883), Rebirth (40129), Zenonzard Episode 0 (40394), Weiß Survive (6425).
        anime_ids=(15883, 40129, 40394, 6425),
        tag_ids=(TagId.CARD_BATTLING,),
    ),
    TagAssignment(
        # Zoids Wild (37395), Mo You Ji (51361), Xiuluo Wushen 2 (62280).
        anime_ids=(37395, 51361, 62280),
        tag_ids=(TagId.TREASURE_HUNTING,),
    ),
    TagAssignment(
        # Zaizen Joutarou (1740), Hanasakeru Seishounen (5835), Gate Part 2 (31637), Shoukoku no Altair (34547),
        # Wangu Zhizun (62954).
        anime_ids=(1740, 5835, 31637, 34547, 62954),
        tag_ids=(TagId.POLITICS,),
    ),
    TagAssignment(
        # Shin Tennis no Oujisama World Cup (62534), Softenni (10109).
        anime_ids=(62534, 10109),
        tag_ids=(TagId.TENNIS,),
    ),
)

TAG_ASSIGNMENT_REGISTRY = TagAssignmentRegistry(TAG_ASSIGNMENTS_VERSION, MANUAL_TAG_ASSIGNMENTS)


@cache
def tag_assignment_registry_identity() -> str:
    """Return the cached identity of the feature tag assignments."""
    return TAG_ASSIGNMENT_REGISTRY.identity()
