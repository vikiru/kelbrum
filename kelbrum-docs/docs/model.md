---
title: 🧩 Model Overview
---

## 🧩 Model Overview

[AnimeEntry](https://github.com/vikiru/recommender/models/AnimeEntry.js): This is the main model which is meant to represent a distinct anime entry, including
properties such as its `title`, `type`, `genres`, `studios`, `score`, `pageURL`, etc.

This is the primary and at present, the only model used within this project. Every entry within the original dataset is read row by row and processed into this model.

An example of an **AnimeEntry** model can be seen below:

```json
 "id": 5183,
 "malID": 11061,
 "title": "Hunter x Hunter (2011)",
 "englishName": "Hunter x Hunter",
 "otherName": "HUNTER×HUNTER（ハンター×ハンター）",
 "titles": [
    "Hunter x Hunter",
    "HxH",
    "HUNTER×HUNTER（ハンター×ハンター）",
    "Hunter X Hunter: Cazadores de Tesoros"
 ],
 "score": 9.04,
 "genres": [
    "Action",
    "Adventure",
    "Fantasy"
 ],
 "themes": [],
 "demographics": [
    "Shounen"
 ],
 "synopsis": "Hunters devote themselves to accomplishing hazardous tasks, all from traversing the world's uncharted territories to locating rare items and monsters. Before becoming a Hunter, one must pass the Hunter Examination—a high-risk selection process in which most applicants end up handicapped or worse, deceased.\n\nAmbitious participants who challenge the notorious exam carry their own reason. What drives 12-year-old Gon Freecss is finding Ging, his father and a Hunter himself. Believing that he will meet his father by becoming a Hunter, Gon takes the first step to walk the same path.\n\nDuring the Hunter Examination, Gon befriends the medical student Leorio Paladiknight, the vindictive Kurapika, and ex-assassin Killua Zoldyck. While their motives vastly differ from each other, they band together for a common goal and begin to venture into a perilous world.",
 "type": "TV",
 "episodes": 148,
 "aired": "Oct 2, 2011 to Sep 24, 2014",
 "premiered": "fall 2011",
 "season": "fall",
 "year": 2011,
 "status": "Finished Airing",
 "producers": [
    "Nippon Television Network",
    "Shueisha",
    "VAP"
 ],
 "licensors": [
    "VIZ Media"
 ],
 "studios": [
    "Madhouse"
 ],
 "source": "Manga",
 "durationText": "23 min per ep",
 "durationMinutes": 23,
 "rating": "PG-13",
 "rank": 10,
 "popularity": 10,
 "favourites": 200265,
 "scoredBy": 1651790,
 "members": 2656870,
 "imageURL": "https://cdn.myanimelist.net/images/anime/1337/99013.jpg",
 "trailerURL": "Unknown",
 "pageURL": "https://myanimelist.net/anime/11061/Hunter x Hunter (2011)",
```

For the purposes of the recommendation system, not all properties are applicable. Through the development process, the following properties were used:

-   `score`
-   `genres`
-   `themes`
-   `demographics`
-   `type`
-   `episodes`
-   `premiered`
-   `season`
-   `year`
-   `status`
-   `producers`
-   `licensors`
-   `studios`
-   `source`
-   `durationMinutes`
-   `rating`
-   `rank`
-   `popularity`
-   `favourites`
-   `scoredBy`
-   `members`

However, in the end not all properties were used in the current system. Additionally, there is potential for expanding upon these existing properties and utilizing additonal properties such as `synopsis`, `titles` and a new property `relations` which would contain information about anime and manga related to a given anime entry, this would include information such as prequels, sequels, etc.
