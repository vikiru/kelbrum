const tf = require('@tensorflow/tfjs');
const { initializeDataFile, returnUniqueArray, writeData, sortData } = require('./utils/utils');
const { createFeatureTensor, calculateFeatureVariance } = require('./utils/normalize');
const { returnKmeansModel, returnOptimalK } = require('./utils/train');
const { similarity, distance } = require('ml-distance');

// dice, jaccard, tanimoto, sorensen. k = 10

// k = 10, 37 - 40, 99, 100
// 37, 43, 47 51 52 -< k
async function main() {
    try {
        const data = await initializeDataFile();
        const featureTensor = await createFeatureTensor(data);
        const featureArray = featureTensor.arraySync();
        //console.log(featureArray[0]);
        //console.log(featureArray[1]);
        const kmeans = await returnKmeansModel(featureArray, 43, distance.dice);
        const id = data.findIndex(d => d.malID === 21); // 25013 - akayona, 6, 21
        const entry = data[id];
        const cluster = kmeans.clusters[entry.id];
        const results = await returnClusterSimilarities(cluster, kmeans.clusters, featureArray, entry.id, [entry.id]);
        console.log(data[id].title);
        const topResults = results.slice(0, 10);
        topResults.forEach(t => {
            const ind = t.index;
            console.log(data[ind].title);
            console.log(t.similarity);
        })
      // console.log(results);
    } catch (err) {
        console.error('Error occured:', err);
    }
}


async function returnClusterSimilarities(clusterNumber, clusters, featureArray, id, excludedIds = []) {
    const otherAnimeIndices = clusters.reduce((indices, cluster, index) => {
        if (cluster === clusterNumber && index !== id && !excludedIds.includes(index)) {
            indices.push(index);
        }
        return indices;
    }, []);

    if (otherAnimeIndices.length ===   0) {
        console.log('No other anime found in the specified cluster.');
        return [];
    }

    const similarityResults = await Promise.all(otherAnimeIndices.map(async (otherIndex) => {
        const tensor = featureArray[id];
        const otherTensor = featureArray[otherIndex];
        try {
            const similarity = await compareTensors(tensor, otherTensor);
            return { index: otherIndex, similarity };
        } catch (error) {
            console.error('Error comparing tensors:', error);
            return null;
        }
    }));

    return similarityResults.filter(result => result !== null).sort((a, b) => b.similarity - a.similarity);
}


// dice, gower, jaccard, lorentzian, sorensen
function compareTensors(tensorA, tensorB) {
    return similarity.pearson(tensorA, tensorB);
}


main();

// add function to reccomend random 10 unique anime within cluster
// function for most 10 unique similar anime
// start working on ui (user enters up to 10 titles, auto complete
// add a list of future improvements 