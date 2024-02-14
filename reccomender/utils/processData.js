const { AnimeEntry } = require("../models/AnimeEntry");
const { UserInteraction } = require("../models/UserInteraction");
const { cleanRating, cleanDuration, cleanArray, findSeasonalYear } = require("./clean");

async function processAnimeData(data) {
    const animeEntries = data.map((row) => {
        let [
            animeID,
            name,
            englishName,
            otherName,
            score,
            genres,
            synopsis,
            type,
            episodes,
            aired,
            premiered,
            status,
            producers,
            licensors,
            studios,
            source,
            duration,
            rating,
            rank,
            popularity,
            favourites,
            scoredBy,
            members,
            imageURL,
        ] = row;
        animeID = parseInt(animeID, 10);
        englishName = englishName.replace('UNKNOWN', 'Unknown');
        otherName = otherName.replace('Unknown', 'Unknown');
        score = parseFloat(score) || 0;
        genres = cleanArray(genres);
        type = type.replace('UNKNOWN', 'Unknown');
        episodes = parseInt(episodes, 10) || 0;
        premiered = premiered.replace('UNKNOWN', 'Unknown');
        const { season, year } = findSeasonalYear(premiered, aired);
        producers = cleanArray(producers);
        licensors = cleanArray(licensors);
        studios = cleanArray(studios);
        source = source.replace('UNKNOWN', 'Unknown');
        duration = cleanDuration(duration);
        rating = cleanRating(rating);
        rank = parseInt(rank, 10) || 0;
        popularity = parseInt(popularity, 10) || 0;
        favourites = parseInt(favourites, 10) || 0;
        scoredBy = parseInt(scoredBy, 10) || 0;
        members = parseInt(members, 10) || 0;
        const pageURL = `https://myanimelist.net/anime/${animeID}/${name.replaceAll(' ', '_')}`;

        return new AnimeEntry(
            animeID,
            name,
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
            duration,
            rating,
            rank,
            popularity,
            favourites,
            scoredBy,
            members,
            imageURL,
            pageURL,
        );
    });
    return animeEntries;
}

async function processUserInteractionData(data) {
    const users = [];
    const uniqueUserIDs = Array.from(new Set(data.map((d) => d[0])));
    for (const id of uniqueUserIDs) {
        const relevantRows = data.filter((row) => row[0] === id);
        const ratings = relevantRows.map((row) => ({
            animeID: row[2],
            animeTitle: row[3],
            rating: row[4],
        }));
        const user = new UserInteraction(id, ratings);
        users.push(user);
    }
    return users;
}

module.exports = {
    processAnimeData,
    processUserInteractionData
}