const tf = require('@tensorflow/tfjs');
const { readFile, writeFile, constructDataFiles } = require('./utils/utils');


function jaccardSimilarity(setA, setB) {
    const intersection = new Set([...setA].filter((x) => setB.has(x)));
    const union = new Set([...setA, ...setB]);
    return intersection.size / union.size;
}

function normalizeGenres(anime, uniqueGenres) {
    const inputGenres = anime.genres;
    return uniqueGenres.map((genre) => (inputGenres.includes(genre) ? 1 : 0));
}

function normalizeOrder(data, property) {
    const orders = data.map((d) => d[property]);
    const orderMapping = {};
    let currentOrder = 1;
    const defaultValue = Math.max(...orders) + 1;
    orders.forEach((order) => {
        if (!orderMapping[order] && order >= 1) {
            orderMapping[order] = currentOrder++;
        } else if (order === 0) {
            orderMapping[order] = defaultValue;
        }
    });
    return data.map((d) => orderMapping[d[property]]);
}

function normalizeStatus(data) {
    const uniqueStatus = returnUniqueArray(data, 'status');
    const normalizedStatus = data.map((entry) => {
        return uniqueStatus.map((status) => (entry.status === status ? 1 : 0));
    });
    return normalizedStatus;
}

function normalizeEpisodes(data) {
    const episodes = data.map((d) => (d.episodes >= 1 ? d.episodes : 0.001));
    const minEpisodes = Math.min(...episodes);
    const maxEpisodes = Math.max(...episodes);
    return episodes.map((ep) => (ep - minEpisodes) / (maxEpisodes - minEpisodes));
}

async function main() {
    try {
        const filteredData = await constructDataFiles();
        const normalizedScores = filteredData.map((d) => parseFloat(d.score) / 10);
       // const encodedGenres = filteredData.map((d) => normalizeGenres(d, uniqueGenres));
        const encodedTypes = filteredData.map((d) => (d.type === 'TV' ? 1 : 0));
        const normalizedRanks = normalizeOrder(filteredData, 'rank');
        const normalizedPopularities = normalizeOrder(filteredData, 'popularity');
        const normalizedEpisodes = normalizeEpisodes(filteredData);
        const combinedFeatures = filteredData.map((d, index) => {
            return [
                normalizedScores[index],
                encodedTypes[index],
              //  ...encodedGenres[index],
                normalizedRanks[index],
                normalizedPopularities[index],
                normalizedEpisodes[index],
            ];
        });
        const featuresTensor = tf.tensor2d(combinedFeatures);
       // return data;
    } catch (err) {
        console.error('Failed to read JSON file:', err);
    }
}
main();










// initially content based filtering, then allow for collaborative approach based on user input
// normalize certain properties, one hot encode genres, etc..
// overlap similarity, jaccard similarity, cosine similarity,
// k means, cosine similarity, unsupervised learning, content, collaborative filter, hybrid, get missing data from JikanAPI.
// missing data: trailer, english/japanese title, source?, aired (update to use timestamp), scoredBy, popularity, favorites, studios, season, year, genres,
