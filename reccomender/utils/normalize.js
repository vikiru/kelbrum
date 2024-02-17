const { returnUniqueArray } = require("./utils");
const tf = require('@tensorflow/tfjs');

function jaccardSimilarity(setA, setB) {
    const intersection = new Set([...setA].filter((x) => setB.has(x)));
    const union = new Set([...setA, ...setB]);
    return intersection.size / union.size;
}

function normalizeGenres(anime) {
    const uniqueGenres = returnUniqueArray(anime, 'genres');
    const normalizedGenres = anime.map((entry) => {
        return uniqueGenres.map((genre) => (entry.genres.includes(genre) ?  1 :  0));
    });
    return normalizedGenres;
}

function normalizeSeason(data) {
    const seasons = ['spring', 'summer', 'fall', 'winter'];
    return data.map(entry => {
        return seasons.map(season => (entry.season === season ?  1 :  0));
    });
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

function normalizeStudio(data) {
    const uniqueStudios = returnUniqueArray(data, 'studio');
    const normalizedStudios = data.map((entry) => {
        return uniqueStudios.map((studio) => (entry.studio === studio ?   1 :   0));
    });
    return normalizedStudios;
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

function normalizeEpisodes(data) {
    const uniqueEpisodes = returnUniqueArray(data, 'episodes', ['Unknown']);
    const episodes = data.map((d) => (d.episodes === 'Unknown' ? -1 : d.episodes));
    const minEpisodes = Math.min(...uniqueEpisodes);
    const maxEpisodes = Math.max(...uniqueEpisodes);

    return episodes.map((ep) => {
        return (ep === -1 || maxEpisodes === minEpisodes) ?   0 : (ep - minEpisodes) / (maxEpisodes - minEpisodes);
    });
}

function normalizeDurationMinutes(data) {
    const uniqueDurations = returnUniqueArray(data, 'durationMinutes', ['Unknown']);
    const durations = data.map((d) => (d.durationMinutes === 'Unknown' ? -1 : d.durationMinutes));
    const minDuration = Math.min(...uniqueDurations);
    const maxDuration = Math.max(...uniqueDurations);

    return durations.map((duration) => {
        return (duration === -1 || maxDuration === minDuration) ?  0 : (duration - minDuration) / (maxDuration - minDuration);
    });
}

function normalizeYear(data) {
    const uniqueYears = returnUniqueArray(data, 'year', ['Unknown']);
    const years = data.map((d) => (d.year === 'Unknown' ? -1 : d.year));
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
    const normalizationFunctions = [
        { func: normalizeGenres, is1D: false }, 
        { func: normalizeType, is1D: false }, 
        { func: normalizeSource, is1D: false }, 
        { func: normalizeProducer, is1D: false },
        { func: normalizeStudio, is1D: false }, 
        { func: normalizeSeason, is1D: false }, 
        { func: normalizeYear, is1D: true },
        { func: normalizeScore, is1D: true }, 
        { func: normalizeEpisodes, is1D: true },
        { func: normalizeDurationMinutes, is1D: true }, 
        { func: normalizeRank, is1D: true }, 
        { func: normalizePopularity, is1D: true }, 
        { func: normalizeScoredBy, is1D: true },
        { func: normalizeMembers, is1D: true },
    ];

    const allTensors = normalizationFunctions.map(({ func, is1D }) => {
        const normalizedData = func(data);
        let tensor;
        if (is1D) {
            tensor = tf.tensor1d(normalizedData);
            tensor = tensor.expandDims(1);
        } else {
            tensor = tf.tensor2d(normalizedData);
        }
        return tensor;
    });
    const concatenatedTensor = tf.concat(allTensors,   1);
    return concatenatedTensor;
}

function calculateFeatureVariance(data) {
    const length =  11925;
    const numFeatures = data[0].length;
    const featureVariances = Array(numFeatures).fill(0);
    const sums = Array(numFeatures).fill(0);
    const squaredSums = Array(numFeatures).fill(0);

    data.forEach(tensor => {
        tensor.forEach((featureValue, index) => {
            sums[index] += featureValue;
            squaredSums[index] += Math.pow(featureValue,  2);
        })
    });

    const averages = sums.map(s => s / length);
    const variances = squaredSums.map((squaredSum, index) => {
        const variance = squaredSum / length - Math.pow(averages[index],  2);
        return variance >  0 ? variance :  0; // Ensure variance is non-negative
    });
    console.log(variances);

    return variances;
}


function validateTensors(tensors) {
    tensors.forEach((tensor, index) => {
        const hasNaN = tf.tidy(() => {
            return tf.logicalNot(tf.isNaN(tensor)).all().logicalNot();
        });

        if (hasNaN.dataSync()[0]) {
            console.error(`Tensor at index ${index} contains NaN values.`);
            console.error(tensor);
        } else {
            console.log(`Tensor at index ${index} does not contain NaN values.`);
        }
    });
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
    normalizeMembers,
    createFeatureTensor,
    calculateFeatureVariance,
};

// pearson correlation, matrix multiplication/factorization
// consider combining rank and popularity into one, revisit all normalization and all properties.