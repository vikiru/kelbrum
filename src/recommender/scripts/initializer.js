import * as tf from '@tensorflow/tfjs';
import { distance, similarity } from 'ml-distance';

import { returnKmeansModel, returnOptimalK } from '../dataAccess/train.js';
import { writeData } from '../dataAccess/writeFile.js';
import {
    customDistance,
    retrieveAnimeData,
    returnClusterSimilarities,
    returnRandomRecommendations,
} from '../recommender.js';
import { createFeatureTensor } from '../utils/normalize.js';
import { initializeDataFile } from '../utils/utils.js';

async function main() {
    try {
        const data = await initializeDataFile();
        const featureTensor = await createFeatureTensor(data);
        const featureArray = featureTensor.arraySync();
        const titleIDMap = data.flatMap((d) => {
            const uniqueTitles = Array.from(new Set(d.titles));
            return { title: d.title, synonyms: uniqueTitles, value: d.id };
        });
        const kmeans = await returnKmeansModel(featureArray, 10, customDistance);
        await writeData('featureArray.json', featureArray);
        await writeData('titleIDMap.json', titleIDMap);
        await writeData('kmeans.json', kmeans);
    } catch (err) {
        console.error('Error occured:', err);
    }
}

main();
