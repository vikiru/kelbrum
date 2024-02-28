import * as ss from 'simple-statistics';

import { returnUniqueArray } from './utils.js';

/**
 * Create a mapping of unique values to integers, starting from 0.
 *
 * @param {Array} uniqueValues - The array of unique values
 * @returns {Object} The mapping of unique values to integers
 */
function createMapping(uniqueValues) {
    const unknownCheck = uniqueValues.filter((v) => v === 'Unknown').length;
    const filteredValues = uniqueValues.filter((v) => v !== 'Unknown');
    const mapping = {};
    let nextInt = 0;
    if (unknownCheck > 0) {
        mapping['Unknown'] = nextInt;
        nextInt++;
    }
    filteredValues.forEach((val) => {
        if (!Object.prototype.hasOwnProperty.call(mapping, val)) {
            mapping[val] = nextInt++;
        }
    });
    return mapping;
}

/**
 * Fills an array based on the given data, mapping, and key.
 *
 * @param {Array} data - The input data array
 * @param {Object} mapping - The mapping object
 * @param {string} key - The key to access the value in each data entry
 * @returns {Array} An array filled based on the mapping and key
 */
function fillArray(data, mapping, key) {
    const array = [];
    data.forEach((entry) => {
        let value = entry[key];
        if (Array.isArray(value)) {
            const valueSum = value.reduce((acc, v) => acc + mapping[v], 0);
            array.push({ value: valueSum, originalValues: value });
        } else if (typeof value === 'string') {
            array.push({ value: mapping[value], originalValues: [value] });
        } else if (typeof value === 'number') {
            array.push({ value: Math.round(value), originalValues: [value] });
        }
    });
    return array;
}

/**
 * Calculate the median and mode of the given values.
 *
 * @param {Array} values - The array of values to calculate median and mode.
 * @param {boolean} isCategorical - Indicates if the values are categorical or not.
 * @returns {Object} An object containing the median and mode values.
 */
function returnMedianMode(values, isCategorical) {
    let median, mode;

    if (isCategorical) {
        const medianValue = ss.median(values.map((v) => v.value));
        const modeValue = ss.mode(values.map((v) => v.value));

        median = {
            median: medianValue,
            value: values.find((v) => v.value === medianValue)?.originalValues || 'Not found',
        };

        mode = {
            mode: modeValue,
            value: Array.isArray(modeValue)
                ? modeValue.map((value) => values.find((v) => v.value === value)?.originalValues || 'Not found')
                : [values.find((v) => v.value === modeValue)?.originalValues || 'Not found'],
        };
    } else {
        median = ss.median(values.map((v) => v.value));
        mode = ss.mode(values.map((v) => v.value));
    }

    return { median, mode };
}

/**
 * Constructs a frequency map based on the data and mapping provided, using the specified key.
 *
 * @param {Array} data - The data to be used for constructing the frequency map.
 * @param {Object} mapping - The mapping object that maps values to their corresponding keys.
 * @param {string} key - The key to be used for constructing the frequency map.
 * @returns {Array} An array containing objects with the value and its occurrences, along with the count of invalid
 *   values.
 */
function constructFrequencyMap(data, mapping, key) {
    const valuesArray = fillArray(data, mapping, key);
    const frequencyMap = [];
    let invalidCount = 0;

    const valueCounts = valuesArray.reduce((counts, value) => {
        counts[value] = (counts[value] || 0) + 1;
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

/**
 * Asynchronously calculates various statistical properties for the given data.
 *
 * @param {Array} data - The input data array to calculate statistics for.
 * @returns {Array} An array of objects containing statistical properties for each key in the input data.
 */
async function calculateStatistics(data) {
    try {
        const firstElement = data[0];
        const excludedKeys = [
            'id',
            'malID',
            'title',
            'englishName',
            'otherName',
            'imageURL',
            'pageURL',
            'aired',
            'premiered',
            'synopsis',
            'durationText',
        ];
        const keys = Object.keys(firstElement).filter((key) => !excludedKeys.includes(key));
        const valuesMap = [];

        const propertyMap = keys.map((key) => {
            const isCategorical = Array.isArray(firstElement[key]) || typeof firstElement[key] === 'string';
            const uniqueValues = returnUniqueArray(data, key);
            const mapping = createMapping(uniqueValues);
            const frequencyMap = constructFrequencyMap(data, mapping, key);
            const values = fillArray(data, mapping, key);

            const processedValues = values.map((valueObj) => valueObj.value);
            if (values.length === 0) {
                throw new Error(`No values found for property ${key}`);
            }

            const mean = ss.mean(processedValues);
            const { median, mode } = returnMedianMode(values, isCategorical);
            const variance = ss.variance(processedValues);
            const standardDeviation = ss.standardDeviation(processedValues);
            const min = ss.min(processedValues);
            const max = ss.max(processedValues);
            const q1 = ss.quantile(processedValues, 0.25);
            const q3 = ss.quantile(processedValues, 0.75);
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

        propertyMap.forEach((prop) => {
            const values = valuesMap[prop.property];
            const filteredProps = propertyMap.filter((otherProp) => otherProp.property !== prop.property);
            prop.covariance = [];
            prop.correlation = [];

            filteredProps.forEach((p) => {
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
        return propertyMap;
    } catch (error) {
        console.error('Error in calculateStatistics:', error);
        throw error;
    }
}

export { createMapping, fillArray, returnMedianMode, constructFrequencyMap, calculateStatistics };
