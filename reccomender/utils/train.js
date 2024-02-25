import { distance, similarity } from 'ml-distance';
import { kmeans } from 'ml-kmeans';
import * as ss from 'simple-statistics';

import { createFeatureTensor } from './normalize.js';
import { checkFileExists, readJSONFile } from './readFile.js';
import { initializeDataFile } from './utils.js';
import { writeData } from './writeFile.js';

let path;
let url;
let fileURLToPath;
let dirname;
let __filename, __dirname;

if (typeof window === 'undefined') {
    path = require('path');
    url = require('url');
    fileURLToPath = url.fileURLToPath;
    dirname = path.dirname;
    __filename = fileURLToPath(import.meta.url);
    __dirname = dirname(__filename);
}

async function returnOptimalK(featureArray, max, distanceFunction, fileName) {
    const results = [];
    for (let k = 2; k <= max; k++) {
        try {
            const result = await kmeans(featureArray, k, {
                initialization: 'kmeans++',
                distanceFunction: distanceFunction,
            });
            const wcss = result.computeInformation(featureArray).reduce((sum, info) => sum + info.error, 0);
            const assignments = result.clusters;
            const silhouetteScore = ss.silhouetteMetric(featureArray, assignments);
            results.push({ k, wcss, silhouetteScore });
        } catch (error) {
            console.error(`Error computing KMeans for k=${k}:`, error);
            await writeData(fileName, results);
            throw error;
        }
    }

    const optimalK = results.reduce((prev, curr) => (curr.wcss < prev.wcss ? curr : prev)).k;
    const optimalS = results.reduce((prev, curr) =>
        Math.abs(curr.silhouetteScore - 1) < Math.abs(prev.silhouetteScore - 1) ? curr : prev,
    ).silhouetteScore;
    await writeData(fileName, results);
    return { optimalK, optimalS };
}

async function returnKmeansModel(featureArray, k, distanceFunction) {
    const modelFileName = 'kmeans.json';
    const modelFilePath = path.resolve(__dirname, `../data/${modelFileName}`);
    const modelExists = await checkFileExists(modelFileName);

    if (modelExists) {
        console.log('Using existing KMeans model from file.');
        const kmeansModel = await readJSONFile(modelFilePath);
        return kmeansModel;
    } else {
        console.log('KMeans model file not found. Training a new model.');
        const kmeansModel = await kmeans(featureArray, k, {
            initialization: 'kmeans++',
            distanceFunction: distanceFunction,
        });
        await writeData(modelFileName, kmeansModel);
        return kmeansModel;
    }
}
export { returnOptimalK, returnKmeansModel };
