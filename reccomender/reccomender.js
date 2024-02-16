const tf = require('@tensorflow/tfjs');
const { returnUniqueArray, constructDataFiles, initializeDataFiles } = require('./utils/utils');
const { normalizeOrder, normalizeEpisodes } = require('./utils/normalize');

async function main() {
    try {
         const data = await initializeDataFiles();
         console.log(data.length);

    } catch (err) {
        console.error('Failed to read JSON file:', err);
    }
}
main();


// TODO: finish cleanup of data retrieval (Ensure props that should be int/float are not string)
// Check if entries.json exists, if not read csv, fetch missing data and write to file
// Add function to check if an entry needs updating.
// TODO: Normalize all properties as much as possible
// TODO: Use unsupersived learning via knn or some other algorithm
// TODO: Experiment with different weights and see how reccomendations are, experiment with different similarity measures. Add
// functions to preprocess user input / add a class for it or use existing userinteraction and modify.