"""Curated same-story links for incomplete catalogue relation data."""

MANUAL_RELATIONSHIPS: dict[int, tuple[int, ...]] = {
    # Higurashi no Naku Koro ni (934) → Kai (1889), Gou (41006), Sotsu (48488), Shinsaku (64449).
    934: (1889, 41006, 48488, 64449),
    # Tokyo Ghoul (22319) → √A (27899), :re (36511), :re 2nd Season (37799).
    22319: (27899, 36511, 37799),
    # Gintama (918) → sequels, films, specials, and compilations.
    918: (7472, 9969, 15335, 15417, 21899, 28977, 34096, 35843, 36838, 37491, 39486, 40323, 58091, 59688),
    # Tennis no Oujisama (22) → films, specials, and Shin Tennis no Oujisama entries.
    22: (814, 10731, 11371, 38882, 41842, 50099, 55570),
    # Cang Lan Jue (51280) → Part 2 and Season 2 (53905, 61561).
    51280: (53905, 61561),
    # Xianwu Zhuan (52522) → Season 2 (56717).
    52522: (56717,),
    # Crayon Shin-chan (966) → movies and related shorts.
    966: (
        2450,
        3744,
        3745,
        6217,
        6460,
        8358,
        8362,
        8363,
        8364,
        8368,
        8369,
        10116,
        12499,
        17113,
        21395,
        27653,
        31978,
        34244,
        35139,
        36566,
        38629,
        40329,
        44616,
        50562,
        53810,
        53969,
        53970,
        53971,
        57499,
        60862,
        63512,
    ),
    # 0-saiji Start Dash Monogatari (58985) → Season 2 (60425).
    58985: (60425,),
    # 100-man no Inochi no Ue ni Ore wa Tatteiru (41380) → Season 2 (44881).
    41380: (44881,),
    # 3-gatsu no Lion (31646) → Season 2 (35180).
    31646: (35180,),
    # 3D Kanojo: Real Girl (36793) → Season 2 (37956).
    36793: (37956,),
    # 5-toubun no Hanayome (38101) → ∬, Movie, and Shunkashuutou (39783, 48548, 64104).
    38101: (39783, 48548, 64104),
    # 12-sai (32601) → 2nd Season (33419).
    32601: (33419,),
    # 7 Seeds (38735) → Season 2 (40602).
    38735: (40602,),
    # Aharen-san wa Hakarenai (49520) → Season 2 (59466).
    49520: (59466,),
    # Active Raid (31790) → 2nd Season (32301).
    31790: (32301,),
    # Arifureta (36882) → Seasons 2-3 (40507, 52995).
    36882: (40507, 52995),
    # Black Lagoon (889) → The Second Barrage (1519).
    889: (1519,),
    # Bocchi the Rock! (47917) → Movie and 2nd Season (55357, 61006).
    47917: (55357, 61006),
    # Chainsaw Man (44511) → Reze Arc Movie (57555).
    44511: (57555,),
    # Edens Zero (42192) → 2nd Season (50002).
    42192: (50002,),
    # Enen no Shouboutai (38671) → Seasons 2-3 (40956, 51818, 59229).
    38671: (40956, 51818, 59229),
    # Fairy Tail (6702) → 2014, Final Series, and 100 Years Quest (22043, 35972, 49785).
    6702: (22043, 35972, 49785),
    # Tate no Yuusha (35790) → Seasons 2-5 (40356, 40357, 57907, 62564).
    35790: (40356, 40357, 57907, 62564),
    # Youjo Senki (32615) → Movie and Season II (37055, 49233).
    32615: (37055, 49233),
    # Zombieland Saga (37976) → Revenge and Movie (40174, 50159).
    37976: (40174, 50159),
    # Bleach: Thousand-Year Blood War (41467) → split parts (53998, 56784, 60636).
    41467: (53998, 56784, 60636),
    # Dr. Stone (38691) → later seasons and parts.
    38691: (40852, 48549, 55644, 57592, 61322, 62568),
    # Fate/kaleid liner Prisma☆Illya (14829) → sequels and films.
    14829: (20509, 27525, 31706, 34100, 38897, 42030, 49703),
    # Fate/Zero (10087) → Season 2 (11741).
    10087: (11741,),
    # Fate/stay night (356) → route adaptations and films.
    356: (6922, 22297, 25537, 28701, 33049, 33050),
    # Fate/Grand Order: Fujimaru Ritsuka wa Wakaranai (54042) → Seasons 2-3 (59465, 62149).
    54042: (59465, 62149),
    # Uta no☆Prince-sama♪ Maji Love 1000% (10321) → later seasons and films.
    10321: (12711, 21439, 31178, 35645, 48573, 57622),
    # Fruits Basket (2019) (38680) → Seasons 2-3 and Prelude (40417, 42938, 49310).
    38680: (40417, 42938, 49310),
    # Natsume Yuujinchou (4081) → later seasons, film, and specials.
    4081: (5300, 10379, 11665, 32983, 34591, 36538, 42894, 55823),
    # Kingdom (12031) → Seasons 2-6 (17389, 40682, 50160, 53223, 61517).
    12031: (17389, 40682, 50160, 53223, 61517),
    # Suzumiya Haruhi no Yuuutsu (849) → 2009 series and film (4382, 7311).
    849: (4382, 7311),
    # Ore no Imouto ga Konnani Kawaii Wake ga Nai (8769) → Season 2 (13659).
    8769: (13659,),
    # Magi: The Labyrinth of Magic (14513) → The Kingdom of Magic (18115).
    14513: (18115,),
    # Love Live! School Idol Project (15051) → Season 2 and Movie (19111, 24997).
    15051: (19111, 24997),
    # Love Live! Sunshine!! (32526) → Season 2 and Movie (34973, 37027).
    32526: (34973, 37027),
    # Love Live! Nijigasaki Gakuen School Idol Doukoukai (40879) → Season 2 (48916).
    40879: (48916,),
    # Love Live! Superstar!! (41169) → Seasons 2-3 (50203, 53287).
    41169: (50203, 53287),
    # BanG Dream! (33573) → Seasons 2-3 (37869, 37870).
    33573: (37869, 37870),
    # BanG Dream! Garupa☆Pico (37873) → later seasons (40854, 49123).
    37873: (40854, 49123),
    # BanG Dream! It's MyGO!!!!! (54959) → Movie (57754).
    54959: (57754,),
    # Shoujo☆Kageki Revue Starlight (35503) → recap and feature films (40664, 40665).
    35503: (40664, 40665),
    # Senki Zesshou Symphogear (11751) → later seasons (15793, 21573, 32836, 32843).
    11751: (15793, 21573, 32836, 32843),
    # Chibi Maruko-chan (951) → original-continuity films (3203, 9348, 31202).
    951: (3203, 9348, 31202),
    # Keroro Gunsou (516) → feature films and specials (2407, 5290, 54355, 58773).
    516: (2407, 5290, 54355, 58773),
    # Mairimashita! Iruma-kun (39196) → Seasons 2-3 (41402, 49784).
    39196: (41402, 49784),
    # Kanojo, Okarishimasu (40839) → Seasons 2-3 and Date Movie (42963, 51135, 53050).
    40839: (42963, 51135, 53050),
    # Itai no wa Iya nanode Bougyoryoku ni Kyokufuri Shitai to Omoimasu. (38790) → Season 2 (42014).
    38790: (42014,),
    # Strike Witches: 501 Butai Hasshin Shimasu! (38004) → Movie (39987).
    38004: (39987,),
    # Magic Knight Rayearth (435) → Season II (1563).
    435: (1563,),
    # Nodame Cantabile (1698) → Paris-hen and Finale (4477, 5690).
    1698: (4477, 5690),
    # JoJo no Kimyou na Bouken (14719) → direct animated parts and continuations.
    14719: (20899, 26055, 31933, 37991, 48661, 51367, 53273, 61469),
    # Bishoujo Senshi Sailor Moon (530) → original-continuity seasons and films.
    530: (531, 532, 740, 996, 997, 1239, 1240),
    # Initial D First Stage (185) → later stages (18, 186, 187, 15059, 22507).
    185: (18, 186, 187, 15059, 22507),
    # Yowamushi Pedal (18179) → seasons and recap films.
    18179: (24277, 25755, 30413, 30790, 31783, 35789, 35880, 50552),
    # Major S1 (627) → Seasons 2-6 and feature film.
    627: (1842, 3226, 5028, 5029, 558, 7655),
    # Major 2nd (36565) → 2nd Season (40504).
    36565: (40504,),
    # Free! (18507) → direct seasons and films.
    18507: (22265, 33845, 35191, 35198, 36704, 38400, 39014, 48830),
    # Nanatsu no Taizai (23755) → later seasons, films, and specials.
    23755: (31722, 34577, 35946, 36569, 39701, 41491, 50315),
    # Dragon Ball (223) → original-series films (502, 891, 892).
    223: (502, 891, 892),
    # Dragon Ball Z (813) → Z films and Kai recuts (6033, 894, 895, 897, 898, 899, 900, 902, 903, 904, 905, 906, 22777).
    813: (6033, 894, 895, 897, 898, 899, 900, 902, 903, 904, 905, 906, 22777),
    # Dragon Ball Super (30694) → feature films (14837, 25389, 36946, 48903).
    30694: (14837, 25389, 36946, 48903),
    # Digimon Adventure (552) → Adventure 02, tri., and continuation films.
    552: (1313, 2397, 2398, 25687, 32108, 32551, 34299, 34962, 36466, 38088, 41206),
    # Digimon Tamers (874) → films (3032, 3033).
    874: (3032, 3033),
    # Digimon Frontier (1132) → film (3031).
    1132: (3031,),
    # Digimon Xros Wars (8624) → later arcs (10444, 11385).
    8624: (10444, 11385),
    # Inazuma Eleven (5231) → feature films (9032, 24347, 59709).
    5231: (9032, 24347, 59709),
    # Inazuma Eleven Go (10507) → Chrono Stone, Galaxy, and films.
    10507: (10999, 13261, 18097),
    # Inazuma Eleven Ares no Tenbin (33733) → Orion no Kokuin (38235).
    33733: (38235,),
    # Futari wa Precure (603) → Max Heart and its film (1929, 4124).
    603: (1929, 4124),
    # Yes! Precure 5 (1932) → GoGo! (3692).
    1932: (3692,),
    # One Piece (21) → feature films and direct specials.
    21: (459, 460, 461, 462, 463, 464, 465, 2107, 3848, 4155, 9999, 12859, 31490, 38234, 50410, 53878, 53880, 60108),
    # Meitantei Conan (235) → feature films.
    235: (
        779,
        780,
        781,
        1363,
        1364,
        1365,
        1366,
        1367,
        1505,
        1506,
        2171,
        4447,
        5460,
        6467,
        9963,
        12117,
        14735,
        21419,
        28479,
        32005,
        34430,
        35798,
        38770,
        39764,
        49320,
        53540,
        56785,
        62387,
    ),
    # Mahou Shoujo Madoka Magica (9756) → original-continuity films.
    9756: (11979, 11981, 32153, 48820),
    # Mahou Shoujo Madoka Magica Gaiden (38256) → Season 2 (41530).
    38256: (41530,),
    # Clannad (2167) → After Story and Movie (1723, 4181).
    2167: (1723, 4181),
    # Code Geass: Lelouch of the Rebellion (1575) → R2 (2904).
    1575: (2904,),
    # Code Geass: Akito the Exiled (8888) → remaining films.
    8888: (15197, 15199, 15201, 30711),
    # Shinseiki Evangelion (30) → original-continuity films (31, 32).
    30: (31, 32),
    # Evangelion: 1.0 You Are (Not) Alone (2759) → Rebuild films 2-4 (3784, 3785, 3786).
    2759: (3784, 3785, 3786),
    # Tales of Zestiria the Cross (30911) → 2nd Season (34086).
    30911: (34086,),
    # T.P BON (56840) → Season 2 (59274).
    56840: (59274,),
    # Tadaima! Chibi Godzilla (42500) → Season 2 (45611).
    42500: (45611,),
    # Taiho Shichau zo (1372) → specials, movie, and later series.
    1372: (2011, 2013, 2014, 3000),
    # Tropical-Rouge! Precure (44191) → related films (46650, 49426).
    44191: (46650, 49426),
    # Shin Kidou Senki Gundam Wing (90) → Endless Waltz (2273).
    90: (2273,),
    # Kidou Senshi Gundam SEED (93) → Destiny and Stargazer (94, 1215).
    93: (94, 1215),
    # Kidou Senshi Gundam 00 (2581) → 2nd Season and Movie (3927, 6288).
    2581: (3927, 6288),
    # Kidou Senshi Gundam: Tekketsu no Orphans (31251) → 2nd Season and Special Edition (33051, 51569).
    31251: (33051, 51569),
    # Kidou Senshi Gundam Thunderbolt (31973) → 2nd Season and Bandit Flower (34391, 35949).
    31973: (34391, 35949),
    # Gundam: G no Reconguista (23259) → five-part movie series.
    23259: (38714, 40890, 43204, 43205, 43206),
    # Gundam Build Fighters (19319) → Try and companion entries (24625, 35567, 35982).
    19319: (24625, 35567, 35982),
    # Gundam Build Divers (37245) → Re:Rise (40192, 40942).
    37245: (40192, 40942),
    # Kidou Senshi Gundam-san (24835) → ONA and theatre shorts (33225, 52520).
    24835: (33225, 52520),
    # Kidou Senshi Gundam: Suisei no Majo (49828) → Season 2 (53199).
    49828: (53199,),
    # Kidou Senshi Zeta Gundam (85) → recap film trilogy (1967, 1968, 1969).
    85: (1967, 1968, 1969),
    # World Trigger (24405) → Seasons 2-3 (40907, 44940).
    24405: (40907, 44940),
    # Tokyo Mew Mew New (41589) → Season 2 (53097).
    41589: (53097,),
    # Vinland Saga (37521) → Season 2 (49387).
    37521: (49387,),
    # Ao Ashi (49052) → Season 2 (61603).
    49052: (61603,),
    # Black Clover (34572) → Season 2 and Movie (48585, 61967).
    34572: (48585, 61967),
    # Dark Gathering (52505) → Season 2 (62865).
    52505: (62865,),
    # Dead Mount Death Play (53613) → Part 2 (54743).
    53613: (54743,),
    # Druaga no Tou (3230) → The Sword of Uruk (4726).
    3230: (4726,),
    # Fairy Gone (39063) → Part 2 (39811).
    39063: (39811,),
    # Yozakura-san Chi no Daisakusen (53865) → Seasons 2 and 2 Part 2 (60055, 64503).
    53865: (60055, 64503),
    # Kaguya-sama: Love Is War (37999) → later seasons and First Kiss film (40591, 43608, 52198).
    37999: (40591, 43608, 52198),
    # Yahari Ore no Seishun Love Comedy wa Machigatteiru. (14813) → Zoku and Kan (23847, 39547).
    14813: (23847, 39547),
    # Kuroko no Basket (11771) → Seasons 2-3 and films (16894, 24415, 31658, 32869, 32870, 32871).
    11771: (16894, 24415, 31658, 32869, 32870, 32871),
    # Aoki Densetsu Shoot! (1327) → Movie (2682).
    1327: (2682,),
    # Aoki Hagane no Arpeggio (18893) → Movies 1-2 (24919, 24921).
    18893: (24919, 24921),
    # Arakawa Under the Bridge (7647) → x Bridge (9074).
    7647: (9074,),
    # Azuki-chan (1893) → Movie (6095).
    1893: (6095,),
    # B: The Beginning (32827) → Succession (37994).
    32827: (37994,),
    # Birdie Wing (50248) → Season 2 (52229).
    50248: (52229,),
    # Buzzer Beater (406) → 2nd Season (2684).
    406: (2684,),
    # Cardcaptor Sakura (232) → films and Clear Card (371, 372, 33354).
    232: (371, 372, 33354),
    # Chain Chronicle: Haecceitas no Hikari (28833) → trilogy films (33728, 33729, 33730).
    28833: (33728, 33729, 33730),
    # Concrete Revolutio (31147) → The Last Song (32313).
    31147: (32313,),
    # Akagami no Shirayuki-hime (30123) → 2nd Season (31173).
    30123: (31173,),
    # Ano Hi Mita Hana no Namae wo Bokutachi wa Mada Shiranai. (9989) → Movie (15039).
    9989: (15039,),
    # Ansatsu Kyoushitsu (24833) → 2nd Season and recap films (30654, 33513, 62421).
    24833: (30654, 33513, 62421),
    # Bakuten Shoot Beyblade (288) → later seasons and movie (1668, 1669, 1670).
    288: (1668, 1669, 1670),
    # Aria the Animation (477) → later seasons and films (962, 3297, 41674, 48411).
    477: (962, 3297, 41674, 48411),
    # Atashin'chi (3006) → 3D Movie (9796).
    3006: (9796,),
    # Blue Gender (58) → The Warrior (1380).
    58: (1380,),
    # Candy Candy (2800) → films (723, 2801, 2802).
    2800: (723, 2801, 2802),
    # Chuunibyou demo Koi ga Shitai! (14741) → Ren and films (18671, 35608, 37967).
    14741: (18671, 35608, 37967),
    # Digimon Savers (859) → films (2606, 8491).
    859: (2606, 8491),
    # Dirty Pair (424) → The Movie (1796).
    424: (1796,),
    # Chibi Godzilla no Gyakushuu (54644) → Seasons 2-4 (58351, 61765, 64502).
    54644: (58351, 61765, 64502),
    # Diamond no Ace (18689) → later seasons and parts (30230, 38731, 58877, 64505).
    18689: (30230, 38731, 58877, 64505),
    # Douluo Dalu (37150) → direct sequel series (37822, 51836).
    37150: (37822, 51836),
    # Wu Dong Qian Kun (39024) → Seasons 2-7 (42266, 49570, 57183, 60541, 62249, 62717).
    39024: (42266, 49570, 57183, 60541, 62249, 62717),
    # Xingchen Bian (38491) → later seasons (41528, 49386, 50667, 51769, 60787, 62718).
    38491: (41528, 49386, 50667, 51769, 60787, 62718),
    # Zhu Xian (49759) → Seasons 2-3 and continuation film (58509, 61784, 64450).
    49759: (58509, 61784, 64450),
    # Tianbao Fuyao Lu (40735) → Seasons 2-3 (44068, 50405).
    40735: (44068, 50405),
    # Tunshi Xingkong (44218) → Seasons 2-4 (49571, 56523, 56524).
    44218: (49571, 56523, 56524),
    # Bai Yao Pu (41224) → later seasons and story arcs (44067, 50537, 57995, 60562).
    41224: (44067, 50537, 57995, 60562),
    # Zhen Hun Jie (33350) → later seasons and re-edited continuation (40733, 42359, 55790, 59969).
    33350: (40733, 42359, 55790, 59969),
    # Zhen Dao Ge (48759) → later seasons and story arcs (48914, 57468, 62444).
    48759: (48914, 57468, 62444),
    # Ze Tian Ji (31838) → Seasons 2-5 and 2026 continuation (37184, 37185, 38220, 41785, 61562).
    31838: (37184, 37185, 38220, 41785, 61562),
    # Bye Bye, Earth (53626) → Season 2 (59819).
    53626: (59819,),
    # Chickip Dancers (47623) → Seasons 2-3 (53320, 56504).
    47623: (53320, 56504),
    # Chiyu Mahou no Machigatta Tsukaikata (49613) → Season 2 (59467).
    49613: (59467,),
    # Douse, Koishite Shimaunda. (58259) → Season 2 (61325).
    58259: (61325,),
    # Da Erduo Tutu (43881) → Seasons 2-5 and feature films (43882, 43883, 43884, 43885, 50050).
    43881: (43882, 43883, 43884, 43885, 50050),
    # Tian Xin Ge Ge (33739) → Seasons 2-5 (33753, 38246, 44460, 44461).
    33739: (33753, 38246, 44460, 44461),
    # Chao Xian Lie Bing-kai Neng (44032) → 2nd Season (44033).
    44032: (44033,),
    # Chaoji Fangchengshi (52062) → 2nd Season (52063).
    52062: (52063,),
    # Eomma Katuri (47378) → later seasons and feature films.
    47378: (47379, 47380, 57017, 57018, 62176, 62177, 62178),
    # Tobot V (48220) → Season 2 (59140).
    48220: (59140,),
    # Aikatsu Planet! (42653) → Movie (52992).
    42653: (52992,),
    # Aikatsu Stars! (32717) → Movie (31485).
    32717: (31485,),
    # Comic Party (289) → Revolution (706).
    289: (706,),
    # Ginga Tetsudou Monogatari (1490) → II (2717).
    1490: (2717,),
    # Gokinjo Monogatari (852) → Movie (7578).
    852: (7578,),
    # Maple Town Monogatari (2223) → Palm Town entries (5203, 11049).
    2223: (5203, 11049),
    # Saiunkoku Monogatari (957) → 2nd Season (1914).
    957: (1914,),
    # Wellber no Monogatari (2032) → Zwei (3501).
    2032: (3501,),
    # Tantei Opera Milky Holmes (7768) → Season 2 and Movie (11341, 31486).
    7768: (11341, 31486),
    # Tsue to Tsurugi no Wistoria (58059) → Seasons 2-3 (59983, 64500).
    58059: (59983, 64500),
    # Tsuki ga Michibiku Isekai Douchuu (43523) → Seasons 2-3 (49889, 59139).
    43523: (49889, 59139),
    # Wind Breaker (54900) → Season 2 (59160).
    54900: (59160,),
    # Yofukashi no Uta (50346) → Season 2 (58390).
    50346: (58390,),
    # Youkoso Jitsuryoku Shijou Shugi no Kyoushitsu e (35507) → Seasons 2-5 (51096, 51180, 59708, 64463).
    35507: (51096, 51180, 59708, 64463),
    # Tsubasa Chronicle (177) → Season 2 and Movie (807, 969).
    177: (807, 969),
    # Ushio to Tora (29854) → 2nd Season (31098).
    29854: (31098,),
    # World Fool News (18205) → Part II (35332).
    18205: (35332,),
    # Yama no Susume (14355) → later seasons and Next Summit (21435, 35672, 48491).
    14355: (21435, 35672, 48491),
    # Kuroshitsuji (4898) → direct seasons, films, and arcs.
    4898: (6707, 22145, 31812, 55855, 59228),
    # Durarara!! (6746) → x2 trilogy (23199, 27831, 27833).
    6746: (23199, 27831, 27833),
    # Noragami (20507) → Aragoto (30503).
    20507: (30503,),
    # Saiki Kusuo no Psi-nan (33255) → Season 2 and continuation (34612, 40542).
    33255: (34612, 40542),
    # My Hero Academia (31964) → numbered seasons and Final Season (33486, 36456, 38408, 41587, 60098).
    31964: (33486, 36456, 38408, 41587, 60098),
    # Yu Yu Hakusho (392) → The Movie (882).
    392: (882,),
    # Attack on Titan (16498) → Seasons 2, 3, Final Season, and later parts.
    16498: (25777, 35760, 36702, 38524, 39478, 40028, 42091, 48583, 59571),
    # Jujutsu Kaisen (40748) → Season 2 (51009).
    40748: (51009, 59654),
    # Demon Slayer: Kimetsu no Yaiba (38000) → television arcs and seasons.
    38000: (47778, 51019, 55701, 59192, 62546, 62547),
    # Bungo Stray Dogs (31478) -> Seasons 2-5 and Dead Apple.
    31478: (32867, 34944, 38003, 50330, 54898),
    # Golden Kamuy (36028) -> Seasons 2-4 and Final Season.
    36028: (37989, 40059, 50528, 55772),
    # Date A Live (15583) -> Seasons II-V.
    15583: (19163, 24655, 36633, 41461, 52196),
    # Genshiken (240) -> Genshiken 2 (2508).
    240: (2508,),
    # High Score Girl (21877) -> Season II (39570).
    21877: (39570,),
    # I Got a Cheat Skill in Another World (52830) -> Season 2 (63822).
    52830: (63822,),
    # Jochum (58944) -> Season 2 (62231).
    58944: (62231,),
    # Rinne no Lagrange (11227) -> Season 2 (12281).
    11227: (12281,),
    # Seitokai Yakuindomo (8675) -> Season 2 and films (20847, 34504, 40814).
    8675: (20847, 34504, 40814),
    # Starmyu (30375) -> Seasons 2-3 (33362, 36536).
    30375: (33362, 36536),
    # Tonikaku Kawaii (41389) -> Season 2 (50307).
    41389: (50307,),
    # Undead Unluck (52741) -> Season 2 (63177).
    52741: (63177,),
    # My Happy Marriage (51552) -> Season 2 (56701).
    51552: (56701,),
    # New Game! (31953) -> Season 2 (34914).
    31953: (34914,),
    # Hayate no Gotoku! (2026) -> Season 2 (4192).
    2026: (4192,),
    # Kyou kara Maou! (251) -> Season 3 (4080).
    251: (4080,),
    # Maria-sama ga Miteru (158) → Maria-sama ga Miteru 4th (3750).
    158: (444, 3750),
    # Uchuu Senkan Yamato (1650) → Uchuu Senkan Yamato (711), 2 (1651), III (1652).
    1650: (711, 1651, 1652),
    # Aa! Megami-sama! (50) → Movie (304).
    50: (304,),
    # Area 88 (284) → Area 88 Movie (33232).
    284: (33232,),
    # Black Cat (68) → Movie (42585).
    68: (42585,),
    # Black Jack (2213) → related films, specials, and Black Jack 21.
    2213: (1521, 1983, 2214, 4070, 10055, 35859),
    # Cha A Er Zhong Movie (56334) → 5th Season (59381).
    56334: (59381,),
    # Chao Shikong Da Maoxian (47505) → Movie (45073).
    47505: (45073,),
    # D.C.S.S. (291) → D.C.II S.S. (3627).
    291: (3627,),
    # Golden Time (17895) → Movie (36789).
    17895: (36789,),
    # Manga Aesop Monogatari (3180) → Movie (23763).
    3180: (23763,),
    # Peter Pan no Bouken (1638) → Movie (54093).
    1638: (54093,),
    # Rilakkuma (60153) → Special Movie (61528).
    60153: (61528,),
    # Thunder 3 (63418) → Thunder (31259).
    63418: (31259,),
    # Wonder 3 (4088) → Wonder (28085).
    4088: (28085,),
    # Zannen na Ikimono Jiten (38016) → later series and Movie (44026, 49843, 52052, 52053).
    38016: (44026, 49843, 52052, 52053),
    # Beastars Final Season (49469) → Part 2 (61114).
    49469: (61114,),
    # Feng Ling Yu Xiu (36184) → 2nd Season (55692).
    36184: (55692,),
    # Fengkuang Xiao Tang (46688) → Seasons 2-5 (46689, 46690, 46691, 46692).
    46688: (46689, 46690, 46691, 46692),
    # Baki-dou (58573) → Part 2 (63833).
    58573: (63833,),
    # Boku to Roboko (51940) → Movie (55709).
    51940: (55709,),
    # Boukyaku Battery (56165) → 2nd Season (60275).
    56165: (60275,),
    # Boushoku no Berserk (53439) → 2nd Season (64059).
    53439: (64059,),
    # Delicious Party Precure (50281) → Movie (50963).
    50281: (50963,),
    # Pokemon (527) → original series and its direct films.
    527: (
        528,
        1117,
        1118,
        1119,
        1120,
        1121,
        1122,
        1526,
        1527,
        2201,
        2847,
        4026,
        4792,
        4793,
        4794,
        4795,
        5526,
        5529,
        6178,
        7695,
    ),
    # Pokemon Advanced Generation (1564) → its direct planetarium film.
    1564: (42135,),
    # Pokemon Diamond & Pearl (1565) → its direct planetarium films.
    1565: (42136, 42137),
    # Pokemon Best Wishes! (9107) → its numbered arcs (14093, 17115, 17873).
    9107: (14093, 17115, 17873),
    # Pokemon XY (19291) → XY&Z (31592).
    19291: (23849, 31592, 21569, 25805, 31231),
    # Pokemon Sun & Moon (34034) → its direct planetarium film.
    34034: (42139,),
    # Pokemon (2019) (40351) → Mezase Pokemon Master (53874).
    40351: (53874,),
    # InuYasha (249) → its four feature films (449, 450, 451, 452).
    249: (449, 450, 451, 452),
    # xxxHOLiC (861) → feature film (793).
    861: (793,),
    # Kimi ni Todoke (6045) → Season 2 (9656).
    6045: (9656, 56538, 58978),
    # Bakuman. (7674) → Seasons 2-3 (10030, 12365).
    7674: (10030, 12365),
    # Log Horizon (17265) → later seasons (23321, 41109).
    17265: (23321, 41109),
    # Space☆Dandy (20057) → Season 2 (23327).
    20057: (23327,),
    # Ajin (31580) → trilogy recap films and Part 2 (30868, 30869, 30870, 33253).
    31580: (30868, 30869, 30870, 33253),
    # Berserk (32379) → Season 2 and Memorial Edition (34055, 52976).
    32379: (34055, 52976),
    # Mushishi (457) → continuation seasons and feature film (21939, 24701, 28957).
    457: (21939, 24701, 28957),
    # Full Metal Panic! (71) → direct series continuations and recap films (72, 73, 31931, 36342, 36343, 36344).
    71: (72, 73, 31931, 36342, 36343, 36344),
    # Shakugan no Shana (355) → recap film and later seasons (1815, 2787, 6773).
    355: (1815, 2787, 6773),
    # Gantz (384) → Season 2 (395).
    384: (395,),
    # Ghost in the Shell: Stand Alone Complex (467) → 2nd GIG (801).
    467: (801,),
    # Project ARMS (1492) → The 2nd Chapter (1493).
    1492: (1493,),
    # Hiiro no Kakera (12461) → 2nd Season (14645).
    12461: (14645,),
    # Yu☆Gi☆Oh! Zexal (10015) → Zexal Second (15489).
    10015: (15489,),
    # Kindaichi Shounen no Jikenbo (2076) → Returns 2nd Season (31227).
    2076: (31227,),
    # One Room (34392) → Season 2 (36431).
    34392: (36431,),
    # Granblue Fantasy The Animation (31629) → Season 2 (36587).
    31629: (36587,),
    # Yakusoku no Neverland (37779) → Season 2 (39617).
    37779: (39617,),
    # Tensei shitara Slime Datta Ken (37430) → Season 2 (39551).
    37430: (39551,),
    # Play Ball (3768) → 2nd Season (3769).
    3768: (3769,),
    # Hakkenden: Touhou Hakken Ibun (15613) → Season 2 (18055).
    15613: (18055,),
    # Kakumeiki Valvrave (16668) → recap ONA and Season 2 (21077, 18295).
    16668: (21077, 18295),
    # Gin no Saji (16918) → Season 2 (19363).
    16918: (19363,),
    # Baby Steps (21185) → Season 2 (27663).
    21185: (27663,),
    # Kyoukai no Rinne (28423) → Seasons 2-3 (31610, 34106).
    28423: (31610, 34106),
    # Hoozuki no Reitetsu (20431) → Seasons 2-3 (35075, 37029).
    20431: (35075, 37029),
    # Piano no Mori (TV) (36652) → Season 2 (37975).
    36652: (37975,),
    # Accel World (11759) → Infinite∞Burst film (31763).
    11759: (31763,),
    # Kaiketsu Zorori (3638) → feature film (35074).
    3638: (35074,),
    # Aldnoah.Zero (22729) → Part 2 and recap film (27655, 60666).
    22729: (27655, 60666),
    # Kaitou Joker (24909) → Seasons 2-4 (28869, 31670, 33490).
    24909: (28869, 31670, 33490),
    # Baxian (45072) → Baxian! (64382).
    45072: (64382,),
    # Metamorphose (31833) → Metamorphose. (60264).
    31833: (60264,),
    # Socket (7416) → -Socket- (59356).
    7416: (59356,),
    # Hajime no Ippo (263) → New Challenger (5258).
    263: (5258,),
    # Tian Guan Cifu (40730) → Season 2 (50399).
    40730: (50399,),
    # Doupo Cangqiong (36491) → later seasons (37176, 38436, 44412, 49701, 51039).
    36491: (37176, 38436, 44412, 49701, 51039),
    # Kizumonogatari I (9260) → Parts II-III (31757, 31758).
    9260: (31757, 31758, 56609),
    # Kizumonogatari Part 3 (31758) → Koyomi Vamp (56609).
    31758: (56609,),
    # Owarimonogatari (31181) → Zoku Owarimonogatari (36999).
    31181: (36999,),
    # Mushoku Tensei Season 1 (39535) → Season 2 (51179).
    39535: (51179, 55888, 59193),
    # Ore dake Level Up na Ken (52299) → Season 2 and recap film (58567, 59841).
    52299: (58567, 59841),
    # Uma Musume: Pretty Derby (35249) → Road to the Top (51761).
    35249: (51761,),
    # One-Punch Man (30276) -> Seasons 2-3 and Season 3 Part 2.
    30276: (34134, 52807, 63193),
    # Mob Psycho 100 (32182) -> Seasons II-III.
    32182: (50172,),
    # Violet Evergarden (33352) → Gaiden and the feature film (37987, 39741).
    33352: (39741,),
    # Laid-Back Camp (34798) -> Seasons II-IV and the feature film.
    34798: (38474, 38475, 53410, 60267),
    # Overlord (29803) → television seasons and theatrical films (35073, 37675, 48895, 48896).
    29803: (34161, 34428, 35073, 37675, 48895),
    # KonoSuba (30831) → television seasons and Legend of Crimson film (32937, 38040, 49458).
    30831: (32937, 38040, 49458),
    # Haikyu!! (20583) → television seasons and continuation films.
    20583: (28891, 29755, 30364, 32935, 35110, 35111, 38883, 40776, 52742),
    # Blue Lock (49596) → Episode Nagi film; retain unrelated spin-offs as separate families.
    49596: (54866,),
    # Steins;Gate (9253) → Steins;Gate 0 and the direct sequel film (11577, 30484).
    9253: (11577, 30484),
    # Psycho-Pass (13601) -> numbered seasons, films, and First Inspector.
    13601: (21339, 37440, 37441, 37442, 39491, 40858, 52747),
    # Made in Abyss (34599) -> recap films, continuation film, and later TV season.
    34599: (36862, 37514, 37515, 41084, 54250),
    # Sword Art Online (11757) -> main adaptation seasons and direct films.
    11757: (21881, 31765, 36474, 39597, 40540, 42916, 50275),
    # Sword Art Online Alternative: Gun Gale Online (36475) -> Season II and Gala (55994, 59968).
    36475: (55994, 59968),
    # DanMachi (28121) -> main seasons and Arrow of the Orion film.
    28121: (37348, 40454, 47164, 53111, 57066, 63442),
    # Re:ZERO (31240) -> main seasons, direct films, and Manner variants.
    31240: (36286, 39921, 41590, 42203, 54857, 61316),
    # Fullmetal Alchemist: Brotherhood (5114) -> Sacred Star of Milos for this adaptation.
    5114: (9135, 10842),
    # Hunter x Hunter (2011) (11061) -> two films; the 1999 adaptation stays separate.
    11061: (13271, 19951),
    # Slam Dunk (170) → films and continuation entries (1764, 1861, 2498, 2499).
    170: (1764, 1861, 2498, 2499),
    # Naruto (20) → direct films, Rock Lee spin-off, The Last/Lost Tower films, and continuation entry.
    20: (442, 936, 2144, 4437, 6325, 8246, 10589, 10659, 10686, 12979, 13667, 16870, 54688),
}
