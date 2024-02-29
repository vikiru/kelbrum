import { Buffer } from 'buffer';
import fs from 'fs';
import Papa from 'papaparse';
import { dirname } from 'path';
import path from 'path';
import { fileURLToPath } from 'url';

import { processAnimeData, processUserInteractionData } from '../utils/processData.js';

const __filename = fileURLToPath(import.meta.url);

const __dirname = dirname(__filename);

/**
 * Check if the specified file exists.
 *
 * @param {string} fileName - The name of the file to check
 * @returns {boolean} True if the file exists, false if it does not
 */
async function checkFileExists(fileName) {
    const filePath = path.resolve(__dirname, `../data/${fileName}`);
    try {
        await fs.promises.access(filePath, fs.constants.F_OK);
        return true;
    } catch (error) {
        if (error.code === 'ENOENT') {
            return false;
        } else {
            throw error;
        }
    }
}

async function readJSONFile(filePath) {
    const fileData = await fs.promises.readFile(filePath, 'utf8');
    return JSON.parse(fileData);
}

/**
 * Asynchronously reads a CSV file and parses the data.
 *
 * @param {string | File} filePath - The path to the CSV file or a File object.
 * @returns {object[]} The parsed data from the CSV file.
 */
async function readCSVFile(filePath) {
    const results = Papa.parse(filePath, {
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
