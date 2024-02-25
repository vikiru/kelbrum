import * as tf from '@tensorflow/tfjs';
import { distance, similarity } from 'ml-distance';

import { createFeatureTensor } from './utils/normalize.js';
import { returnKmeansModel } from './utils/train.js';
import { initializeDataFile, writeData } from './utils/utils.js';

async function retrieveAnimeData(recommendations, data) {
    const indexes = recommendations.map((r) => r.index);
    const animeData = data.filter((d) => indexes.includes(d.id));
    animeData.forEach((d) => {
        d.similarity = (recommendations.find((r) => r.index === d.id).similarity * 100).toFixed(2);
    });
    return animeData.sort((a, b) => b.similarity - a.similarity);
}

async function shuffleRandom(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
}

async function returnRandomRecommendations(similarities) {
    const MIN_THRESHOLD = 0.8;
    const MAX_ANIME = 100;

    const filteredSimilarities = similarities.filter((s) => s.similarity >= MIN_THRESHOLD);
    filteredSimilarities.sort((a, b) => b.similarity - a.similarity);

    shuffleRandom(filteredSimilarities);

    const selectedIds = new Set();
    const recommendations = [];

    for (const item of filteredSimilarities) {
        if (recommendations.length === MAX_ANIME) {
            break;
        }
        if (!selectedIds.has(item.index)) {
            selectedIds.add(item.index);
            recommendations.push(item);
        }
    }

    return Array.from(recommendations).sort((a, b) => b.similarity - a.similarity);
}

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

    return similarityResults.filter((result) => result !== null).sort((a, b) => b.similarity - a.similarity);
}

function customDistance(tensorA, tensorB) {
    let tensorDistance = 0;
    let weightSum = 0;

    const numCategoricalFeatures = 11;

    const categoricalA = tensorA.slice(0, numCategoricalFeatures);
    const categoricalB = tensorB.slice(0, numCategoricalFeatures);
    const continuousA = tensorA.slice(numCategoricalFeatures);
    const continuousB = tensorB.slice(numCategoricalFeatures);

    const categoricalDistance = similarity.cosine(categoricalA, categoricalB) * 0.8;
    const numericalDistance = (1 - similarity.cosine(continuousA, continuousB)) * 0.2;

    tensorDistance = categoricalDistance + numericalDistance;

    weightSum = numCategoricalFeatures * 0.8 + (tensorA.length - numCategoricalFeatures) * 0.2;

    if (weightSum === 0) {
        console.error('Weight sum is zero, cannot divide by zero');
        return NaN;
    }

    return tensorDistance / weightSum;
}

// dice, gower, jaccard, lorentzian, sorensen
function compareTensors(tensorA, tensorB) {
    return similarity.cosine(tensorA, tensorB);
}

// dice, jaccard, tanimoto, sorensen. k = 10

// k = 10, 37 - 40, 99, 100
// 37, 43, 47 51 52 -< k
async function main() {
    try {
        const data = await initializeDataFile();
        const featureTensor = await createFeatureTensor(data);
        const featureArray = featureTensor.arraySync();
        const titleIDMap = data.flatMap((d) => {
            const uniqueTitles = Array.from(new Set(d.titles));
            return { title: d.title, synonyms: uniqueTitles, value: d.id };
        });
        await writeData('titleIDMap.json', titleIDMap);
        await writeData('featureArray.json', featureArray);
        const kmeans = await returnKmeansModel(featureArray, 4, customDistance);
        const id = data.findIndex((d) => d.malID === 4898); // 25013 - akayona, 6, 21
        const entry = data[id];
        const cluster = kmeans.clusters[entry.id];
        const results = await returnClusterSimilarities(cluster, kmeans.clusters, featureArray, id);
        const reccs = await returnRandomRecommendations(results);
        const topResults = await retrieveAnimeData(reccs, data);
        topResults.forEach((d) => {
            console.log(d.title);
        });
    } catch (err) {
        console.error('Error occured:', err);
    }
}

export { shuffleRandom, customDistance, returnClusterSimilarities, retrieveAnimeData, returnRandomRecommendations };
// start working on ui (user enters up to 10 titles, auto complete
