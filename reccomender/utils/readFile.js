const path = require('path');
const fs = require('fs');

const { parse } = require('csv-parse');
const { processUserInteractionData, processAnimeData } = require('./processData');

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
    try {
        const jsonData = await fs.promises.readFile(filePath, 'utf8');
        const parsedData = JSON.parse(jsonData);
        console.log(`Successfully read JSON file at path "${filePath}".`);
        return parsedData;
    } catch (error) {
        console.error(`Error reading JSON file at path "${filePath}":`, error);
        throw error;
    }
}

async function readCSVFile(filePath) {
    const data = [];
    await new Promise((resolve, reject) => {
        fs.createReadStream(filePath)
            .pipe(parse({ delimiter: ',', from_line:  2 }))
            .on('data', (row) => {
                data.push(row);
            })
            .on('end', () => {
                console.log(`Successfully read CSV file at path "${filePath}".`);
                resolve();
            })
            .on('error', reject);
    });
    return data;
}


async function readFile(fileName, type) {
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
            }
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


module.exports = {
    readCSVFile,
    readJSONFile,
    readFile,
    checkFileExists,
};
