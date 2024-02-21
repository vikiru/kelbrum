const tf = require('@tensorflow/tfjs');
const { initializeDataFile, returnUniqueArray, writeData, sortData } = require('./utils/utils');
const { createFeatureTensor, calculateFeatureVariance } = require('./utils/normalize');
const { returnKmeansModel, returnOptimalK } = require('./utils/train');
const { similarity, distance } = require('ml-distance');

// dice, jaccard, tanimoto, sorensen. k = 10

// k = 10, 37 - 40, 99, 100
// 37, 43, 47 51 52 -< k
async function main() {
    try {
        const data = await initializeDataFile();
        const featureTensor = await createFeatureTensor(data);
        const featureArray = featureTensor.arraySync();
        //console.log(featureArray[0]);
        //console.log(featureArray[1]);
        const kmeans = await returnKmeansModel(featureArray, 43, distance.dice);
        const id = data.findIndex(d => d.malID === 1); // 25013 - akayona, 6, 21
        const entry = data[id];
        const cluster = kmeans.clusters[entry.id];
        const results = await returnClusterSimilarities(cluster, kmeans.clusters, featureArray, entry.id, [entry.id]);
        console.log(data[id].title);
        const topResults = results.slice(0, 10);
        topResults.forEach(t => {
            const ind = t.index;
            console.log(data[ind].title);
            console.log(t.similarity);
        })
       console.log(results);
    } catch (err) {
        console.error('Error occured:', err);
    }
}


async function returnClusterSimilarities(clusterNumber, clusters, featureArray, id, excludedIds = []) {
    const otherAnimeIndices = clusters.reduce((indices, cluster, index) => {
        if (cluster === clusterNumber && index !== id && !excludedIds.includes(index)) {
            indices.push(index);
        }
        return indices;
    }, []);

    if (otherAnimeIndices.length ===   0) {
        console.log('No other anime found in the specified cluster.');
        return [];
    }

    const similarityResults = await Promise.all(otherAnimeIndices.map(async (otherIndex) => {
        const tensor = featureArray[id];
        const otherTensor = featureArray[otherIndex];
        try {
            const similarity = await compareTensors(tensor, otherTensor);
            return { index: otherIndex, similarity };
        } catch (error) {
            console.error('Error comparing tensors:', error);
            return null;
        }
    }));

    return similarityResults.filter(result => result !== null).sort((a, b) => b.similarity - a.similarity);
}

function customDistance(tensorA, tensorB) {
    let tensorDistance =   0;
    let weightSum =   0;

    const numCategoricalFeatures =   11;

    const categoricalA = tensorA.slice(0, numCategoricalFeatures);
    const categoricalB = tensorB.slice(0, numCategoricalFeatures);
    const continuousA = tensorA.slice(numCategoricalFeatures);
    const continuousB = tensorB.slice(numCategoricalFeatures);

    const categoricalDistance = similarity.cosine(categoricalA, categoricalB) *   0.8;
    const numericalDistance = (1 - similarity.cosine(continuousA, continuousB)) *   0.2;

    tensorDistance = categoricalDistance + numericalDistance;

    weightSum = numCategoricalFeatures *  0.8  + (tensorA.length - numCategoricalFeatures) *   0.2;

    if (weightSum ===   0) {
        console.error('Weight sum is zero, cannot divide by zero');
        return NaN;
    }

    return  tensorDistance / weightSum;
}

// dice, gower, jaccard, lorentzian, sorensen
function compareTensors(tensorA, tensorB) {
    return similarity.cosine(tensorA, tensorB);
}


main();

// add function to reccomend random 10 unique anime within cluster
// function for most 10 unique similar anime
// start working on ui (user enters up to 10 titles, auto complete
// add a list of future improvements 