import { distance, similarity } from 'ml-distance';
import { kmeans } from 'ml-kmeans';
import { dirname } from 'path';
import path from 'path';
import * as ss from 'simple-statistics';
import { fileURLToPath } from 'url';

import { checkFileExists, readJSONFile } from './readFile.js';
import { writeData } from './writeFile.js';

const __filename = fileURLToPath(import.meta.url);

const __dirname = dirname(__filename);
/**
 * Asynchronously computes the optimal value of k for k-means clustering using the given feature array, maximum value of
 * k, distance function, and file name.
 *
 * @param {Array} featureArray - The array of feature vectors
 * @param {number} max - The maximum value of k
 * @param {Function} distanceFunction - The function to compute distance between feature vectors
 * @param {string} fileName - The name of the file for writing data
 * @returns {Promise<Object>} An object containing the optimal value of k and the silhouette score
 */
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
            results.push({ k, wcss });
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

/**
 * Asynchronously returns a KMeans model based on the provided feature array, number of clusters, and distance function.
 *
 * @param {Array} featureArray - The array of features used for training the model
 * @param {number} k - The number of clusters
 * @param {Function} distanceFunction - The distance function used for clustering
 * @returns {Promise<Object>} The KMeans model
 */
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
