import { cleanDuration, cleanPremiered, cleanRating } from './clean.js';
import { handleMissingData } from './fetchData.js';
import { checkFileExists, readAndProcessFile } from './readFile.js';
import { createMapping } from './stats.js';
import { writeData } from './writeFile.js';

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
    const excludedTypes = ['OVA', 'Special', 'Music', 'PV', 'TV Special'];
    const excludedGenres = ['Erotica', 'Hentai'];
    const filteredData = data.filter((d) => {
        return !excludedTypes.includes(d.type) && !d.genres.some((genre) => excludedGenres.includes(genre));
    });
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
        entry.malID = parseInt(entry.malID, 10);
        entry.durationMinutes = cleanDuration(entry.durationText);
        entry.premiered = cleanPremiered(entry.premiered, entry.season, entry.year);
        entry.rating = cleanRating(entry.rating);
    });
    filteredData = filterAnimeData(filteredData);
    await writeData('entries.json', filteredData);
    return filteredData;
}

async function returnFilteredData(data, property) {
    const uniqueValues = returnUniqueArray(data, property);
    const result = uniqueValues.map((value) => {
        const filteredData = data.filter((d) => {
            if (Array.isArray(d[property])) {
                if (d[property].length === 0) {
                    return value === 'Unknown';
                }
                return d[property].includes(value);
            }
            return d[property] === value;
        });

        return {
            key: value,
            values: filteredData,
        };
    });

    return result;
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
        const data = await readAndProcessFile(fileName, 'AnimeEntry');
        const filteredData = filterAnimeData(data);
        return filteredData;
    }
}

export {
    writeData,
    findMax,
    findMin,
    filterAnimeData,
    sortData,
    returnUniqueArray,
    constructDataFile,
    initializeDataFile,
    returnFilteredData,
};
