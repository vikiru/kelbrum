const tf = require('@tensorflow/tfjs');
const { returnUniqueArray, constructDataFiles } = require('./utils/utils');
const { normalizeOrder, normalizeEpisodes } = require('./utils/normalize');

async function main() {
    try {
        const filteredData = await constructDataFiles();
        const normalizedScores = filteredData.map((d) => parseFloat(d.score) / 10);
        // const encodedGenres = filteredData.map((d) => normalizeGenres(d, uniqueGenres));
        // const encodedTypes = filteredData.map((d) => (d.type === 'TV' ? 1 : 0));
        // const normalizedRanks = normalizeOrder(filteredData, 'rank');
        // const normalizedPopularities = normalizeOrder(filteredData, 'popularity');
        // const normalizedEpisodes = normalizeEpisodes(filteredData);
        // const combinedFeatures = filteredData.map((d, index) => {
          //  return [
           //     normalizedScores[index],
            //    encodedTypes[index],
                //  ...encodedGenres[index],
            //    normalizedRanks[index],
             //   normalizedPopularities[index],
             //   normalizedEpisodes[index],
          //  ];
        //});
        //const featuresTensor = tf.tensor2d(combinedFeatures);
        // return data;
    } catch (err) {
        console.error('Failed to read JSON file:', err);
    }
}
main();
