import { Buffer } from 'buffer';
import fs from 'fs/promises';
import Papa from 'papaparse';
import path from 'path';

import { processAnimeData, processUserInteractionData } from '../utils/processData.js';

/**
 * Check if the specified file exists.
 *
 * @param {string} fileName - The name of the file to check
 * @returns {boolean} True if the file exists, false if it does not
 */
async function checkFileExists(fileName) {
    const filePath = path.resolve(__dirname, `../data/${fileName}`);
    try {
        await fs.access(filePath, fs.constants.F_OK);
        return true;
    } catch (error) {
        if (error.code === 'ENOENT') {
            return false;
        } else {
            throw error;
        }
    }
}

/**
 * Asynchronously reads the content of the specified file.
 *
 * @param {string | File} filePathOrFile - The path to the file or a File object.
 * @returns {Promise<string>} A promise that resolves with the content of the file as a string.
 */
async function readFile(filePathOrFile) {
    if (typeof window === 'undefined') {
        return fs.promises.readFile(filePathOrFile, 'utf8');
    } else {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (event) => resolve(event.target.result);
            reader.onerror = (error) => reject(error);
            reader.readAsText(filePathOrFile);
        });
    }
}

/**
 * Read the content of a JSON file and parse it into a JavaScript object.
 *
 * @param {string | Buffer | URL | number} filePathOrFile - The path to the JSON file or a File object.
 * @returns {Promise<Object>} A Promise that resolves to the parsed JSON object.
 */
async function readJSONFile(filePathOrFile) {
    const fileData = await readFile(filePathOrFile);
    return JSON.parse(fileData);
}

/**
 * Asynchronously reads a CSV file and parses the data.
 *
 * @param {string | File} filePathOrFile - The path to the CSV file or a File object.
 * @returns {object[]} The parsed data from the CSV file.
 */
async function readCSVFile(filePathOrFile) {
    const fileData = await readFile(filePathOrFile);
    const results = Papa.parse(fileData, {
        header: true,
        skipEmptyLines: true,
    });
    return results.data;
}

/**
 * Asynchronously reads and processes a file based on its type.
 *
 * @param {string} fileName - The name of the file to be read
 * @param {string} type - The type of the file to be processed
 * @returns {Promise<any>} A promise that resolves to the processed file data
 */
async function readAndProcessFile(fileName, type) {
    const filePath = path.resolve(__dirname, `../data/${fileName}`);
    const fileExtension = path.extname(fileName).toLowerCase();

    try {
        const fileTypeHandlers = {
            '.json': () => readJSONFile(filePath),
            '.csv': async () => {
                const data = await readCSVFile(filePath);
                if (type === 'AnimeEntry') {
                    return processAnimeData(data);
                } else if (type === 'UserInteraction') {
                    return processUserInteractionData(data);
                }
            },
        };

        const handler = fileTypeHandlers[fileExtension];
        if (!handler) {
            throw new Error(`Unsupported file type: ${fileExtension}`);
        }

        return await handler();
    } catch (err) {
        console.error(`Error reading file or parsing data: ${filePath}`, err);
        throw err;
    }
}

export { readCSVFile, readJSONFile, readAndProcessFile, checkFileExists };
