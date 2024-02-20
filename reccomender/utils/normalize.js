const { calculateStatistics, createMapping } = require('./stats');
const { sortData, returnUniqueArray } = require('./utils');
const tf = require('@tensorflow/tfjs');

function jaccardSimilarity(setA, setB) {
    const intersection = new Set([...setA].filter((x) => setB.has(x)));
    const union = new Set([...setA, ...setB]);
    return intersection.size / union.size;
}

function encodeCombination(data, property) {
    const uniqueValues = returnUniqueArray(data, property);
    const mapping = createMapping(uniqueValues);

    return data.map((entry) => {
        const propertyValues = entry[property];
        let combinationSum = 0;

        if (Array.isArray(propertyValues)) {
            propertyValues.forEach((value) => {
                const valueInt = mapping[value];
                if (valueInt !== undefined) {
                    combinationSum += valueInt;
                }
            });
        } else {
            const valueInt = mapping[propertyValues];
            if (valueInt !== undefined) {
                combinationSum = valueInt;
            }
        }

        return combinationSum;
    });
}

function encodeCategorical(data, property) {
    const uniqueValues = returnUniqueArray(data, property);
    return data.map((entry) => {
        const propertyValue = entry[property];
        const propertyString = propertyValue.toString();
        return uniqueValues.map((value) => {
            const valueString = value.toString();
            if (Array.isArray(propertyValue)) {
                return propertyValue.includes(value) ? 1 : 0;
            } else {
                return valueString === propertyString ? 1 : 0;
            }
        });
    });
}

function ordinalEncode(data, property) {
    const uniqueValues = sortData(returnUniqueArray(data, property, ['Unknown']));
    return data.map((entry) => {
        if (entry[property] === 0 || entry[property] === 'Unknown') {
            return -1;
        }
        return uniqueValues.indexOf(entry[property]);
    });
}

function minMaxScale(data, property) {
    const uniqueValues = returnUniqueArray(data, property, ['Unknown']);
    const minValue = Math.min(...uniqueValues);
    const maxValue = Math.max(...uniqueValues);
    const range = maxValue - minValue;

    return data.map((entry) => {
        if (entry[property] === 0 || entry[property] === 'Unknown') {
            return (minValue - minValue) / range;
        } else {
            return (entry[property] - minValue) / range;
        }
    });
}

function robustScale(data, property, stats) {
    const values = data.map((d) => d[property]);
    const valueStats = stats.find((s) => s.property === property);
    const median = valueStats.median;
    const iqr = valueStats.iqr;

    return values.map((value) => {
        if (value === 'Unknown') {
            return 0;
        } else {
            const roundedValue = Math.round(value);
            return (roundedValue - median) / iqr;
        }
    });
}

function multiHotEncode(data, property) {
    const uniqueValues = returnUniqueArray(data, property);
    return data.map((entry) => {
        return uniqueValues.map((value) => (entry[property].includes(value) ? 1 : 0));
    });
}

function checkArrayDimension(arr) {
    if (arr.some((item) => Array.isArray(item))) {
        return '2D';
    } else {
        return '1D';
    }
}

async function createFeatureTensor(data) {
    const stats = await calculateStatistics(data);
    const normalizationFunctions = [
        { func: encodeCategorical, isCategorical: true, property: 'type' },
        { func: encodeCategorical, isCategorical: true, property: 'source' },
        { func: encodeCategorical, isCategorical: true, property: 'status' },
        { func: encodeCategorical, isCategorical: true, property: 'rating' },
        { func: encodeCategorical, isCategorical: true, property: 'season' },
        { func: encodeCategorical, isCategorical: true, property: 'year' },
        { func: encodeCategorical, isCategorical: true, property: 'genres' },
        { func: encodeCategorical, isCategorical: true, property: 'demographics' },
        { func: encodeCategorical, isCategorical: true, property: 'themes' },
        { func: encodeCategorical, isCategorical: true, property: 'producers' },
        { func: encodeCategorical, isCategorical: true, property: 'studios' },
        { func: encodeCategorical, isCategorical: true, property: 'licensors' },

        { func: ordinalEncode, isCategorical: false, property: 'rank' },
        { func: ordinalEncode, isCategorical: false, property: 'popularity' },

        { func: robustScale, isCategorical: false, property: 'score' },
        { func: robustScale, isCategorical: false, property: 'scoredBy' },
        { func: robustScale, isCategorical: false, property: 'favourites' },
        { func: robustScale, isCategorical: false, property: 'members' },

        { func: minMaxScale, isCategorical: false, property: 'durationMinutes' },
        { func: minMaxScale, isCategorical: false, property: 'episodes' },
    ];

    const allTensors = normalizationFunctions.map(({ func, isCategorical, property }) => {
        let normalizedData;
        if (isCategorical) {
            normalizedData = func(data, property);
        } else {
            normalizedData = func(data, property, stats);
        }
        const dimension = checkArrayDimension(normalizedData);

        let tensor;
        if (dimension === '1D') {
            tensor = tf.tensor1d(normalizedData);
            tensor = tensor.expandDims(1);
        } else {
            tensor = tf.tensor2d(normalizedData);
        }
        return tensor;
    });

    validateTensors(allTensors);
    const concatenatedTensor = tf.concat(allTensors, 1);
    return concatenatedTensor;
}

function calculateFeatureVariance(data) {
    const length = 11925;
    const numFeatures = data[0].length;
    const featureVariances = Array(numFeatures).fill(0);
    const sums = Array(numFeatures).fill(0);
    const squaredSums = Array(numFeatures).fill(0);

    data.forEach((tensor) => {
        tensor.forEach((featureValue, index) => {
            sums[index] += featureValue;
            squaredSums[index] += Math.pow(featureValue, 2);
        });
    });

    const averages = sums.map((s) => s / length);
    const variances = squaredSums.map((squaredSum, index) => {
        const variance = squaredSum / length - Math.pow(averages[index], 2);
        return variance > 0 ? variance : 0;
    });
    return variances;
}

function validateTensors(tensors) {
    tensors.forEach((tensor, index) => {
        const hasNaN = tf.tidy(() => {
            return tf.logicalNot(tf.isNaN(tensor)).all().logicalNot();
        });

        if (hasNaN.dataSync()[0]) {
            console.error(`Tensor at index ${index} contains NaN values.`);
            console.error(tensor);
        }
    });
}

module.exports = {
    jaccardSimilarity,
    ordinalEncode,
    minMaxScale,
    robustScale,
    multiHotEncode,
    checkArrayDimension,
    createFeatureTensor,
    calculateFeatureVariance,
    validateTensors,
};
