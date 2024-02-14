const { parse } = require('csv-parse');
const { cleanArray, findSeasonalYear, cleanDuration, cleanRating } = require('./clean');
const { AnimeEntry } = require('../models/AnimeEntry');
const { UserInteraction } = require('../models/UserInteraction');
const { readFile } = require('./readFile');
const { handleMissingData } = require('./fetchData');
const { writeFile } = require('./writeFile');

function findMax(data, property) {
    const propArr = data.map((d) => Number(d[property])).filter((arrItem) => !isNaN(arrItem));
    return Math.max(...propArr);
}

function findMin(data, property) {
    const propArr = data.map((d) => Number(d[property])).filter((arrItem) => !isNaN(arrItem));
    return Math.min(...propArr);
}

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

function sortData(data) {
    const firstElement = data[0];
    const type = typeof firstElement;
    if (type === 'string') {
        data.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    } else if (type === 'number') {
        data.sort((a, b) => a - b);
    }
    return data;
}

function returnUniqueArray(data, property, filter = []) {
    const allPropertyValues = data.flatMap((d) => d[property]).filter((value) => !filter.includes(value));
    const uniquePropertyValues = Array.from(new Set(allPropertyValues)).filter((a) => a !== '');
    return uniquePropertyValues;
}

function filterAnimeData(data) {
    const excludedTypes = ['ONA', 'OVA', 'Special', 'Music', 'Unknown', 'TV Special'];
    const filteredData = data.filter((d) => !d.genres.includes('Hentai') && !excludedTypes.includes(d.type));
    return filteredData;
}

async function constructDataFiles() {
    // const animeData = await readFile('../data/anime-dataset-2023.csv', 'csv', 'AnimeEntry');
    const animeData = await readFile('../data/entries.json', 'json', 'AnimeEntry');
    const filteredData = filterAnimeData(animeData);
    await handleMissingData(filteredData);
    await writeFile('entries.json', filteredData);
    const allowedKeys = [
        'aired',
        'genres',
        'type',
        'episodes',
        'season',
        'year',
        'status',
        'producers',
        'licensors',
        'studios',
        'source',
        'duration',
        'rating',
    ];
    const specialKeys = ['duration', 'rating', 'season', 'year', 'source', 'premiered'];

    for (const key of allowedKeys) {
        const fileName = `${key}.json`;
        const data = specialKeys.includes(key)
            ? returnUniqueArray(filteredData, key, ['Unknown'])
            : returnUniqueArray(filteredData, key);
        await writeFile(fileName, sortData(data));
    }
    return filteredData;
}

module.exports = {
    writeFile,
    findMax,
    findMin,
    filterAnimeData,
    processAnimeData,
    processUserInteractionData,
    sortData,
    returnUniqueArray,
    constructDataFiles,
    cleanArray,
    cleanDuration,
    cleanRating,
};
