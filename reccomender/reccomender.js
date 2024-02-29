import * as tf from '@tensorflow/tfjs';
import { distance, similarity } from 'ml-distance';

/**
 * Asynchronously retrieves anime data based on recommendations and input data.
 *
 * @param {Array} recommendations - The list of anime recommendations.
 * @param {Array} data - The input data containing anime information.
 * @returns {Array} The sorted anime data based on similarity.
 */
async function retrieveAnimeData(recommendations, data) {
    const indexes = recommendations.map((r) => r.index);
    const animeData = data.filter((d) => indexes.includes(d.id));
    animeData.forEach((d) => {
        d.similarity = (recommendations.find((r) => r.index === d.id).similarity * 100).toFixed(2);
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
async function returnRandomRecommendations(similarities) {
    const MIN_THRESHOLD = 0.9;
    const MAX_ANIME = 100;

    const filteredSimilarities = similarities.filter((s) => 1 - s.similarity >= MIN_THRESHOLD);
    filteredSimilarities.sort((a, b) => a.similarity - b.similarity);

    const selectedIds = new Set();
    const recommendations = [];

    for (const item of filteredSimilarities) {
        const similarity = 1 - item.similarity;
        if (recommendations.length === MAX_ANIME) {
            break;
        }
        if (!selectedIds.has(item.index) && similarity >= MIN_THRESHOLD) {
            selectedIds.add(item.index);
            recommendations.push(item);
        }
    }

    console.log(recommendations);

    return Array.from(recommendations).sort((a, b) => a.similarity - b.similarity);
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
    const otherAnimeIndices = clusters.reduce((indices, cluster, index) => {
        if (cluster === clusterNumber && index !== id && !excludedIds.includes(index)) {
            indices.push(index);
        }
        return indices;
    }, []);

    if (otherAnimeIndices.length === 0) {
        console.log('No other anime found in the specified cluster.');
        return [];
    }

    const similarityResults = await Promise.all(
        otherAnimeIndices.map(async (otherIndex) => {
            const tensor = featureArray[id];
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
 * Calculate the custom distance between two tensors.
 *
 * @param {Array} tensorA - The first tensor
 * @param {Array} tensorB - The second tensor
 * @returns {number} The custom distance between the two tensors
 */
function customDistance(tensorA, tensorB) {
    let tensorDistance = 0;
    let weightSum = 0;

    const categoricalWeight = 0.7;
    const numericalWeight = 1 - categoricalWeight;

    const numCategoricalFeatures = 7;

    const categoricalA = tensorA.slice(0, numCategoricalFeatures);
    const categoricalB = tensorB.slice(0, numCategoricalFeatures);
    const continuousA = tensorA.slice(numCategoricalFeatures);
    const continuousB = tensorB.slice(numCategoricalFeatures);

    const categoricalDistance = distance.gower(categoricalA, categoricalB) * categoricalWeight;
    const numericalDistance = distance.gower(continuousA, continuousB) * numericalWeight;

    tensorDistance = categoricalDistance + numericalDistance;

    weightSum =
        numCategoricalFeatures * categoricalWeight + (tensorA.length - numCategoricalFeatures) * numericalWeight;

    if (weightSum === 0) {
        console.error('Weight sum is zero, cannot divide by zero');
        return NaN;
    }

    return tensorDistance / weightSum;
}

function compareTensors(tensorA, tensorB) {
    return customDistance(tensorA, tensorB);
}

export { shuffleRandom, customDistance, returnClusterSimilarities, retrieveAnimeData, returnRandomRecommendations };
