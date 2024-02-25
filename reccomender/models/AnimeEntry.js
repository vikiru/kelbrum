class AnimeEntry {
    constructor(
        malID,
        title,
        englishName,
        otherName,
        score,
        genres,
        synopsis,
        type,
        episodes,
        aired,
        premiered,
        season,
        year,
        status,
        producers,
        licensors,
        studios,
        source,
        durationText,
        durationMinutes,
        rating,
        rank,
        popularity,
        favourites,
        scoredBy,
        members,
        imageURL,
    ) {
        this.id = -1;
        this.malID = malID;
        this.title = title;
        this.englishName = englishName;
        this.otherName = otherName;
        this.titles = [];
        this.score = score;
        this.genres = genres;
        this.themes = [];
        this.demographics = [];
        this.synopsis = synopsis;
        this.type = type;
        this.episodes = episodes;
        this.aired = aired;
        this.premiered = premiered;
        this.season = season;
        this.year = year;
        this.status = status;
        this.producers = producers;
        this.licensors = licensors;
        this.studios = studios;
        this.source = source;
        this.durationText = durationText;
        this.durationMinutes = durationMinutes;
        this.rating = rating;
        this.rank = rank;
        this.popularity = popularity;
        this.favourites = favourites;
        this.scoredBy = scoredBy;
        this.members = members;
        this.imageURL = imageURL;
        this.trailerURL = 'Unknown';
        this.pageURL = `https://myanimelist.net/anime/${malID}/${title}`;
    }
}

export { AnimeEntry };
