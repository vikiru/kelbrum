class AnimeEntry {
    constructor(id, title, englishName, otherName, score, genres, synopsis, type, episodes, aired, premiered, status, producers, licensors, studios, source, duration, rating, rank, popularity, favourites, scoredBy, members, imageURL, pageURL) {
        this.id = id;
        this.title = title;
        this.englishName = englishName;
        this.otherName = otherName;
        this.score = score;
        this.genres = genres;
        this.synopsis = synopsis;
        this.type = type;
        this.episodes = episodes;
        this.aired = aired;
        this.premiered = premiered;
        this.status = status;
        this.producers = producers;
        this.licensors = licensors;
        this.studios = studios;
        this.source = source;
        this.duration = duration;
        this.rating = rating;
        this.rank = rank;
        this.popularity = popularity;
        this.favourites = favourites;
        this.scoredBy = scoredBy;
        this.members = members;
        this.imageURL = imageURL;
        this.pageURL = pageURL;
    }
}

module.exports = {
    AnimeEntry
}