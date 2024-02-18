const tf = require('@tensorflow/tfjs');
const { kmeans } = require('ml-kmeans');
const { initializeDataFile, returnUniqueArray, writeData, sortData } = require('./utils/utils');
const { createFeatureTensor, calculateFeatureVariance } = require('./utils/normalize');
const fs = require('fs');
const ss = require('simple-statistics');

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

  function createMapping(uniqueValues){
    const unknownCheck = uniqueValues.filter(v => v === 'Unknown').length;
    const filteredValues = uniqueValues.filter(v => v !== 'Unknown');
    const mapping = {};
    let nextInt = 0;
    if (unknownCheck > 0){
        mapping['Unknown'] = nextInt;
        nextInt++;
    }
    filteredValues.forEach(val => {
        if (!Object.prototype.hasOwnProperty.call(mapping, val)) {
            mapping[val] = nextInt++;
          }
        });
    return mapping;
  }

  function fillArray(data, mapping, key) {
    const array = [];
    data.forEach(entry => {
      let value = entry[key];
      if (Array.isArray(value)) {
        const valueSum = value.reduce((acc, v) => acc + mapping[v],   0);
        array.push({ value: valueSum, originalValues: value });
      } else if (typeof value === 'string') {
        array.push({ value: mapping[value], originalValues: [value] });
      } else if (typeof value === 'number') {
        array.push({ value: Math.round(value), originalValues: [value] });
      }
    });
    return array;
  }

  function returnMedianMode(values, mapping, isCategorical) {
    let median, mode;
  
    if (isCategorical) {
      const medianValue = ss.median(values.map(v => v.value));
      const modeValue = ss.mode(values.map(v => v.value));
  
      median = {
        median: medianValue,
        value: values.find(v => v.value === medianValue)?.originalValues || 'Not found'
      };
  
      mode = {
        mode: modeValue,
        value: Array.isArray(modeValue)
          ? modeValue.map(value => values.find(v => v.value === value)?.originalValues || 'Not found')
          : [values.find(v => v.value === modeValue)?.originalValues || 'Not found']
      };
  
      console.log(median, mode);
    } else {
      median = ss.median(values.map(v => v.value));
      mode = ss.mode(values.map(v => v.value));
    }
  
    return { median, mode };
  }

  function constructFrequencyMap(data, mapping, key) {
    const valuesArray = fillArray(data, mapping, key);
    const frequencyMap = [];
    let invalidCount =  0;
  
    const valueCounts = valuesArray.reduce((counts, value) => {
      counts[value] = (counts[value] ||  0) +  1;
      return counts;
    }, {});
  
    Object.entries(valueCounts).forEach(([value, occurences]) => {
      if (value === mapping['Unknown'] || value === mapping[0]) {
        invalidCount += occurences;
      }
      frequencyMap.push({
        value,
        occurences,
      });
    });
  
    frequencyMap.invalidCount = invalidCount;
    return frequencyMap;
  }

  async function calculateStatistics(data) {
    try {
      const firstElement = data[0];
      const excludedKeys = ['id', 'malID', 'title', 'englishName', 'otherName', 'imageURL', 'pageURL', 'aired', 'premiered', 'synopsis', 'durationText'];
      const keys = Object.keys(firstElement).filter(key => !excludedKeys.includes(key));
      const valuesMap = [];
  
      const propertyMap = keys.map(key => {
        const isCategorical = Array.isArray(firstElement[key]) || typeof firstElement[key] === 'string';
        const uniqueValues = returnUniqueArray(data, key);
        const mapping = createMapping(uniqueValues);
        const frequencyMap = constructFrequencyMap(data, mapping, key);
        const values = fillArray(data, mapping, key);
  
        const processedValues = values.map(valueObj => valueObj.value);
        if (values.length ===   0) {
          throw new Error(`No values found for property ${key}`);
        }
  
        const mean = ss.mean(processedValues);
        const {median, mode} = returnMedianMode(values, processedValues, mapping, isCategorical);
        const variance = ss.variance(processedValues);
        const standardDeviation = ss.standardDeviation(processedValues);
        const min = ss.min(processedValues);
        const max = ss.max(processedValues);
        const q1 = ss.quantile(processedValues,   0.25);
        const q3 = ss.quantile(processedValues,   0.75);
        const iqr = ss.iqr(processedValues);
        const invalidCount = frequencyMap.invalidCount;
        const skewness = ss.sampleSkewness(processedValues);
        const kurtosis = ss.sampleKurtosis(processedValues);
        valuesMap[key] = processedValues;

        return {
          property: key,
          mean,
          median,
          mode,
          variance,
          standardDeviation,
          min,
          max,
          q1,
          q3,
          iqr,
          skewness,
          kurtosis,
          invalidCount,
        };
      });
  
      propertyMap.forEach(prop => {
        const values = valuesMap[prop.property];
        const filteredProps = propertyMap.filter(otherProp => otherProp.property !== prop.property);
        prop.covariance = [];
        prop.correlation = [];
  
        filteredProps.forEach(p => {
          const otherValues = valuesMap[p.property];
          const covariance = ss.sampleCovariance(values, otherValues);
          const correlation = ss.sampleCorrelation(values, otherValues);
          prop.covariance.push({
            comparedProperty: p.property,
            covariance,
          });
          prop.correlation.push({
            comparedProperty: p.property,
            correlation,
          });
        });
      });
  
      await writeData('statistics.json', propertyMap);
      return propertyMap;
    } catch (error) {
      console.error('Error in calculateStatistics:', error);
      throw error;
    }
  }

 async function kmeansTrain(featureArray, data){
    let wcssValues = [];
    const titles = [];
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

         const animeId =   25013; // 30276 - one punch man, 25013 - aka yona. // cowboy bebop, trigun, black lagoon. hellsing ultimate, drifters, vampire hunter d. nge serial experiments lain akira.
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
 }

async function main() {
    try {
        const data = await initializeDataFile();
        //const featureTensor = createFeatureTensor(data);
        //const featureArray = featureTensor.arraySync();
        //const featureVariances = calculateFeatureVariance(featureArray);
        await calculateStatistics(data);
    } catch (err) {
        console.error('Error occured:', err);
    }
}


main();


// revisit normalization, experiment with k and # of iterations
// save centroids and clusters, commit to repo, read it and reccomend based on that.

// try kmeans++, dbscan, knn, 