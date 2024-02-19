const tf = require('@tensorflow/tfjs');
const { kmeans } = require('ml-kmeans');
const { initializeDataFile, returnUniqueArray, writeData, sortData } = require('./utils/utils');
const { createFeatureTensor, calculateFeatureVariance } = require('./utils/normalize');
const ss = require('simple-statistics');
const { similarity, distance } = require('ml-distance');

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

  async function returnOptimalK(featureArray, max) {
    const results = [];
    const fileName = 'manhattan.json';
    for (let k =  2; k <= max; k++) {
        try {
            const result = await kmeans(featureArray, k, {initialization: 'kmeans++', distanceFunction: distance.manhattan });
            const wcss = result.computeInformation(featureArray).reduce((sum, info) => sum + info.error,  0);
            const assignments = result.clusters;
            const silhouetteScore = ss.silhouetteMetric(featureArray, assignments);
            console.log(k, wcss, silhouetteScore);
            results.push({ k, wcss, silhouetteScore});
        } catch (error) {
            console.error(`Error computing KMeans for k=${k}:`, error);
            await writeData(fileName, results);
            throw error;
        }
    }

    const optimalK = results.reduce((prev, curr) => (curr.wcss < prev.wcss ? curr : prev)).k;
    const optimalS = results.reduce((prev, curr) => Math.abs(curr.silhouetteScore -  1) < Math.abs(prev.silhouetteScore -  1) ? curr : prev).silhouetteScore;

    console.log(`Optimal number of clusters: ${optimalK}`);
    console.log(`Greatest silhouette score: ${optimalS}`);

    results.optimalK = optimalK;
    await writeData(fileName, results);
    return { optimalK, optimalS };
}

// create custom distance function takes tensorA, tensorB
// use jaccard cosine and other measures together.


  // k = 12,14  24, 99, 100
 async function kmeansTrain(featureArray, data){
    let wcssValues = [];
    let sScores = [];
    const titles = new Set();
        const max = 100;
        for (let k = 2; k <= max; k++) {
            let result = kmeans(featureArray, k, {initialization: 'kmeans++', distanceFunction: distance.jaccard });
            let wcss = result.computeInformation(featureArray).reduce((sum, info) => sum + info.error,   0);
            wcssValues.push({ k, wcss });
            console.log(k, wcss);

            const assignments = result.clusters; 
            const silhouetteScore = ss.silhouetteMetric(featureArray, assignments);
            sScores.push(silhouetteScore);

            console.log(`Silhouette score: ${silhouetteScore}`);

            const clusteredAnime = assignments.map((clusterIndex, dataIndex) => {
                return {
                    anime: data[dataIndex], 
                    cluster: clusterIndex 
                };
            });

         const animeId =   25013; // 30276 - one punch man, 25013 - aka yona. // cowboy bebop, trigun, black lagoon. hellsing ultimate, drifters, vampire hunter d. nge serial experiments lain akira.
         const animeIndex = data.findIndex(anime => anime.malID === animeId);
         const animeCluster = assignments[animeIndex];
         console.log(`The anime with ID ${animeId} belongs to cluster ${animeCluster +   1}`);

         const topAnimeByCluster = assignments.reduce((acc, clusterIndex, dataIndex) => {
             if (!acc[clusterIndex]) {
                 acc[clusterIndex] = [];
             }
             acc[clusterIndex].push(data[dataIndex]);
             return acc;
         }, {});

         const topAnime = topAnimeByCluster[animeCluster];
         console.log(`Anime within ${animeCluster +   1}: ${topAnime.length}`);
         topAnime.forEach((anime, index) => {
           // console.log(`Anime ${index +   1}:`, anime.title);
             titles.add(anime.title);
         });
        }

        let optimalK = wcssValues.reduce((prev, curr) => (curr.wcss < prev.wcss ? curr : prev)).k;
        let optimalS = sScores.reduce((prev, curr) => (curr < prev ? curr : prev));
        console.log(`Optimal number of clusters: ${optimalK}`);
        console.log(`Optimal number of S: ${optimalS}`);
        await writeData('titles.json', Array.from(titles));
 }

async function main() {
    try {
        const data = await initializeDataFile();
        const featureTensor = await createFeatureTensor(data);
        const featureArray = featureTensor.arraySync();
        //console.log(featureArray);
        //const featureVariances = calculateFeatureVariance(featureArray);
        await returnOptimalK(featureArray, 100);
        //await kmeansTrain(featureArray, data);
    } catch (err) {
        console.error('Error occured:', err);
    }
}


main();


// revisit normalization, experiment with k and # of iterations
// save centroids and clusters, commit to repo, read it and reccomend based on that.

// try kmeans++, dbscan, knn, 


// TODO: revisit normalization try diff funcs, identify good # of clusters, use silhouette metric.
// once satisfied, commit to main.
// k 25 /31?

// IMAGEURL: cleanup https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png -> ''

// season, year, status, producers, licensors, studios, type, source, rating as one/multi-hot encode.
// rank, popularity as ordinal encode
// favourites, scoredBy, members min max or robust scale
// duration minutes either robust or multi-hot encode
// combine features with high covariance?


// experiment with custom distances using ml-distance

// TODO: go through each distance/similarity until k = 100 or as high as possible without error and save to file
// select best distance algorithm with highest silhouette and lowest wcss, use k value.
// cleanup, commit results to branch and update statistics file to save covariance and correlation of features (add handling to
// output which features are related and not based on values)
// experiment with predict and also see which anime are in which clusters
// store statistics and cluster distance functions results in data/statistics

//  cosine, pearson, hamming, mahalanobis, euclid, manhattan, chebyshev, minkowski (p = 1, p = 2)