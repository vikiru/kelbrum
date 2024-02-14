const { cleanDuration, cleanRating } = require('./clean');

const RATE_LIMIT_STATUS = 429;
async function fetchWithRetry(url, retries = 1) {
    try {
        const response = await fetch(url);
        if (response.status === RATE_LIMIT_STATUS && retries > 0) {
            console.log('Rate limit reached. Attempting to retry request after delay.');
            await delay();
            return await fetchWithRetry(url, retries - 1);
        }
        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

async function fetchData(url) {
    try {
        return await fetchWithRetry(url);
    } catch (error) {
        console.error('Error fetching data:', error);
        return {
            data: [],
        };
    }
}

function delay() {
    return new Promise((resolve) => {
        setTimeout(resolve, 1000);
    });
}

function compareArrays(inputArray, fetchedArray) {
    let array = inputArray;
    if (inputArray.length === 0 && fetchedArray.length > 0) {
        inputArray = fetchedArray.map((a) => a.name).join(',');
    }
    return array;
}

function comparePremiered(inputPremiered, fetchedSeason, fetchedYear) {
    let premiered = inputPremiered;
    if (inputPremiered === 'Unknown') {
        const season = fetchedSeason !== null ? fetchedSeason : '';
        const year = fetchedYear !== null ? fetchedYear : '';
        premiered = `${season} ${year}`;
    }
    return premiered;
}

function compareInputToFetched(inputProperty, fetchedProperty) {
    let property = inputProperty;
    const inputDefaults = ['Unknown', 0, 'No description available for this anime.', 'Not available'];
    const fetchedDefaults = ['Unknown', null];
    if (inputDefaults.includes(inputProperty) && !fetchedDefaults.includes(fetchedProperty)) {
        property = fetchedProperty;
    }
    if (property === undefined || property === null){
        property = inputProperty;
    }
    return property;
}

async function handleMissingData(data) {
    const indexes = data.filter((d) => d.status !== 'Finished Airing').map((d) => data.indexOf(d));
    const total = indexes.length;
    const baseQuery = 'https://api.jikan.moe/v4/anime?q=';
    for (const index of indexes) {
        const entry = data[index];
        const title = entry.title;
        const url = baseQuery + `${title}`;
        console.log(`Fetching data for missing data entry ${indexes.indexOf(index) + 1} / ${total}`);
        const result = await fetchData(url);
        const resultData = result.data.length > 0 ? result.data.find((d) => d.title === entry.title) : undefined;
        if (resultData) {
            entry.title = compareInputToFetched(entry.title, resultData.title);
            entry.englishName = compareInputToFetched(entry.englishName, resultData.title_english);
            entry.otherName = compareInputToFetched(entry.otherName, resultData.title_japanese);
            entry.type = compareInputToFetched(entry.type, resultData.type);
            entry.source = compareInputToFetched(entry.source, resultData.source);
            entry.episodes = compareInputToFetched(entry.episodes, resultData.episodes);
            entry.status = compareInputToFetched(entry.status, resultData.status);
            entry.aired = compareInputToFetched(entry.aired, resultData.aired.string);
            entry.duration = cleanDuration(compareInputToFetched(entry.duration, resultData.duration));
            entry.rating = cleanRating(compareInputToFetched(entry.rating, resultData.rating));
            entry.score = compareInputToFetched(entry.score, resultData.score);
            entry.scoredBy = compareInputToFetched(entry.score, resultData.scored_by);
            entry.rank = compareInputToFetched(entry.rank, resultData.rank);
            entry.popularity = compareInputToFetched(entry.popularity, resultData.popularity);
            entry.members = compareInputToFetched(entry.members, resultData.members);
            entry.favourites = compareInputToFetched(entry.favourites, resultData.favorites);
            entry.synopsis = compareInputToFetched(entry.synopsis, resultData.synopsis);
            entry.season = compareInputToFetched(entry.season, resultData.season);
            entry.year = compareInputToFetched(entry.year, resultData.year);
            entry.premiered = comparePremiered(entry.premiered, resultData.season, resultData.year);
            entry.producers = compareArrays(entry.producers, resultData.producers);
            entry.licensors = compareArrays(entry.licensors, resultData.licensors);
            entry.studios = compareArrays(entry.studios, resultData.studios);
            entry.genres = compareArrays(entry.genres, resultData.genres);
            entry.pageURL = resultData.url;
            await delay();
        }
    }
}

module.exports = {
    fetchData,
    delay,
    compareArrays,
    compareInputToFetched,
    comparePremiered,
    handleMissingData,
};
