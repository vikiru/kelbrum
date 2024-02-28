import { Buffer } from 'buffer';
import fs from 'fs';
import Papa from 'papaparse';
import path from 'path';
import { fileURLToPath } from 'url';

import { processAnimeData, processUserInteractionData } from './processData.js';

let dirname;
let __filename, __dirname;

if (typeof window === 'undefined') {
    dirname = path.dirname;
    __filename = fileURLToPath(import.meta.url);
    __dirname = dirname(__filename);
}

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

async function readJSONFile(filePathOrFile) {
    const fileData = await readFile(filePathOrFile);
    return JSON.parse(fileData);
}

async function readCSVFile(filePathOrFile) {
    const fileData = await readFile(filePathOrFile);
    const results = Papa.parse(fileData, {
        header: true,
        skipEmptyLines: true,
    });
    return results.data;
}

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
