import { checkFileExists, readAndProcessFile } from '../dataAccess/readFile.js';
import { cleanDuration, cleanPremiered, cleanRating } from './clean.js';
import { handleMissingData } from './fetchData.js';
import { createMapping } from './stats.js';

/**
 * Finds the maximum value of a specified property in the given data array.
 *
 * @param {Array} data - The array of objects containing the data.
 * @param {string} property - The property to find the maximum value of.
 * @returns {number} The maximum value of the specified property.
 */
function findMax(data, property) {
    const propArr = data.map((d) => Number(d[property])).filter((arrItem) => !isNaN(arrItem));
    return Math.max(...propArr);
}

/**
 * Finds the minimum value of a specified property in the given data array.
 *
 * @param {Array} data - The array of objects containing the data.
 * @param {string} property - The property of the objects to find the minimum value for.
 * @returns {number} The minimum value of the specified property.
 */
function findMin(data, property) {
    const propArr = data.map((d) => Number(d[property])).filter((arrItem) => !isNaN(arrItem));
    return Math.min(...propArr);
}

/**
 * Sorts the input data based on the type of the first element.
 *
 * @param {Array} data - The input data to be sorted
 * @returns {Array} The sorted data
 */
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

/**
 * Returns an array of unique values from the specified property in the input data, excluding values present in the
 * filter array.
 *
 * @param {Array} data - The input data array containing objects with the specified property.
 * @param {string} property - The property name to extract values from.
 * @param {Array} [filter=[]] - The array of values to exclude from the result. Default is `[]`
 * @returns {Array} UniquePropertyValues - An array of unique values from the specified property.
 */
function returnUniqueArray(data, property, filter = []) {
    const allPropertyValues = data.flatMap((d) => d[property]).filter((value) => !filter.includes(value));
    const uniquePropertyValues = Array.from(new Set(allPropertyValues)).filter((a) => a !== '');
    return uniquePropertyValues;
}

/**
 * Filters anime data based on excluded types and genres.
 *
 * @param {array} data - The array of anime data to be filtered.
 * @returns {array} The filtered array of anime data.
 */
function filterAnimeData(data) {
    const excludedTypes = ['OVA', 'Special', 'Music', 'PV', 'TV Special'];
    const excludedGenres = ['Erotica', 'Hentai'];
    const filteredData = data.filter((d) => {
        return !excludedTypes.includes(d.type) && !d.genres.some((genre) => excludedGenres.includes(genre));
    });
    return filteredData;
}

/**
 * Returns filtered data based on unique values of a specified property.
 *
 * @param {Array} data - The input data array
 * @param {string} property - The property to filter by
 * @returns {Array} An array of objects with key-value pairs of unique values and their filtered data
 */
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

/**
 * Initializes the data file by checking if it exists, constructing it if it doesn't, and reading and filtering the data
 * if it does.
 *
 * @returns {Promise} The initialized data file.
 */
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

export { findMax, findMin, filterAnimeData, sortData, returnUniqueArray, initializeDataFile, returnFilteredData };
