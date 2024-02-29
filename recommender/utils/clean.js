const seasons = [
    { name: 'fall', months: ['Oct', 'Nov', 'Dec'] },
    { name: 'spring', months: ['Apr', 'May', 'Jun'] },
    { name: 'summer', months: ['Jul', 'Aug', 'Sep'] },
    { name: 'winter', months: ['Jan', 'Feb', 'Mar'] },
];

/**
 * Finds the seasonal year by the aired text.
 *
 * @param {string} text - The text to search for seasonal year.
 * @returns {Object} An object containing the seasonal name and year.
 */
function findSeasonalYearByAired(text) {
    if (text === 'Not available') {
        return {
            season: 'Unknown',
            year: 'Unknown',
        };
    }

    const regex = /(?:([a-zA-Z]+)\s*(\d{4})|(\d{4})\s*to\s*(\d{4})?|(\d{4})|([a-zA-Z]{3})\s*(\d{1,2}),\s*(\d{4}))/i;
    const matches = text.match(regex);
    if (!matches) {
        return {
            season: 'Unknown',
            year: 'Unknown',
        };
    }

    const season = matches[1] || null;
    const year = matches[2] || matches[3] || matches[4] || matches[5] || matches[8];

    const seasonMatch = season ? seasons.find((seasonObj) => seasonObj.months.includes(season)) : null;
    const seasonName = seasonMatch
        ? seasonMatch.name
        : matches[6]
          ? seasons.find((seasonObj) => seasonObj.months.includes(matches[6])).name
          : 'Unknown';

    const yearValue = year ? parseInt(year, 10) : 'Unknown';

    return {
        season: seasonName,
        year: yearValue,
    };
}

/**
 * Function to find seasonal year based on the premiered text.
 *
 * @param {string} text - The premiered text
 * @returns {Object} Object containing the season and year
 */
function findSeasonalYearByPremiered(text) {
    if (text.toLowerCase() === 'unknown') {
        return {
            season: 'Unknown',
            year: 'Unknown',
        };
    } else {
        const splitText = text.includes(' ') ? text.split(' ') : [text];
        const [season, year] = splitText;
        return {
            season: season || 'Unknown',
            year: parseInt(year, 10) || 'Unknown',
        };
    }
}

/**
 * Finds the seasonal year based on the premiered and aired dates.
 *
 * @param {string} premiered - The premiered date of the show
 * @param {string} aired - The aired date of the show
 * @returns {object} Object with the season and year of the show
 */
function findSeasonalYear(premiered, aired) {
    if (premiered !== 'Unknown') {
        return findSeasonalYearByPremiered(premiered);
    }
    if (aired !== 'Unknown') {
        return findSeasonalYearByAired(aired);
    }
    return { season: 'Unknown', year: 'Unknown' };
}

/**
 * Cleans the rating text by replacing 'UNKNOWN' with 'Unknown' and returning the first word of any other text.
 *
 * @param {string} text - The input text to be cleaned
 * @returns {string} The cleaned rating text
 */
function cleanRating(text) {
    if (text === 'UNKNOWN') {
        return text.replace(text, 'Unknown');
    } else {
        return text.split(' ')[0];
    }
}

/**
 * Cleans the input text by extracting duration information and converting it to total minutes.
 *
 * @param {string} text - The input text to be cleaned and processed for duration information.
 * @returns {number} The total duration in minutes extracted from the input text.
 */
function cleanDuration(text) {
    if (text === 'Unknown' || typeof text !== 'string') {
        return text;
    }

    const regex = /(\d+)\s*(hr|min|sec)(?:\s*per ep)?/gi;
    let match;
    let hours = 0;
    let minutes = 0;
    let seconds = 0;

    while ((match = regex.exec(text)) !== null) {
        const value = parseInt(match[1], 10);
        const unit = match[2];
        if (!isNaN(value)) {
            if (unit === 'hr') {
                hours += value;
            } else if (unit === 'min') {
                minutes += value;
            } else if (unit === 'sec') {
                seconds += value;
            }
        }
    }
    const totalMinutes = hours * 60 + minutes + Math.round(seconds / 60);
    return totalMinutes;
}

/**
 * Cleans the input array by splitting it, removing 'UNKNOWN' strings, trimming white spaces, and filtering empty
 * strings.
 *
 * @param {string} array - The input array to be cleaned
 * @returns {array} The cleaned array
 */
function cleanArray(array) {
    const cleanedArray = array
        .split(',')
        .map((arr) => arr.replace('UNKNOWN', '').trim())
        .filter((a) => a !== '');
    cleanedArray.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    return cleanedArray;
}

/**
 * Cleans the premiered value based on the season and year, or returns the original premiered value if season or year is
 * 'Unknown' or undefined.
 *
 * @param {string} premiered - The original premiered value
 * @param {string} season - The season value
 * @param {string} year - The year value
 * @returns {string} The cleaned premiered value or the original premiered value
 */
function cleanPremiered(premiered, season, year) {
    if (season !== undefined && season !== 'Unknown' && year !== undefined && year !== 'Unknown') {
        return `${season} ${year}`;
    }
    return premiered;
}

export {
    seasons,
    findSeasonalYearByAired,
    findSeasonalYearByPremiered,
    findSeasonalYear,
    cleanRating,
    cleanDuration,
    cleanArray,
    cleanPremiered,
};
