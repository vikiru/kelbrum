const seasons = [
    { name: 'fall', months: ['Oct', 'Nov', 'Dec'] },
    { name: 'spring', months: ['Apr', 'May', 'Jun'] },
    { name: 'summer', months: ['Jul', 'Aug', 'Sep'] },
    { name: 'winter', months: ['Jan', 'Feb', 'Mar'] },
];

function findSeasonalYearByAired(text) {
    if (text === 'Not available') {
        return {
            season: 'Unknown',
            year: 'Unknown',
        };
    }

    // Updated regex to include optional day and month format
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

function findSeasonalYear(premiered, aired) {
    if (premiered !== 'Unknown') {
        return findSeasonalYearByPremiered(premiered);
    }
    if (aired !== 'Unknown') {
        return findSeasonalYearByAired(aired);
    }
    return { season: 'Unknown', year: 'Unknown' };
}

function cleanRating(text) {
    if (text === 'UNKNOWN') {
        return text.replace(text, 'Unknown');
    } else {
        return text.split(' ')[0];
    }
}

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
    const totalMinutes = hours * 60 + minutes + Math.round(seconds / 60); // Keep precision down to the second
    return totalMinutes;
}

function cleanArray(array) {
    const cleanedArray = array
        .split(',')
        .map((arr) => arr.replace('UNKNOWN', '').trim())
        .filter((a) => a !== '');
    cleanedArray.sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    return cleanedArray;
}

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
