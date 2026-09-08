"""Curated same-story links for incomplete catalogue relation data."""

MANUAL_RELATIONSHIPS: dict[int, tuple[int, ...]] = {
    # Higurashi no Naku Koro ni (934) → Kai (1889), Gou (41006), Sotsu (48488), Shinsaku (64449).
    934: (1889, 41006, 48488, 64449),
    # Tokyo Ghoul (22319) → √A (27899), :re (36511), :re 2nd Season (37799).
    22319: (27899, 36511, 37799),
    # My Hero Academia (31964) → numbered seasons and Final Season (33486, 36456, 38408, 41587, 60098).
    31964: (33486, 36456, 38408, 41587, 60098),
    # Yu Yu Hakusho (392) → The Movie (882).
    392: (882,),
    # Attack on Titan (16498) → Seasons 2, 3, Final Season, and later parts.
    16498: (35760, 36702, 38524, 39478, 40028, 48583, 59571),
    # Jujutsu Kaisen (40748) → Season 2 (51009).
    40748: (51009, 59654),
    # Demon Slayer: Kimetsu no Yaiba (38000) → television arcs and seasons.
    38000: (47778, 51019, 55701, 59192, 62546, 62547),
    # Bungo Stray Dogs (31478) -> Seasons 2-5.
    31478: (34944, 38003, 50330, 54898),
    # Golden Kamuy (36028) -> Seasons 2-4 and Final Season.
    36028: (40059, 50528, 55772),
    # Date A Live (15583) -> Seasons II-V.
    15583: (19163, 24655, 36633, 41461, 52196),
    # One-Punch Man (30276) -> Seasons 2-3 and Season 3 Part 2.
    30276: (52807, 63193),
    # Mob Psycho 100 (32182) -> Seasons II-III.
    32182: (50172,),
    # Violet Evergarden (33352) → Gaiden and the feature film (37987, 39741).
    33352: (39741,),
    # Laid-Back Camp (34798) -> Seasons II-IV and the feature film.
    34798: (38475, 53410, 60267),
    # Overlord (29803) → television seasons and theatrical films (35073, 37675, 48895, 48896).
    29803: (37675, 48895, 48896),
    # KonoSuba (30831) → television seasons and Legend of Crimson film (32937, 38040, 49458).
    30831: (38040, 49458),
    # Haikyu!! (20583) → television seasons and direct continuation film (28891, 32935, 38883, 40776, 52742).
    20583: (32935, 38883, 40776, 52742),
    # Blue Lock (49596) → Episode Nagi film; retain unrelated spin-offs as separate families.
    49596: (54866,),
    # Steins;Gate (9253) → Steins;Gate 0 and the direct sequel film (11577, 30484).
    9253: (11577, 30484),
    # Psycho-Pass (13601) -> numbered seasons, films, and First Inspector.
    13601: (21339, 37440, 37441, 37442, 39491, 40858, 52747),
    # Made in Abyss (34599) -> recap films, continuation film, and later TV season.
    34599: (41084, 54250),
    # Sword Art Online (11757) -> main adaptation seasons and direct films.
    11757: (31765, 36474, 39597, 40540, 50275),
    # Sword Art Online Alternative: Gun Gale Online (36475) -> Season II (55994).
    36475: (),
    # DanMachi (28121) -> main seasons and Arrow of the Orion film.
    28121: (37348, 40454, 47164, 53111, 57066, 63442),
    # Re:ZERO (31240) -> main seasons, direct films, and Manner variants.
    31240: (36286, 39921, 41590, 42203, 54857, 61316),
    # Fullmetal Alchemist: Brotherhood (5114) -> Sacred Star of Milos for this adaptation.
    5114: (9135,),
    # Hunter x Hunter (2011) (11061) -> two films; the 1999 adaptation stays separate.
    11061: (13271, 19951),
    # Slam Dunk (170) → films and continuation entries (1764, 1861, 2498, 2499).
    170: (1764, 1861, 2498, 2499),
    # Naruto (20) → direct films and the current continuation entry.
    20: (442, 936, 2144, 4437, 6325, 10589, 10659, 10686, 13667, 54688),
    # Gintama (918) → The Final feature film.
    918: (39486,),
    # Madoka Magica (9756) → Concept Movie; Magia Record remains a separate setting.
    9756: (32153,),
}
