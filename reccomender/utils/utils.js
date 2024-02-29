import { checkFileExists, readAndProcessFile } from '../dataAccess/readFile.js';
import { filterAnimeData } from './filter.js';

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

export { findMax, findMin, sortData, initializeDataFile };
