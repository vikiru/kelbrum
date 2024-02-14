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
    console.log('Starting to construct data files by reading input csv file.');
    //const animeData = await readFile('../data/anime-dataset-2023.csv', 'csv', 'AnimeEntry');
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
    sortData,
    returnUniqueArray,
    constructDataFiles,
};
