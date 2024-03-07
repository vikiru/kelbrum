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
    const filteredSimilarities = similarities.sort((a, b) => a.similarity - b.similarity);
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
    //const MAX_THRESHOLD = 0.4;
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

    return similarityResults.filter((result) => result !== null).sort((a, b) => a.similarity - b.similarity);
}

/**
 * Creates new tensors based on the input tensors, filtering out elements where either tensorA or tensorB is equal to 1.
 *
 * @param {Array} tensorA - The first input tensor
 * @param {Array} tensorB - The second input tensor
 * @returns {Object} An object containing the new tensors newTensorA and newTensorB
 */
function createNewTensors(tensorA, tensorB) {
    const newTensorA = [];
    const newTensorB = [];

    for (let i = 0; i < tensorA.length; i++) {
        const tensorAValue = tensorA[i];
        const tensorBValue = tensorB[i];
        if (tensorAValue === 1 || tensorBValue === 1) {
            newTensorA.push(tensorAValue);
            newTensorB.push(tensorBValue);
        }
    }
    return { newTensorA, newTensorB };
}

/**
 * Slices a given tensor from the start index to the end index.
 *
 * @param {Tensor} tensor - The tensor to be sliced
 * @param {number} start - The start index of the slice
 * @param {number} end - The end index of the slice
 * @returns {Tensor} The sliced tensor
 */
function sliceTensor(tensor, start, end) {
    return tensor.slice(start, end);
}

/**
 * Calculate the distance between two tensors based on the given property.
 *
 * @param {string} property - The property based on which the distance is calculated.
 * @param {Tensor} tensorA - The first tensor.
 * @param {Tensor} tensorB - The second tensor. {number} The distance between the two tensors.
 */
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
        case 'durationMinutes':
            return distance.manhattan(tensorA, tensorB);
        case 'score':
            return distance.manhattan(tensorA, tensorB);
        case 'synopsis':
            return distance.dice(tensorA, tensorB);
        case 'year':
            return distance.manhattan(tensorA, tensorB);
    }
}

/**
 * Calculate the weighted distance between two tensors based on the specified indices and weights.
 *
 * @param {Object} tensorA - The first tensor
 * @param {Object} tensorB - The second tensor {number} the weighted distance between the two tensors
 */
function weightedDistance(tensorA, tensorB) {
    const indices = {
        type: [0, 1],
        source: [1, 18],
        rating: [18, 19],
        genres: [19, 38],
        demographics: [38, 39],
        themes: [39, 90],
        synopsis: [90, 339],
        durationMinutes: [339, 340],
        score: [340, 341],
        year: [341, 342],
    };

    const weights = {
        type: 0.8,
        source: 0.2,
        rating: 0.5,
        genres: 0.4,
        demographics: 0.5,
        themes: 0.55,
        synopsis: 0.2,
        score: 0.1,
        durationMinutes: 1,
        year: 0.1,
    };

    const shouldCreateNew = {
        type: false,
        source: false,
        rating: false,
        genres: true,
        demographics: false,
        themes: true,
        synopsis: true,
        score: false,
        durationMinutes: false,
        year: false,
    };
    const weightSum = Object.values(weights).reduce((sum, currentValue) => sum + currentValue, 0);

    let distanceSum = 0;

    for (const [feature, [start, end]] of Object.entries(indices)) {
        const firstTensor = sliceTensor(tensorA, start, end);
        const secondTensor = sliceTensor(tensorB, start, end);
        const weight = weights[feature];
        let distance = 0;

        if (shouldCreateNew[feature]) {
            const { newTensorA, newTensorB } = createNewTensors(firstTensor, secondTensor);
            distance = newTensorA.length > 0 ? getDistance(feature, newTensorA, newTensorB) : 0;
        } else {
            distance = getDistance(feature, firstTensor, secondTensor);
        }

        if (isNaN(distance)) {
            distanceSum += 0;
        } else {
            distanceSum += distance * weight;
        }
    }

    return distanceSum / weightSum;
}

/**
 * Compares two tensors using a given distance function.
 *
 * @param {type} tensorA - The first tensor
 * @param {type} tensorB - The second tensor
 * @returns {type} The result of the comparison
 */
async function compareTensors(tensorA, tensorB) {
    return weightedDistance(tensorA, tensorB);
}

export { shuffleRandom, returnClusterSimilarities, retrieveAnimeData, returnRandomRecommendations, weightedDistance };
