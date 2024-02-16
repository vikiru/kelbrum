const { returnUniqueArray } = require("./utils");

function jaccardSimilarity(setA, setB) {
    const intersection = new Set([...setA].filter((x) => setB.has(x)));
    const union = new Set([...setA, ...setB]);
    return intersection.size / union.size;
}

function normalizeGenres(anime, uniqueGenres) {
    const inputGenres = anime.genres;
    return uniqueGenres.map((genre) => (inputGenres.includes(genre) ? 1 : 0));
}

function normalizeSeason(data) {
    const seasons = ['spring', 'summer', 'fall', 'winter'];
    return data.map(entry => {
        return seasons.map(season => (entry.season === season ?  1 :  0));
    });
}

function normalizeOrder(data, property) {
    const orders = data.map((d) => d[property]);
    const orderMapping = {};
    let currentOrder = 1;
    const defaultValue = Math.max(...orders) + 1;
    orders.forEach((order) => {
        if (!orderMapping[order] && order >= 1) {
            orderMapping[order] = currentOrder++;
        } else if (order === 0) {
            orderMapping[order] = defaultValue;
        }
    });
    return data.map((d) => orderMapping[d[property]]);
}

function normalizeLicensor(data) {
    const uniqueLicensors = returnUniqueArray(data, 'licensor');
    const normalizedLicensors = data.map((entry) => {
        return uniqueLicensors.map((licensor) => (entry.licensor === licensor ?  1 :  0));
    });
    return normalizedLicensors;
}

function normalizeProducer(data) {
    const uniqueProducers = returnUniqueArray(data, 'producer');
    const normalizedProducers = data.map((entry) => {
        return uniqueProducers.map((producer) => (entry.producer === producer ?  1 :  0));
    });
    return normalizedProducers;
}

function normalizeRating(data) {
    const uniqueRatings = returnUniqueArray(data, 'rating');
    const normalizedRatings = data.map((entry) => {
        return uniqueRatings.map((rating) => (entry.rating === rating ?   1 :   0));
    });
    return normalizedRatings;
}

function normalizeSource(data) {
    const uniqueSources = returnUniqueArray(data, 'source');
    const normalizedSources = data.map((entry) => {
        return uniqueSources.map((source) => (entry.source === source ?   1 :   0));
    });
    return normalizedSources;
}

function normalizeType(data) {
    const uniqueTypes = returnUniqueArray(data, 'type');
    const normalizedTypes = data.map((entry) => {
        return uniqueTypes.map((type) => (entry.type === type ?   1 :   0));
    });
    return normalizedTypes;
}

function normalizeStatus(data) {
    const uniqueStatus = returnUniqueArray(data, 'status');
    const normalizedStatus = data.map((entry) => {
        return uniqueStatus.map((status) => (entry.status === status ?   1 :   0));
    });
    return normalizedStatus;
}

function normalizeStudio(data) {
    const uniqueStudios = returnUniqueArray(data, 'studio');
    const normalizedStudios = data.map((entry) => {
        return uniqueStudios.map((studio) => (entry.studio === studio ?  1 :  0));
    });
    return normalizedStudios;
}

function normalizeEpisodes(data) {
    const episodes = data.map((d) => d.episodes);
    const minEpisodes = Math.min(...episodes);
    const maxEpisodes = Math.max(...episodes);
    return episodes.map((ep) => (ep - minEpisodes) / (maxEpisodes - minEpisodes));
}

function normalizeDurationMinutes(data) {
    const durations = data.map((d) => d.durationMinutes);
    const minDuration = Math.min(...durations);
    const maxDuration = Math.max(...durations);
    return durations.map((duration) => (duration - minDuration) / (maxDuration - minDuration));
}

function normalizeYear(data) {
    const years = data.map((d) => (d.year === 'unknown' ? -1 : d.year));
    const minYear = Math.min(...years.filter(year => year !== -1));
    const maxYear = Math.max(...years.filter(year => year !== -1));
    return years.map((year) => (year === -1 ?   0 : (year - minYear) / (maxYear - minYear)));
}

module.exports = {
    normalizeGenres,
    normalizeOrder,
    normalizeStatus,
    normalizeEpisodes,
    jaccardSimilarity
}

// pearson correlation, matrix multiplication/factorization
// consider combining rank and popularity into one, revisit all normalization and all properties.