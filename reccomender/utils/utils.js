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
    const excludedTypes = ['ONA', 'OVA', 'Special', 'Music', 'PV', 'TV Special'];
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
    const uniqueMapping = createMapping(uniqueValues);

    const filteredData = {};

    data.forEach((entry) => {
        const propertyValue = entry[property];
        const type = Array.isArray(propertyValue) ? 'array' : 'single';

        if (type === 'array') {
            if (propertyValue.length === 0) {
                const lastId = Object.keys(uniqueMapping).reduce(
                    (maxId, key) => Math.max(maxId, uniqueMapping[key]),
                    -1,
                );
                const unknownId = lastId + 1;
                const unknownKey = 'Unknown';
                uniqueMapping[unknownKey] = unknownId;
                propertyValue.push(unknownKey);
            }

            propertyValue.forEach((value) => {
                const mappingId = uniqueMapping[value];
                if (mappingId !== undefined) {
                    if (!filteredData[mappingId]) {
                        filteredData[mappingId] = {
                            key: value,
                            values: [],
                        };
                    }

                    filteredData[mappingId].values.push(entry);
                }
            });
        } else {
            const mappingId = uniqueMapping[propertyValue];
            if (mappingId !== undefined) {
                if (!filteredData[mappingId]) {
                    filteredData[mappingId] = {
                        key: propertyValue,
                        values: [],
                    };
                }

                filteredData[mappingId].values.push(entry);
            }
        }
    });

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
