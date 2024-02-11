class AnimeEntry{
    constructor(id, title, rank, type, episodeCount, aired, members, malURL, imageURL, score){
        this.id = id;
        this.title = title;
        this.rank = rank;
        this.type = type;
        this.episodeCount = episodeCount;
        this.aired = aired;
        this.members = members;
        this.malURL = malURL;
        this.imageURL = imageURL;
        this.score = score;
    }
}

module.exports = {
    AnimeEntry
}