const fs = require('fs');
const path = require('path');

const { parse } = require("csv-parse");

const { AnimeEntry } = require('../models/AnimeEntry');
const { UserInteraction } = require('../models/UserInteraction');

function findMax(data, property) {
    const propArr = data.map((d) => Number(d[property])).filter((arrItem) => !isNaN(arrItem));
    return Math.max(...propArr);
}

function findMin(data, property) {
    const propArr = data.map((d) => Number(d[property])).filter((arrItem) => !isNaN(arrItem));
    return Math.min(...propArr);
}

const seasons = [
    { name: "fall", months: ["Oct", "Nov", "Dec"] },
    { name: "spring", months: ["Apr", "May", "Jun"] },
    { name: "summer", months: ["Jul", "Aug", "Sep"] },
    { name: "winter", months: ["Jan", "Feb", "Mar"] }
  ];

function cleanAired(text){
    if (text === 'Not available'){
        return {
            season: 'Unknown',
            year: 'Unknown',
        }
    }
    else {
        const regex = /([a-zA-z]+)\s+(\d+),?\s+(\d+)/im;
        const matches = text.match(regex);
        if (matches){
            const matchLength = matches.length;
            if (matchLength >= 2){
                const month = matches[1];
                const seasonMatch = seasons.find(season => season.months.includes(month));
                let season = 'Unknown';
                if (seasonMatch){
                    season = seasonMatch.name;
                }
                const year = parseInt(matches[3], 10) || 'Unknown';
                return {
                    season, year
                }
            }
        }
        else {
            const standAloneYear = /^(\d+)$/im;
            const matches = text.match(standAloneYear);
            if (matches){
                return {
                    season: 'Unknown',
                    year: parseInt(matches[0], 10),
                }
            }
        }
    }
}

function cleanPremiered(text){
    if (text.toLowerCase() === 'unknown'){
        return {
            season: 'Unknown',
            year: 'Unknown'
        };
    }
    else {
        const splitText = text.split(" ");
        const [season , year] = splitText;
        return {
            season, year: parseInt(year, 10)
        }
    }
}

function findSeasonalYear(premiered, aired){
    let season = 'Unknown';
    let year = 'Unknown';
    let result = {};
    if (premiered !== 'Unknown'){
         result = cleanPremiered(premiered);
    }
    else if (premiered === 'Unknown' && aired !== 'Unknown'){
         result = cleanAired(aired);
    }
    return result || {season, year};
}

function cleanRating(text){
    if (text === 'UNKNOWN'){
        return text.replace(text, 'Unknown');
    }
    else {
        return text.split(" ")[0];
    }
}

function cleanDuration(text) {
    if (text.toLowerCase() === 'unknown') {
        return text;
    }

    const regex = /(\d+)\s*(hr|min|sec)(?:\s*per ep)?/gi;
    let match;
    let hours =   0;
    let minutes =   0;
    let seconds =  0;

    while ((match = regex.exec(text)) !== null) {
        const value = parseInt(match[1],   10);
        const unit = match[2];
        if (unit === 'hr') {
            hours += value;
        } else if (unit === 'min') {
            minutes += value;
        } else if (unit === 'sec') {
            seconds += value;
        }
    }

    const totalMinutes = hours *   60 + minutes + Math.round(seconds /  60);
    return totalMinutes;
}


function cleanArray(array){
    const cleanedArray = array.split(',').map((arr) => arr.replace("UNKNOWN", '').trim()).filter((a) => a !== '');
    cleanedArray.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    return cleanedArray;
}

async function processAnimeData(data){
    const animeEntries = data.map((row) => {
        let [animeID, name, englishName, otherName, score, genres, synopsis, type, episodes, aired, premiered, status, producers, licensors, studios, source, duration, rating, rank, popularity, favourites, scoredBy, members, imageURL] = row;
        englishName = englishName.replace('UNKNOWN', 'Unknown');
        otherName = otherName.replace("Unknown", 'Unknown');
        score = parseFloat(score) || 0;
        genres = cleanArray(genres);
        type = type.replace("UNKNOWN", 'Unknown');
        episodes = parseInt(episodes, 10) || 0;
        premiered = premiered.replace("UNKNOWN", "Unknown");
        const {season , year} = findSeasonalYear(premiered, aired);
        producers = cleanArray(producers);
        licensors = cleanArray(licensors);
        studios = cleanArray(studios);
        source = source.replace("UNKNOWN", 'Unknown');
        duration = cleanDuration(duration);
        rating = cleanRating(rating);
        rank = parseInt(rank, 10) || 0;
        popularity = parseInt(popularity, 10) || 0;
        favourites = parseInt(favourites, 10) || 0;
        scoredBy = parseInt(scoredBy, 10) || 0;
        members = parseInt(members, 10) || 0;
        const pageURL = `https://myanimelist.net/anime/${animeID}/${name.replace(' ', '_')}`;

        return new AnimeEntry(
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
            season,
            year,
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
    })
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
        .pipe(parse({ delimiter: ",", from_line: 2 }))
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

async function writeFile(fileName, data) {
    const filePath = path.resolve(__dirname, `../data/${fileName}`);
    try {
        const dataString = JSON.stringify(data, null, 2);
        await fs.promises.writeFile(filePath, dataString, 'utf8');
        console.log(`Data successfully written to ${filePath}`);
    } catch (err) {
        console.error('Error writing file:', err);
        throw err;
    }
}



function sortData(data){
    const firstElement = data[0];
    const type = typeof firstElement;
    if (type === 'string'){
        data.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    }
    else if (type === 'number'){
        data.sort((a,b) => a - b);
    }
    return data;
}

function returnUniqueArray(data, property, filter = []) {
    const allPropertyValues = data.flatMap((d) => d[property]).filter((value) => !filter.includes(value));
    const uniquePropertyValues = Array.from(new Set(allPropertyValues)).filter((a) => a !== '');
    return uniquePropertyValues;
}

function filterAnimeData(data) {
    const excludedTypes = ['ONA', 'OVA', 'Special', 'Music', 'Unknown'];
    const filteredData = data.filter((d) => !d.genres.includes('Hentai') && !excludedTypes.includes(d.type));
    return filteredData;
}
async function constructDataFiles() {
    const animeData = await readFile('../data/anime-dataset-2023.csv', 'csv', 'AnimeEntry');
    //const animeData = await readFile('entries.json', 'json', 'AnimeEntry');
    const filteredData = filterAnimeData(animeData);
    await writeFile('entries.json', filteredData);
    const allowedKeys = ['aired', 'genres', 'type', 'episodes', 'season', 'year', 'status', 'producers', 'licensors', 'studios', 'source', 'duration', 'rating'];
    const specialKeys = ['duration', 'rating', 'season', 'year', 'source', 'premiered'];

    for (const key of allowedKeys){
        const fileName = `${key}.json`;
        const data = specialKeys.includes(key) ? returnUniqueArray(filteredData, key, ['Unknown']) : returnUniqueArray(filteredData, key);
        await writeFile(fileName, sortData(data));
    }
    return filteredData;
}



module.exports = {
    readFile,
    writeFile,
    findMax,
    findMin,
    constructDataFiles,
};
