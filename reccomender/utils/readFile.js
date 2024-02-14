const path = require('path');
const fs = require('fs');

const { parse } = require('csv-parse');
const { processUserInteractionData, processAnimeData } = require('./processData');

async function readJSONFile(filePath) {
    try {
        const jsonData = await fs.promises.readFile(filePath, 'utf8');
        return JSON.parse(jsonData);
    } catch (error) {
        console.error(`Error reading JSON file at path "${filePath}":`, error);
    }
}

async function readCSVFile(filePath) {
    const data = [];
    await new Promise((resolve, reject) => {
        fs.createReadStream(filePath)
            .pipe(parse({ delimiter: ',', from_line: 2 }))
            .on('data', (row) => {
                data.push(row);
                console.log(data.length);
            })
            .on('end', resolve)
            .on('error', reject);
    });
    return data;
}

async function readFile(fileName, fileType, type) {
    const filePath = path.resolve(__dirname, `../data/${fileName}`);
    try {
        if (fileType === 'json') {
            return readJSONFile(filePath);
        } else if (fileType === 'csv') {
            const data = await readCSVFile(filePath);
            if (type === 'AnimeEntry') {
                return processAnimeData(data);
            } else if (type === 'UserInteraction') {
                return processUserInteractionData(data);
            }
        } else {
            throw new Error(`Unsupported file type: ${fileType}`);
        }
    } catch (err) {
        console.error('Error reading file or parsing data:', err);
        throw err;
    }
}

module.exports = {
    readCSVFile,
    readJSONFile,
    readFile,
};
