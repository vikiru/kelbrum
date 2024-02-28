import { AnimeEntry } from '../models/AnimeEntry.js';
import { UserInteraction } from '../models/UserInteraction.js';
import { cleanArray, cleanDuration, cleanPremiered, cleanRating, findSeasonalYear } from './clean.js';

/**
 * Parses the input value to the specified type, or returns the default value if parsing fails.
 *
 * @param {any} value - The value to parse.
 * @param {number} defaultValue - The default value to return if parsing fails. Default is 0.
 * @param {string} type - The type to parse the value to. Options are "int" or "float". Default is "int".
 * @returns {number} The parsed value or the default value if parsing fails.
 */
function parseOrDefault(value, defaultValue = 0, type = 'int') {
    if (type === 'int') {
        return parseInt(value, 10) || defaultValue;
    } else if (type === 'float') {
        return parseFloat(value) || defaultValue;
    } else {
        throw new Error('Invalid type specified for parseOrDefault. Use "int" or "float".');
    }
}

/**
 * Replaces 'UNKNOWN' with 'Unknown' in the given value.
 *
 * @param {string} value - The string to be cleaned
 * @returns {string} The cleaned string
 */
function cleanString(value) {
    return value.replace('UNKNOWN', 'Unknown');
}

/**
 * Processes the provided anime data and creates an array of AnimeEntry objects.
 *
 * @param {Array} data - The anime data to be processed
 * @returns {Array} An array of AnimeEntry objects
 */
async function processAnimeData(data) {
    const animeEntries = data.map((row) => {
        const malID = row.anime_id;
        const name = row.Name;
        const englishName = row['English name'];
        const otherName = row['Other name'];
        const score = row.Score;
        const genres = row.Genres;
        const synopsis = row.Synopsis;
        const type = row.Type;
        const episodes = row.Episodes;
        const aired = row.Aired;
        const premiered = row.Premiered;
        const status = row.Status;
        const producers = row.Producers;
        const licensors = row.Licensors;
        const studios = row.Studios;
        const source = row.Source;
        const durationText = row.Duration;
        const rating = row.Rating;
        const rank = row.Rank;
        const popularity = row.Popularity;
        const favourites = row.Favorites;
        const scoredBy = row['Scored By'];
        const members = row.Members;
        const imageURL = row['Image URL'];

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
            parseOrDefault(score, 0, 'float'),
            cleanedGenres,
            synopsis,
            cleanedType,
            parseOrDefault(episodes, 0, 'int'),
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
            parseOrDefault(rank, 0, 'int'),
            parseOrDefault(popularity, 0, 'int'),
            parseOrDefault(favourites, 0, 'int'),
            parseOrDefault(scoredBy, 0, 'int'),
            parseOrDefault(members, 0, 'int'),
            imageURL,
        );
    });

    return animeEntries;
}

/**
 * Processes user interaction data to create user objects.
 *
 * @param {Array} data - The user interaction data to be processed
 * @returns {Array} An array of user objects
 */
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

export { processAnimeData, processUserInteractionData };
