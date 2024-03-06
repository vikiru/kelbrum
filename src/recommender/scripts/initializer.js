import { distance, similarity } from 'ml-distance';

import { returnKmeansModel, returnOptimalK } from '../dataAccess/train.js';
import { writeData } from '../dataAccess/writeFile.js';
import { weightedDistance } from '../recommender.js';
import { createFeatureTensor } from '../utils/normalize.js';
import { initializeDataFile } from '../utils/utils.js';

/**
 * Calculate various distance metrics between two feature tensors. This function is primarily used to test the
 * effectiveness of each distance measure
 *
 * @param {number} indexA - The index of the first feature tensor in the featureArray
 * @param {number} indexB - The index of the second feature tensor in the featureArray
 * @param {Array} featureArray - An array containing the feature tensors
 */
function testDistances(indexA, indexB, featureArray) {
    const tensorA = featureArray[indexA];
    const tensorB = featureArray[indexB];

    const gowerDistance = distance.gower(tensorA, tensorB);
    console.log(`Gower Distance: ${gowerDistance}`);

    const diceDistance = distance.dice(tensorA, tensorB);
    console.log(`Dice Distance: ${diceDistance}`);

    const jaccardDistance = distance.jaccard(tensorA, tensorB);
    console.log(`Jaccard Distance: ${jaccardDistance}`);

    const tanimotoDistance = distance.tanimoto(tensorA, tensorB);
    console.log(`Tanimoto Distance: ${tanimotoDistance}`);

    const czekanowskiDistance = distance.czekanowski(tensorA, tensorB);
    console.log(`Czekanowski Distance: ${czekanowskiDistance}`);

    const kulczynskiDistance = distance.kulczynski(tensorA, tensorB);
    console.log(`Kulczynski Distance: ${kulczynskiDistance}`);

    const ruzickaDistance = distance.ruzicka(tensorA, tensorB);
    console.log(`Ruzicka Distance: ${ruzickaDistance}`);

    const sorensenDistance = distance.sorensen(tensorA, tensorB);
    console.log(`Sorensen Distance: ${sorensenDistance}`);

    const matusitaDistance = distance.matusita(tensorA, tensorB);
    console.log(`Matusita Distance: ${matusitaDistance}`);

    const manhattanDistanceVal = distance.manhattan(tensorA, tensorB);
    console.log(`Manhattan Distance: ${manhattanDistanceVal}`);

    const euclideanDistanceVal = distance.euclidean(tensorA, tensorB);
    console.log(`Euclidean Distance: ${euclideanDistanceVal}`);

    const squaredEuclideanDistanceVal = distance.squaredEuclidean(tensorA, tensorB);
    console.log(`Squared Euclidean Distance: ${squaredEuclideanDistanceVal}`);

    const weightedDistanceVal = weightedDistance(tensorA, tensorB);
    console.log(`Weighted Distance: ${weightedDistanceVal}`);
}

async function main() {
    try {
        const data = await initializeDataFile();
        const featureTensor = await createFeatureTensor(data);
        console.log(featureTensor);
        const featureArray = featureTensor.arraySync();
        const titleIDMap = data.flatMap((d) => {
            const uniqueTitles = Array.from(new Set(d.titles));
            return { title: d.title, synonyms: uniqueTitles, value: d.id };
        });
        const kmeans = await returnKmeansModel(featureArray, 10, weightedDistance);
        await writeData('featureArray.json', featureArray);
        await writeData('titleIDMap.json', titleIDMap);
        await writeData('kmeans.json', kmeans);
    } catch (err) {
        console.error('Error occured:', err);
    }
}

main();
