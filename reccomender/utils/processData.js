const { AnimeEntry } = require("../models/AnimeEntry");
const { UserInteraction } = require("../models/UserInteraction");
const { cleanRating, cleanDuration, cleanArray, findSeasonalYear, cleanPremiered } = require("./clean");

function parseOrDefault(value, defaultValue =  0, type = 'int') {
    if (type === 'int') {
        return parseInt(value,  10) || defaultValue;
    } else if (type === 'float') {
        return parseFloat(value) || defaultValue;
    } else {
        throw new Error('Invalid type specified for parseOrDefault. Use "int" or "float".');
    }
}

function cleanString(value) {
    return value.replace('UNKNOWN', 'Unknown');
}

async function processAnimeData(data) {
    const animeEntries = data.map((row) => {
        const [
            malID,
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
            durationText,
            rating,
            rank,
            popularity,
            favourites,
            scoredBy,
            members,
            imageURL,
        ] = row;

        const cleanedGenres = cleanArray(genres);
        const cleanedProducers = cleanArray(producers);
        const cleanedLicensors = cleanArray(licensors);
        const cleanedStudios = cleanArray(studios);

        const cleanedPremiered = cleanString(premiered);
        const { season, year } = findSeasonalYear(cleanedPremiered, aired);
        const cleanedPremieredWithSeason = cleanPremiered(cleanedPremiered, season, year);

        const cleanedType = cleanString(type);
        const cleanedSource = cleanString(source);
        const durationMinutes = cleanDuration(durationText);
        const cleanedRating = cleanRating(rating);

        return new AnimeEntry(
            malID,
            name,
            cleanString(englishName),
            cleanString(otherName),
            parseOrDefault(score,  0, 'float'),
            cleanedGenres,
            synopsis,
            cleanedType,
            parseOrDefault(episodes,  0, 'int'),
            aired,
            cleanedPremieredWithSeason,
            season,
            year,
            status,
            cleanedProducers,
            cleanedLicensors,
            cleanedStudios,
            cleanedSource,
            durationText,
            durationMinutes,
            cleanedRating,
            parseOrDefault(rank,  0, 'int'),
            parseOrDefault(popularity,  0, 'int'),
            parseOrDefault(favourites,  0, 'int'),
            parseOrDefault(scoredBy,  0, 'int'),
            parseOrDefault(members,  0, 'int'),
            imageURL,
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