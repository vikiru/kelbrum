const { returnUniqueArray } = require("./utils");
const tf = require('@tensorflow/tfjs');

function jaccardSimilarity(setA, setB) {
    const intersection = new Set([...setA].filter((x) => setB.has(x)));
    const union = new Set([...setA, ...setB]);
    return intersection.size / union.size;
}

function normalizeGenres(anime) {
    const uniqueGenres = returnUniqueArray(anime, 'genres');
    const inputGenres = anime.genres;
    return uniqueGenres.map((genre) => (inputGenres.includes(genre) ?  1 :  0));
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
    const uniqueEpisodes = returnUniqueArray(data, 'episodes');
    const episodes = data.map((d) => d.episodes);
    const minEpisodes = Math.min(...uniqueEpisodes);
    const maxEpisodes = Math.max(...uniqueEpisodes);
    return episodes.map((ep) => (ep - minEpisodes) / (maxEpisodes - minEpisodes));
}

function normalizeDurationMinutes(data) {
    const uniqueDurations = returnUniqueArray(data, 'durationMinutes');
    const durations = data.map((d) => d.durationMinutes);
    const minDuration = Math.min(...uniqueDurations);
    const maxDuration = Math.max(...uniqueDurations);
    return durations.map((duration) => (duration - minDuration) / (maxDuration - minDuration));
}

function normalizeYear(data) {
    const uniqueYears = returnUniqueArray(data, 'year', ['unknown']);
    const years = data.map((d) => (d.year === 'unknown' ? -1 : d.year));
    const minYear = Math.min(...uniqueYears);
    const maxYear = Math.max(...uniqueYears);
    return years.map((year) => (year === -1 ?   0 : (year - minYear) / (maxYear - minYear)));
}

function normalizeScore(data) {
    const uniqueScores = returnUniqueArray(data, 'score');
    const scores = data.map((d) => d.score);
    const minScore = Math.min(...uniqueScores);
    const maxScore = Math.max(...uniqueScores);
    return scores.map((score) => (score - minScore) / (maxScore - minScore));
}

function normalizeRank(data) {
    const uniqueRanks = returnUniqueArray(data, 'rank');
    const ranks = data.map((d) => d.rank);
    const minRank = Math.min(...uniqueRanks);
    const maxRank = Math.max(...uniqueRanks);
    return ranks.map((rank) => (rank - minRank) / (maxRank - minRank));
}

function normalizePopularity(data) {
    const uniquePopularities = returnUniqueArray(data, 'popularity');
    const popularities = data.map((d) => d.popularity);
    const minPopularity = Math.min(...uniquePopularities);
    const maxPopularity = Math.max(...uniquePopularities);
    return popularities.map((popularity) => (popularity - minPopularity) / (maxPopularity - minPopularity));
}

function normalizeScoredBy(data) {
    const uniqueScoredBy = returnUniqueArray(data, 'scoredBy');
    const scoredBy = data.map((d) => d.scoredBy);
    const minScoredBy = Math.min(...uniqueScoredBy);
    const maxScoredBy = Math.max(...uniqueScoredBy);
    return scoredBy.map((scored) => (scored - minScoredBy) / (maxScoredBy - minScoredBy));
}

function normalizeMembers(data) {
    const uniqueMembers = returnUniqueArray(data, 'members');
    const members = data.map((d) => d.members);
    const minMembers = Math.min(...uniqueMembers);
    const maxMembers = Math.max(...uniqueMembers);
    return members.map((member) => (member - minMembers) / (maxMembers - minMembers));
}

function createFeatureTensor(data) {
    const normalizedGenres = normalizeGenres(data);
    const normalizedSeasons = normalizeSeason(data);
    const normalizedLicensors = normalizeLicensor(data);
    const normalizedProducers = normalizeProducer(data);
    const normalizedRatings = normalizeRating(data);
    const normalizedSources = normalizeSource(data);
    const normalizedTypes = normalizeType(data);
    const normalizedStatuses = normalizeStatus(data);
    const normalizedStudios = normalizeStudio(data);
    const normalizedEpisodes = normalizeEpisodes(data);
    const normalizedDurationMinutes = normalizeDurationMinutes(data);
    const normalizedYears = normalizeYear(data);
    const normalizedScores = normalizeScore(data);
    const normalizedRanks = normalizeRank(data);
    const normalizedPopularities = normalizePopularity(data);
    const normalizedScoredBy = normalizeScoredBy(data);
    const normalizedMembers = normalizeMembers(data);

    const featureTensor = tf.tensor2d([
        ...normalizedGenres,
        ...normalizedSeasons,
        ...normalizedLicensors,
        ...normalizedProducers,
        ...normalizedRatings,
        ...normalizedSources,
        ...normalizedTypes,
        ...normalizedStatuses,
        ...normalizedStudios,
        ...normalizedEpisodes,
        ...normalizedDurationMinutes,
        ...normalizedYears,
        ...normalizedScores,
        ...normalizedRanks,
        ...normalizedPopularities,
        ...normalizedScoredBy,
        ...normalizedMembers
    ]);

    return featureTensor;
}


module.exports = {
    normalizeGenres,
    normalizeOrder,
    normalizeStatus,
    normalizeEpisodes,
    jaccardSimilarity,
    normalizeLicensor,
    normalizeProducer,
    normalizeRating,
    normalizeSource,
    normalizeType,
    normalizeStudio,
    normalizeYear,
    normalizeScore,
    normalizeRank,
    normalizePopularity,
    normalizeScoredBy,
    normalizeMembers
};

// pearson correlation, matrix multiplication/factorization
// consider combining rank and popularity into one, revisit all normalization and all properties.