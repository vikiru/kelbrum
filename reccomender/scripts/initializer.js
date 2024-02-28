import * as tf from '@tensorflow/tfjs';
import { distance, similarity } from 'ml-distance';

import { returnKmeansModel } from './dataAccess/train.js';
import { createFeatureTensor } from './utils/normalize.js';
import { initializeDataFile, writeData } from './utils/utils.js';

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

main();
