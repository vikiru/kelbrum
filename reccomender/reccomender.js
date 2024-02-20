const tf = require('@tensorflow/tfjs');
const { initializeDataFile, returnUniqueArray, writeData, sortData } = require('./utils/utils');
const { createFeatureTensor, calculateFeatureVariance } = require('./utils/normalize');
const { returnKmeansModel } = require('./utils/train');
const { similarity, distance } = require('ml-distance');

// dice, jaccard, tanimoto, sorensen. k = 10

async function main() {
    try {
        const data = await initializeDataFile();
        const featureTensor = await createFeatureTensor(data);
        const featureArray = featureTensor.arraySync();
        const kmeans = await returnKmeansModel(featureArray, 10, distance.jaccard);
    } catch (err) {
        console.error('Error occured:', err);
    }
}

main();
