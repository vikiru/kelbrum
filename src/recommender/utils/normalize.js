import * as tf from '@tensorflow/tfjs';

import { writeData } from '../dataAccess/writeFile.js';
import { returnUniqueArray } from './filter.js';
import { constructTFIDF, normalizeSynopsis } from './handleSynopsis.js';
import { calculateStatistics, createMapping } from './stats.js';
import { sortData } from './utils.js';

const typeMapping = {
    TV: 1,
    ONA: 2,
    Movie: 3,
    Unknown: 4,
};

const ratingMapping = {
    G: 1,
    PG: 2,
    'PG-13': 3,
    R: 4,
    'R+': 5,
    Unknown: 6,
};

const demographicMapping = {
    Kids: 1,
    Shoujo: 2,
    Josei: 2.5,
    Shounen: 3,
    Seinen: 3.5,
    Unknown: 5,
};

function normalizeMapping(data, property) {
    const mapping = {
        type: typeMapping,
        rating: ratingMapping,
        demographics: demographicMapping,
    };
    const map = mapping[property];
    return data.map((entry) => {
        const value = entry[property];
        if (Array.isArray(value) && value.length === 0) {
            return map['Unknown'];
        } else {
            if (Array.isArray(value) && value.length > 1) {
                const mappedValues = value.map((val) => map[val]);
                return Math.min(...mappedValues);
            } else {
                return map[value];
            }
        }
    });
}

/**
 * Encodes the combination of data based on the given property using a unique value mapping.
 *
 * @param {Array} data - The input data array
 * @param {string} property - The property to encode the combination on
 * @returns {Array} The encoded combination array
 */
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

/**
 * Encodes categorical data based on unique property values.
 *
 * @param {Array} data - The input data array
 * @param {string} property - The property to encode
 * @returns {Array} The encoded data array
 */
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

/**
 * Encodes the given property in the data array as ordinal values.
 *
 * @param {Array} data - The input data array
 * @param {string} property - The property to be encoded
 * @returns {Array} The encoded array
 */
function ordinalEncode(data, property) {
    const uniqueValues = sortData(returnUniqueArray(data, property));
    return data.map((entry) => {
        if (entry[property] === 0 || entry[property] === 'Unknown') {
            return -1;
        }
        return uniqueValues.indexOf(entry[property]);
    });
}

/**
 * Scales the given data based on the specified property to a range of [0, 1].
 *
 * @param {Array} data - The input data array
 * @param {string} property - The property to be used for scaling
 * @returns {Array} The scaled data array
 */
function minMaxScale(data, property) {
    const uniqueValues = returnUniqueArray(data, property, ['Unknown']);
    const minValue = Math.min(...uniqueValues);
    const maxValue = Math.max(...uniqueValues);
    const range = maxValue - minValue;

    return data.map((entry) => {
        if (entry[property] === 0 || entry[property] === 'Unknown') {
            return 0;
        } else {
            return (entry[property] - minValue) / range;
        }
    });
}

/**
 * Scales the given data based on the specified property using robust scaling.
 *
 * @param {Array} data - The input data array
 * @param {string} property - The property to be used for scaling
 * @param {Array} stats - The statistical information for the property
 * @returns {Array} The scaled values based on robust scaling
 */
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

/**
 * Normalizes categorical data to a range between 0 and 1.
 *
 * @param {Array} data - The array of categorical data to be normalized
 * @returns {Array} - The normalized data array
 */
function normalizeCategorical(data) {
    const uniqueValues = Array.from(new Set(data.map((d) => d)));
    const minValue = Math.min(...uniqueValues);
    const maxValue = Math.max(...uniqueValues);
    const range = maxValue - minValue;
    return data.map((entry) => {
        if (entry === 0 || entry === 'Unknown') {
            return (minValue - minValue) / range;
        } else {
            return (entry - minValue) / range;
        }
    });
}

/**
 * Multi-hot encodes the data based on the specified property.
 *
 * @param {Array} data - The input data array.
 * @param {string} property - The property to perform encoding on.
 * @returns {Array} - The multi-hot encoded array.
 */
function multiHotEncode(data, property) {
    const uniqueValues = returnUniqueArray(data, property);
    return data.map((entry) => {
        return uniqueValues.map((value) => (entry[property].includes(value) ? 1 : 0));
    });
}

/**
 * Asynchronously creates a feature tensor based on the given data.
 *
 * @param {array} data - The input data to create the feature tensor
 * @returns {Tensor} The concatenated feature tensor
 */
async function createFeatureTensor(data) {
    const stats = await calculateStatistics(data);
    const synopsisData = await normalizeSynopsis(data);
    const normalizationFunctions = [
        { func: normalizeMapping, isCategorical: true, property: 'type', is1D: true },
        { func: multiHotEncode, isCategorical: true, property: 'source', is1D: false },
        { func: normalizeMapping, isCategorical: true, property: 'rating', is1D: true },
        { func: multiHotEncode, isCategorical: true, property: 'genres', is1D: false },
        { func: normalizeMapping, isCategorical: true, property: 'demographics', is1D: true },
        { func: multiHotEncode, isCategorical: true, property: 'themes', is1D: false },
        { func: normalizeSynopsis, isCategorical: true, property: 'synopsis', is1D: false },
        { func: minMaxScale, isCategorical: false, property: 'durationMinutes', is1D: true },
        { func: minMaxScale, isCategorical: false, property: 'score', is1D: true },
        { func: minMaxScale, isCategorical: false, property: 'year', is1D: true },
        //{ func: multiHotEncode, isCategorical: true, property: 'studios', is1D: false },
        //{ func: minMaxScale, isCategorical: false, property: 'episodes', is1D: true },
    ];

    const allTensors = normalizationFunctions.map(({ func, isCategorical, is1D, property }) => {
        let normalizedData;
        if (isCategorical) {
            normalizedData = func(data, property);
            if (func === normalizeSynopsis) normalizedData = synopsisData;
        } else {
            normalizedData = func(data, property, stats);
        }

        let tensor;
        if (is1D) {
            tensor = tf.tensor1d(normalizedData);
            tensor = tensor.expandDims(1);
        } else {
            tensor = tf.tensor2d(normalizedData);
        }
        return tensor;
    });

    validateTensors(allTensors);
    const concatenatedTensor = tf.concat2d(allTensors, 1);
    return concatenatedTensor;
}

/**
 * Calculate the variance of each feature in the given data.
 *
 * @param {number[][]} data - The input data containing features
 * @returns {number[]} An array containing the variance of each feature
 */
function calculateFeatureVariance(data) {
    const length = data.length;
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

/**
 * Validates an array of tensors for NaN values and logs an error if NaN values are found.
 *
 * @param {Array} tensors - The array of tensors to be validated
 * @returns {void}
 */
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

export {
    minMaxScale,
    encodeCombination,
    ordinalEncode,
    robustScale,
    encodeCategorical,
    normalizeCategorical,
    createFeatureTensor,
    calculateFeatureVariance,
    validateTensors,
};
