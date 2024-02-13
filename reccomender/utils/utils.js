const fs = require('fs');
const fastcsv = require('fast-csv');
const { AnimeEntry } = require('./AnimeEntry');
const { UserInteraction } = require('./UserInteraction');

function findMax(data, property) {
    const propArr = data.map((d) => Number(d[property])).filter((arrItem) => !isNaN(arrItem));
    return Math.max(...propArr);
}

function findMin(data, property) {
    const propArr = data.map((d) => Number(d[property])).filter((arrItem) => !isNaN(arrItem));
    return Math.min(...propArr);
}

async function processAnimeData(data) {
    const animeEntries = [];

    for (const row of data) {
        const animeID = row[0];
        const name = row[1];
        const englishName = row[2].replace('UNKNOWN', 'Unknown');
        const otherName = row[3].replace('UNKNOWN', 'Unknown');
        const score = row[4].replace('UNKNOWN', 'Unknown');
        const genres = row[5]
            .split(',')
            .map((genre) => genre.replace('UNKNOWN', '').trim())
            .filter((a) => a !== '');
        const synopsis = row[6];
        const type = row[7].replace('UNKNOWN', 'Unknown');
        const episodes = parseInt(row[8], 10) || 0;
        const aired = row[9];
        const premiered = row[10].replace('UNKNOWN', 'Unknown');
        const status = row[11];
        const producers = row[12]
            .split(',')
            .map((producer) => producer.replace('UNKNOWN', '').trim())
            .filter((a) => a !== '');
        const licensors = row[13]
            .split(',')
            .map((licensor) => licensor.replace('UNKNOWN', '').trim())
            .filter((a) => a !== '');
        const studios = row[14]
            .split(',')
            .map((studio) => studio.replace('UNKNOWN', '').trim())
            .filter((a) => a !== '');
        const source = row[15].replace('UNKNOWN', 'Unknown');
        const duration = row[16];
        const rating = row[17].replace('UNKNOWN', 'Unknown');
        const rank = parseInt(row[18], 10) || 0;
        const popularity = parseInt(row[19], 10);
        const favourites = parseInt(row[20], 10) || 0;
        const scoredBy = parseInt(row[21], 10) || 0;
        const members = parseInt(row[22], 10) || 0;
        const imageURL = row[23];
        const pageURL = `https://myanimelist.net/anime/${animeID}/${name.replace(' ', '_')}`;

        const animeEntry = new AnimeEntry(
            animeID,
            name,
            englishName,
            otherName,
            score,
            genres,
            synopsis,
            type,
            episodes,
            aired,
            premiered,
            status,
            producers,
            licensors,
            studios,
            source,
            duration,
            rating,
            rank,
            popularity,
            favourites,
            scoredBy,
            members,
            imageURL,
            pageURL,
        );
        animeEntries.push(animeEntry);
    }
    return animeEntries;
}

async function processUserInteractionData(data) {
    const users = [];
    const uniqueUserIDs = Array.from(new Set(data.map((d) => d[0])));
    for (const id of uniqueUserIDs) {
        const relevantRows = data.filter((row) => row[0] === id);
        const ratings = relevantRows.map((row) => ({
            animeID: row[2],
            animeTitle: row[3],
            rating: row[4],
        }));
        const user = new UserInteraction(id, ratings);
        users.push(user);
    }
    return users;
}

async function readJSONFile(filePath) {
    try {
        const jsonData = await fs.promises.readFile(filePath, 'utf8');
        return JSON.parse(jsonData);
    } catch (error) {
        console.error(error);
    }
}

async function readCSVFile(filePath) {
    const data = [];
    await new Promise((resolve, reject) => {
        fs.createReadStream(filePath)
            .pipe(fastcsv.parse())
            .on('data', (row) => {
                data.push(row);
                console.log(data.length);
            })
            .on('end', resolve)
            .on('error', reject);
    });
    return data;
}

async function readFile(filePath, fileType, type) {
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
async function writeFile(filePath, data) {
    try {
        const dataString = JSON.stringify(data, null, 2);
        await fs.promises.writeFile(filePath, dataString, 'utf8');
        console.log(`Data successfully written to ${filePath}`);
    } catch (err) {
        console.error('Error writing file:', err);
        throw err;
    }
}

module.exports = {
    readFile: readFile,
    writeFile: writeFile,
    findMax: findMax,
    findMin: findMin,
};
