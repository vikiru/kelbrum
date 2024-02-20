const { kmeans } = require('ml-kmeans');
const { writeData } = require('./writeFile');
const { similarity, distance } = require('ml-distance');
const ss = require('simple-statistics');
const { createFeatureTensor } = require('./normalize');
const { initializeDataFile } = require('./utils');
const path = require('path');
const { readJSONFile, checkFileExists } = require('./readFile');

async function returnOptimalK(data, featureArray, max) {
    const results = [];
    const fileName = 'jaccard.json';
    for (let k = 2; k <= max; k++) {
        try {
            const result = await kmeans(featureArray, k, {
                initialization: 'kmeans++',
                distanceFunction: distance.jaccard,
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
        console.log(kmeansModel);
        return kmeansModel;
    } else {
        console.log('KMeans model file not found. Training a new model.');
        const kmeansModel = await kmeans(featureArray, k, {
            initialization: 'kmeans++',
            distanceFunction: distanceFunction,
        });
        await writeData(modelFilePath, kmeansModel);
        return kmeansModel;
    }
}
module.exports = {
    returnOptimalK,
    returnKmeansModel,
};
