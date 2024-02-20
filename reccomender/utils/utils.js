const { parse } = require('csv-parse');
const { cleanArray, findSeasonalYear, cleanDuration, cleanRating, cleanPremiered } = require('./clean');
const { AnimeEntry } = require('../models/AnimeEntry');
const { UserInteraction } = require('../models/UserInteraction');
const { checkFileExists, readAndProcessFile } = require('./readFile');
const { handleMissingData } = require('./fetchData');
const { writeData } = require('./writeFile');

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
    const excludedTypes = ['ONA', 'OVA', 'Special', 'Music', 'PV', 'TV Special'];
    const excludedGenres = ['Erotica', 'Hentai'];
    const filteredData = data.filter((d) => !excludedGenres.includes(d.genres) && !excludedTypes.includes(d.type));
    return filteredData;
}

async function constructDataFile() {
    console.log('Starting to construct data files by reading input csv file.');
    const animeCSV = await readAndProcessFile('../data/anime-dataset-2023.csv', 'AnimeEntry');
    let filteredData = filterAnimeData(animeCSV);
    filteredData = await handleMissingData(filteredData);
    filteredData.sort((a, b) => a.title.localeCompare(b.title));
    filteredData.forEach((entry, index) => {
        entry.id = index;
        entry.durationMinutes = cleanDuration(entry.durationText);
        entry.premiered = cleanPremiered(entry.premiered, entry.season, entry.year);
        entry.rating = cleanRating(entry.rating);
    });
    await writeData('entries.json', filteredData);
    return filteredData;
}

async function initializeDataFile() {
    const fileName = 'entries.json';
    const fileExists = await checkFileExists(fileName);

    if (!fileExists) {
        console.log(`The file '${fileName}' does not exist. Constructing data files...`);
        const data = await constructDataFile();
        return data;
    } else {
        console.log(`The file '${fileName}' already exists. Reading data...`);
        return await readAndProcessFile(fileName,  'AnimeEntry');
    }
}


module.exports = {
    writeData,
    findMax,
    findMin,
    filterAnimeData,
    sortData,
    returnUniqueArray,
    constructDataFile,
    initializeDataFile,
};
