const tf = require('@tensorflow/tfjs');
const { kmeans } = require('ml-kmeans');
const { initializeDataFile, returnUniqueArray, writeData } = require('./utils/utils');
const { createFeatureTensor, calculateFeatureVariance } = require('./utils/normalize');
const fs = require('fs');

function euclideanDistance(point1, point2) {
    if (point1.length !== point2.length) {
      throw new Error('Points must have the same number of dimensions');
    }
  
    let sum =  0;
    for (let i =  0; i < point1.length; i++) {
      sum += Math.pow(point1[i] - point2[i],  2);
    }
  
    return Math.sqrt(sum);
  }

async function main() {
    try {
        const data = await initializeDataFile();
        const featureTensor = createFeatureTensor(data);
        const featureArray = featureTensor.arraySync();
        const featureVariances = calculateFeatureVariance(featureArray);
        const titles = [];

        let wcssValues = [];
        const max = 200;
        for (let k =   99; k <= max; k++) {
            let result = kmeans(featureArray, k, {maxIterations:   10000});
            let wcss = result.computeInformation(featureArray).reduce((sum, info) => sum + info.error,   0);
            wcssValues.push({ k, wcss });
            console.log(k, wcss);

            const assignments = result.clusters; 

            const clusteredAnime = assignments.map((clusterIndex, dataIndex) => {
                return {
                    anime: data[dataIndex], 
                    cluster: clusterIndex 
                };
            });

         const animeId =   25013; // 30276 - one punch man, 25013 - aka yona.
         const animeIndex = data.findIndex(anime => anime.malID === animeId);
         const animeCluster = assignments[animeIndex];
        // console.log(`The anime with ID ${animeId} belongs to cluster ${animeCluster +   1}`);

         const topAnimeByCluster = assignments.reduce((acc, clusterIndex, dataIndex) => {
             if (!acc[clusterIndex]) {
                 acc[clusterIndex] = [];
             }
             acc[clusterIndex].push(data[dataIndex]);
             return acc;
         }, {});

         const topAnime = topAnimeByCluster[animeCluster];
         console.log(`Anime within ${animeCluster +   1}:`);
         topAnime.forEach((anime, index) => {
             console.log(`Anime ${index +   1}:`, anime.title);
             titles.push(anime.title);
         });
        }

        let optimalK = wcssValues.reduce((prev, curr) => (curr.wcss < prev.wcss ? curr : prev)).k;
        console.log(`Optimal number of clusters: ${optimalK}`);
        await writeData('titles.json', titles);

    } catch (err) {
        console.error('Error occured:', err);
    }
}


main();


// revisit normalization, experiment with k and # of iterations
// save centroids and clusters, commit to repo, read it and reccomend based on that.

// try kmeans++, dbscan, knn, 