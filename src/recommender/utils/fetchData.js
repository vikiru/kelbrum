const RATE_LIMIT_STATUS = 429;
/**
 * Asynchronously fetches the data from the specified URL with the option to retry a certain number of times.
 *
 * @param {string} url - The URL to fetch data from
 * @param {number} retries - The number of retries in case of failure (default is 1)
 * @returns {Promise} A Promise that resolves with the fetched data, or rejects with an error
 */
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

/**
 * Asynchronously fetches data from the given URL, with error handling and retry mechanism.
 *
 * @param {string} url - The URL to fetch data from
 * @returns {Promise} A Promise that resolves with the fetched data, or an empty array if an error occurs
 */
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

/**
 * Creates a Promise that resolves after a specified delay.
 *
 * @returns {Promise} A Promise that resolves after the specified delay.
 */
function delay() {
    return new Promise((resolve) => {
        setTimeout(resolve, 1000);
    });
}

/**
 * Compares two arrays and performs a specific operation on the input array based on the fetched array.
 *
 * @param {Array} inputArray - The input array to compare
 * @param {Array} fetchedArray - The array to compare against the input array
 * @returns {Array} The original input array
 */
function compareArrays(inputArray, fetchedArray) {
    let array = inputArray;
    if (fetchedArray === undefined) return;
    if (inputArray.length === 0 && fetchedArray.length > 0) {
        inputArray = fetchedArray.map((a) => a.title || a.name).join(',');
    }
    return array;
}

/**
 * Compares the input premiered with the fetched season and year, and returns the finalized premiered value.
 *
 * @param {string} inputPremiered - The input premiered value to compare.
 * @param {string} fetchedSeason - The fetched season value.
 * @param {string} fetchedYear - The fetched year value.
 * @returns {string} The finalized premiered value.
 */
function comparePremiered(inputPremiered, fetchedSeason, fetchedYear) {
    let premiered = inputPremiered;
    if (inputPremiered === 'Unknown') {
        const season = fetchedSeason !== null ? fetchedSeason : '';
        const year = fetchedYear !== null ? fetchedYear : '';
        premiered = `${season} ${year}`;
    }
    return premiered;
}

/**
 * Compares input property to fetched property and returns the most suitable property based on certain conditions.
 *
 * @param {any} inputProperty - The input property to be compared
 * @param {any} fetchedProperty - The fetched property to be compared
 * @returns {any} The most suitable property based on comparison
 */
function compareInputToFetched(inputProperty, fetchedProperty) {
    const inputDefaults = ['Unknown', 0, 'No description available for this anime.', 'Not available'];
    const fetchedDefaults = ['Unknown', null];

    const isNumber = (value) => !isNaN(parseFloat(value)) && isFinite(value);
    const inputIsNumber = isNumber(inputProperty);
    const fetchedIsNumber = isNumber(fetchedProperty);

    const bothAreStrings = typeof inputProperty === 'string' && typeof fetchedProperty === 'string';
    if (bothAreStrings && inputProperty !== fetchedProperty) {
        return fetchedProperty;
    }

    if (inputIsNumber && fetchedIsNumber && inputProperty !== fetchedProperty) {
        return fetchedProperty;
    }

    if (inputDefaults.includes(inputProperty) && !fetchedDefaults.includes(fetchedProperty)) {
        return fetchedProperty;
    }

    return inputProperty;
}

/**
 * Cleans the given title by normalizing it and removing any special characters.
 *
 * @param {string} title - The title to be cleaned.
 * @returns {string} The cleaned title.
 */
function cleanTitle(title) {
    const normalizedTitle = title.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return normalizedTitle.replace(/[^a-zA-Z0-9\s]/g, '');
}

/**
 * Filters and returns the keys of the given entry that are not in the excludedKeys array and have a value of 'Unknown',
 * 0, or an empty array.
 *
 * @param {Object} entry - The entry object to identify missing properties from
 * @returns {Array} An array of keys representing the missing properties
 */
function identifyMissingProperties(entry) {
    const excludedKeys = ['relations', 'streaming', 'external'];
    return Object.keys(entry).filter(
        (key) =>
            !excludedKeys.includes(key) &&
            (entry[key] === 'Unknown' ||
                entry[key] === 0 ||
                (Array.isArray(entry[key]) && entry[key].length === 0) ||
                entry[key] === 'No description available for this anime.'),
    );
}

/**
 * Constructs a URL for searching anime based on the provided title.
 *
 * @param {string} title - The title of the anime to search for
 * @returns {string} The constructed URL for searching the anime
 */
function constructUrl(title) {
    const searchTitle = cleanTitle(title);
    const baseQuery = 'https://api.jikan.moe/v4/anime?q=';
    const url = baseQuery + encodeURIComponent(searchTitle);
    return url;
}

/**
 * Asynchronously constructs URLs based on the provided data.
 *
 * @param {Array} data - The input data to be processed
 * @returns {Promise<Array>} An array of URLs constructed based on the input data
 */
async function constructUrls(data) {
    const urls = [];
    for (const entry of data) {
        const title = entry.englishName !== 'Unknown' ? entry.englishName : entry.title;
        const url = await constructUrl(title);
        urls.push(url);
    }

    return urls;
}

/**
 * Function to find a matching anime in the fetched data based on the provided entry.
 *
 * @param {Object} entry - The anime entry to search for
 * @param {Object} fetchedData - The data containing anime information
 * @returns {Object} The matching anime object from the fetched data
 */
function findMatchingAnime(entry, fetchedData) {
    const searchTitle = cleanTitle(entry.title);
    const possibleTitles = [entry.englishName, entry.otherName, entry.title, searchTitle].filter(
        (t) => t !== 'Unknown',
    );
    const uniquePossibleTitles = Array.from(new Set(possibleTitles));
    return fetchedData.data.find((a) => {
        const titlesToCheck = [a.title, a.title_english, a.title_japanese];
        return (
            titlesToCheck.some((title) => uniquePossibleTitles.includes(title)) ||
            a.title_synonyms.some((synonym) => uniquePossibleTitles.includes(synonym)) ||
            a.titles.some((t) => uniquePossibleTitles.includes(t.title))
        );
    });
}

const propertyMapping = {
    malID: 'mal_id',
    pageURL: 'url',
    trailerURL: 'trailer',
    title: 'title',
    titles: 'titles',
    englishName: 'title_english',
    otherName: 'title_japanese',
    type: 'type',
    source: 'source',
    episodes: 'episodes',
    status: 'status',
    aired: 'aired',
    durationText: 'duration',
    rating: 'rating',
    score: 'score',
    scoredBy: 'scored_by',
    rank: 'rank',
    popularity: 'popularity',
    members: 'members',
    favourites: 'favorites',
    synopsis: 'synopsis',
    season: 'season',
    year: 'year',
    producers: 'producers',
    licensors: 'licensors',
    studios: 'studios',
    genres: 'genres',
    themes: 'themes',
    demographics: 'demographics',
};

function updateEntry(entry, animeResult) {
    const propertiesToUpdate = identifyMissingProperties(entry);
    for (const key of propertiesToUpdate) {
        const type = Array.isArray(entry[key]) ? 'array' : 'singleValue';
        if (type === 'singleValue') {
            entry[key] = compareInputToFetched(entry[key], animeResult[propertyMapping[key]]);
        } else if (type === 'array') {
            entry[key] = compareArrays(entry[key], animeResult[propertyMapping[key]]);
        }
    }
    const titles = Array.from(
        new Set([entry.title, entry.englishName, entry.otherName].filter((title) => title !== 'Unknown')),
    );
    entry.titles = animeResult.titles.length > 0 ? Array.from(new Set(animeResult.titles.map((t) => t.title))) : titles;
    entry.themes = animeResult.themes.map((theme) => theme.name);
    entry.demographics = animeResult.demographics.map((demo) => demo.name);
    entry.trailerURL = animeResult.trailer.url !== null ? animeResult.trailer.url : 'Unknown';
}

async function handleMissingData(data) {
    const missing = [];
    const issues = [];
    const total = data.length;
    const startTime = process.hrtime();

    console.log(`Starting to process ${total} entries.`);

    const urls = await constructUrls(data);
    const entriesToUpdate = data.filter((entry) => identifyMissingProperties(entry).length >= 2);
    const totalBatches = Math.ceil(entriesToUpdate.length / 2);

    console.log(`Processing ${entriesToUpdate.length} entries with missing data into ${totalBatches} batches.`);

    for (let i = 0; i < entriesToUpdate.length; i += 2) {
        const batchNumber = i / 2 + 1;
        const remainingBatches = totalBatches - i / 2;

        console.log(`Processing batch ${batchNumber} of ${totalBatches}. ${remainingBatches} batches remaining.`);

        const batch = entriesToUpdate.slice(i, i + 2);
        const batchUrls = batch.map((entry) => urls[data.indexOf(entry)]);

        console.log(`URLs for batch ${batchNumber}:`, batchUrls);

        try {
            const results = await Promise.all(batchUrls.map((url) => fetchData(url)));

            for (let j = 0; j < batch.length; j++) {
                const entry = batch[j];
                const result = results[j];

                if (result.data.length === 0) {
                    console.warn(`Entry for '${entry.title}' not found. Adding to missing list for exclusion.`);
                    missing.push(entry);
                } else {
                    const animeResult = findMatchingAnime(entry, result);
                    if (animeResult) {
                        updateEntry(entry, animeResult);
                        console.info(`Entry for '${entry.title}' updated successfully.`);
                        console.log(entry.title, entry.synopsis);
                    } else {
                        console.warn(
                            `Entry for '${entry.title}' could not be matched. Adding to issues list for exclusion.`,
                        );
                        issues.push(entry);
                    }
                }
            }
        } catch (error) {
            console.error(`Error processing batch ${batchNumber}:`, error);
        }

        await new Promise((resolve) => setTimeout(resolve, 500));
    }

    const elapsedTime = process.hrtime(startTime);
    const elapsedSeconds = elapsedTime[0] + elapsedTime[1] / 1e9;
    console.log(`Total time for processing all entries: ${elapsedSeconds.toFixed(2)} seconds`);

    const remainingEntries = data.filter((d) => !missing.includes(d) && !issues.includes(d));
    console.log(`Processed ${remainingEntries.length} entries successfully.`);

    return remainingEntries;
}

export {
    fetchWithRetry,
    fetchData,
    delay,
    compareArrays,
    comparePremiered,
    compareInputToFetched,
    cleanTitle,
    identifyMissingProperties,
    constructUrl,
    constructUrls,
    findMatchingAnime,
    updateEntry,
    handleMissingData,
};
