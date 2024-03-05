import { distance } from 'ml-distance';

/**
 * Asynchronously retrieves anime data based on recommendations and input data.
 *
 * @param {Array} recommendations - The list of anime recommendations.
 * @param {Array} data - The input data containing anime information.
 * @returns {Array} The sorted anime data based on similarity.
 */
async function retrieveAnimeData(recommendations, data) {
    const indexes = new Set(recommendations.map((r) => r.index));
    const animeData = data.filter((d) => indexes.has(d.id));
    animeData.forEach((d) => {
        d.similarity = recommendations.find((r) => r.index === d.id).similarity.toFixed(2);
    });
    return animeData.sort((a, b) => a.similarity - b.similarity);
}

/**
 * Shuffles the elements of the input array in random order.
 *
 * @param {Array} arr - The array to be shuffled
 * @returns {undefined} This function does not return anything
 */
async function shuffleRandom(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
}

/**
 * A function that returns a list of random recommendations based on similarities.
 *
 * @param {Array} similarities - The array of similarities to filter and use for recommendations
 * @returns {Array} An array of recommended items sorted by similarity
 */
async function returnRandomRecommendations(similarities, MAX_ANIME = 100) {
    const filteredSimilarities = similarities
        .sort((a, b) => a.similarity - b.similarity);
    console.log(similarities);
    const recommendations = filteredSimilarities.slice(0, MAX_ANIME);
    return recommendations;
}

/**
 * Calculate similarities between specified cluster and other clusters based on given feature array and index.
 *
 * @param {number} clusterNumber - The cluster number to compare with
 * @param {array} clusters - Array of cluster numbers
 * @param {array} featureArray - Array of feature tensors
 * @param {number} id - The index of the anime to compare
 * @param {array} excludedIds - Array of excluded anime indices
 * @returns {array} Sorted array of objects containing index and similarity
 */
async function returnClusterSimilarities(clusterNumber, clusters, featureArray, id, excludedIds = []) {
    const MAX_THRESHOLD = Infinity;

    const excludedSet = new Set(excludedIds);
    const otherAnimeIndices = clusters.reduce((indices, cluster, index) => {
        if (cluster === clusterNumber && index !== id && !excludedSet.has(index)) {
            indices.push(index);
        }
        return indices;
    }, []);

    if (otherAnimeIndices.length === 0) {
        return [];
    }

    const tensor = featureArray[id];
    const similarityResults = await Promise.all(
        otherAnimeIndices.map(async (otherIndex) => {
            const otherTensor = featureArray[otherIndex];
            try {
                const similarity = await compareTensors(tensor, otherTensor);
                return { index: otherIndex, similarity };
            } catch (error) {
                console.error('Error comparing tensors:', error);
                return null;
            }
        }),
    );

    return similarityResults.filter((result) => result !== null && result.similarity <= MAX_THRESHOLD).sort((a, b) => a.similarity - b.similarity);
}

function sliceTensor(tensor, start, end) {
    return tensor.slice(start, end);
}

function getDistance(property, tensorA, tensorB) {
    switch (property) {
        case 'type':
            return distance.manhattan(tensorA, tensorB);
        case 'source':
            return distance.dice(tensorA, tensorB);
        case 'rating':
            return distance.manhattan(tensorA, tensorB);
        case 'genres':
            return distance.dice(tensorA, tensorB);
        case 'demographics':
            return distance.manhattan(tensorA, tensorB);
        case 'themes':
            return distance.dice(tensorA, tensorB);
        case 'duration':
            return distance.manhattan(tensorA, tensorB);
        case 'score':
            return distance.manhattan(tensorA, tensorB);
        case 'synopsis':
            return distance.dice(tensorA, tensorB);
    }
}

function weightedDistance(tensorA, tensorB) {
    const indices = {
        type: [0, 1],
        source: [1, 18],
        rating: [18, 19],
        genres: [19, 38],
        demographics: [38, 39],
        themes: [39, 90],
        synopsis: [90, 339],
        duration: [339, 340],
        score: [340, 341]
    };

    const weights = {
        type: 0.5,
        source: 0.7,
        rating: 0.5,
        genres: 0.1,
        demographics: 0.1,
        themes: 0.1,
        synopsis: 0.1,
        duration: 0.5,
        score: 0.5
    };
    const weightSum = Object.values(weights).reduce((sum, currentValue) => sum + currentValue, 0);

    let distanceSum = 0;

    for (const [feature, [start, end]] of Object.entries(indices)) {
        const firstTensor = sliceTensor(tensorA, start, end);
        const secondTensor = sliceTensor(tensorB, start, end);
        const weight = weights[feature];
        const distance = getDistance(feature, firstTensor, secondTensor);
        //console.log(`Feature: ${feature}, Raw Distance: ${distance}, Weighted Distance: ${distance * weight}`);

        distanceSum += distance * weight;
    }

    return distanceSum / weightSum;
}


async function compareTensors(tensorA, tensorB) {
    return weightedDistance(tensorA, tensorB);
}

export { shuffleRandom, returnClusterSimilarities, retrieveAnimeData, returnRandomRecommendations, weightedDistance };
