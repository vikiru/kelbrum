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
    } else {
        const regex = /([a-zA-z]+)\s+(\d+),?\s+(\d+)/im;
        const matches = text.match(regex);
        if (matches) {
            const matchLength = matches.length;
            if (matchLength >= 2) {
                const month = matches[1];
                const seasonMatch = seasons.find((season) => season.months.includes(month));
                let season = 'Unknown';
                if (seasonMatch) {
                    season = seasonMatch.name;
                }
                const year = parseInt(matches[3], 10) || 'Unknown';
                return {
                    season,
                    year,
                };
            }
        } else {
            const standAloneYear = /^(\d+)$/im;
            const matches = text.match(standAloneYear);
            if (matches) {
                return {
                    season: 'Unknown',
                    year: parseInt(matches[0], 10),
                };
            }
        }
    }
}

function findSeasonalYearByPremiered(text) {
    if (text.toLowerCase() === 'unknown') {
        return {
            season: 'Unknown',
            year: 'Unknown',
        };
    } else {
        const splitText = text.split(' ');
        const [season, year] = splitText;
        return {
            season,
            year: parseInt(year, 10),
        };
    }
}

function findSeasonalYear(premiered, aired) {
    let season = 'Unknown';
    let year = 'Unknown';
    let result = {};
    if (premiered !== 'Unknown') {
        result = findSeasonalYearByPremiered(premiered);
    } else if (premiered === 'Unknown' && aired !== 'Unknown') {
        result = findSeasonalYearByAired(aired);
    }
    return result || { season, year };
}

function cleanRating(text) {
    if (text === 'UNKNOWN') {
        return text.replace(text, 'Unknown');
    } else {
        return text.split(' ')[0];
    }
}

function cleanDuration(text) {
    if (text === 'Unknown') {
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
        if (unit === 'hr') {
            hours += value;
        } else if (unit === 'min') {
            minutes += value;
        } else if (unit === 'sec') {
            seconds += value;
        }
    }
    const totalMinutes = hours * 60 + minutes + Math.round(seconds / 60);
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

function cleanPremiered(premiered, season, year){
    if (premiered === 'Unknown' && season !== 'Unknown' && year !== 'Unknown'){
        console.log('HMM', season, year);
        return `${season} ${year}`;
    }
    else {
        return premiered;
    }
}

module.exports = {
    findSeasonalYearByAired,
    seasons,
    findSeasonalYearByPremiered,
    findSeasonalYear,
    cleanRating,
    cleanDuration,
    cleanArray,
    cleanPremiered
};
