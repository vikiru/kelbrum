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
        if (index !== id && !excludedSet.has(index)) {
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


/**
 * Calculate the custom distance between two tensors.
 *
 * @param {Array} tensorA - The first tensor
 * @param {Array} tensorB - The second tensor
 * @returns {number} The custom distance between the two tensors
 */
async function customDistance(tensorA, tensorB) {
    let tensorDistance = 0;
    let weightSum = 0;

    const categoricalWeight = 0.7;
    const numericalWeight = 0.3;

    const numCategoricalFeatures = 6;

    const categoricalA = tensorA.slice(0, numCategoricalFeatures);
    const categoricalB = tensorB.slice(0, numCategoricalFeatures);
    const continuousA = tensorA.slice(numCategoricalFeatures);
    const continuousB = tensorB.slice(numCategoricalFeatures);

    const categoricalDistance = distance.gower(categoricalA, categoricalB) * categoricalWeight;
    const numericalDistance = distance.gower(continuousA, continuousB) * numericalWeight;

    tensorDistance = categoricalDistance;

    return tensorDistance;
}


function weightedDistance(tensorA, tensorB){
    const typeStart = 0;
    const typeEnd = typeStart + 4;
    const sourceStart = typeEnd;
    const sourceEnd = sourceStart + 17;
    const ratingStart = sourceEnd;
    const ratingEnd = ratingStart + 6;
    const genresStart = ratingEnd;
    const genresEnd = genresStart + 19;
    const demographicsStart = genresEnd;
    const demographicsEnd = demographicsStart + 5;
    const themeStart = demographicsEnd;
    const themeEnd = themeStart + 51;
    const synopsisStart = themeEnd;
    const synopsisEnd = synopsisStart + 223;

    const typeTensorA = tensorA.slice(typeStart, typeEnd);
    const typeTensorB = tensorB.slice(typeStart, typeEnd);
    
    const sourceTensorA = tensorA.slice(sourceStart, sourceEnd);
    const sourceTensorB = tensorB.slice(sourceStart, sourceEnd);
    
    const ratingTensorA = tensorA.slice(ratingStart, ratingEnd);
    const ratingTensorB = tensorB.slice(ratingStart, ratingEnd);

    const genresTensorA = tensorA.slice(genresStart, genresEnd);
    const genresTensorB = tensorB.slice(genresStart, genresEnd);

    const demographicsTensorA = tensorA.slice(demographicsStart, demographicsEnd);
    const demographicsTensorB = tensorB.slice(demographicsStart, demographicsEnd);

    const themesTensorA = tensorA.slice(themeStart, themeEnd);
    const themesTensorB = tensorB.slice(themeStart, themeEnd);

    const synopsisTensorA = tensorA.slice(synopsisStart, synopsisEnd);
    const synopsisTensorB = tensorB.slice(synopsisStart, synopsisEnd);

    const synopsisWeight = 0.1;
    const themesWeight = 0.1;
    const genresWeight = 0.3;
    const demographicsWeight = 0;
    const typeWeight = 1;
    const sourceWeight = 1;
    const ratingWeight = 0.5;

    const typeLength = 4;
    const sourceLength = 17;
    const ratingLength = 6;
    const genresLength = 19;
    const demographicsLength = 5;
    const themesLength = 51;
    const synopsisLength = 223;

    const weightSum = (typeLength * typeWeight) + (sourceLength * sourceWeight) + (ratingLength * ratingWeight) + (genresWeight * genresLength) +
    (genresWeight * demographicsLength) + (genresWeight * themesLength) + (synopsisWeight * synopsisLength);

    const typeDistance = distance.dice(typeTensorA, typeTensorB) * typeWeight;
    const sourceDistance = distance.manhattan(sourceTensorA, sourceTensorB) * sourceWeight;
    const ratingDistance = distance.manhattan(ratingTensorA, ratingTensorB) * ratingWeight;
    const genresDistance = distance.manhattan(genresTensorA, genresTensorB) * genresWeight;
    const themeDistance = distance.manhattan(themesTensorA, themesTensorB) * themesWeight;
    const demographicsDistance = distance.squaredEuclidean(demographicsTensorA, demographicsTensorB) * demographicsWeight;
    const synopsisDistance = distance.jaccard(synopsisTensorA, synopsisTensorB) * synopsisWeight;

    const distanceSum = typeDistance + sourceDistance + ratingDistance + genresDistance + demographicsDistance + themeDistance + synopsisDistance;
    return distanceSum;
}

async function compareTensors(tensorA, tensorB) {
    return weightedDistance(tensorA, tensorB);
}

export { shuffleRandom, customDistance, returnClusterSimilarities, retrieveAnimeData, returnRandomRecommendations, weightedDistance };
