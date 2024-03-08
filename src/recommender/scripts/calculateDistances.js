import { distance, similarity } from 'ml-distance';

import { returnKmeansModel, returnOptimalK } from '../dataAccess/train.js';
import { weightedDistance } from '../recommender.js';
import { createFeatureTensor } from '../utils/normalize.js';
import { initializeDataFile } from '../utils/utils.js';

async function main() {
    const data = await initializeDataFile();
    const featureTensor = await createFeatureTensor(data);
    const featureArray = featureTensor.arraySync();
    const k = 10;
    const distances = {
        chebyshev: {
            distanceFunction: distance.chebyshev,
            fileName: 'statistics/chebyshev.json',
        },
        cosine: {
            distanceFunction: similarity.cosine,
            fileName: 'statistics/cosine.json',
        },
        dice: {
            distanceFunction: distance.dice,
            fileName: 'statistics/dice.json',
        },
        euclidean: {
            distanceFunction: distance.euclidean,
            fileName: 'statistics/euclidean.json',
        },
        gower: {
            distanceFunction: distance.gower,
            fileName: 'statistics/gower.json',
        },
        jaccard: {
            distanceFunction: distance.jaccard,
            fileName: 'statistics/jaccard.json',
        },
        manhattan: {
            distanceFunction: distance.manhattan,
            fileName: 'statistics/manhattan.json',
        },
        sorensen: {
            distanceFunction: distance.sorensen,
            fileName: 'statistics/sorensen.json',
        },
        squaredEuclidean: {
            distanceFunction: distance.squaredEuclidean,
            fileName: 'statistics/squaredEuclidean.json',
        },
        tanimoto: {
            distanceFunction: distance.tanimoto,
            fileName: 'statistics/tanimoto.json',
        },
        weightedDistance: {
            distanceFunction: weightedDistance,
            fileName: 'statistics/weightedDistance.json',
        },
    };

    for (const key in distances) {
        const distance = distances[key];
        const distanceFunction = distance.distanceFunction;
        const fileName = distance.fileName;
        await returnOptimalK(featureArray, k, distanceFunction, fileName);
    }
}

main();
