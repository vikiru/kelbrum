/**
 * Returns an array of unique values from the specified property in the input data, excluding values present in the
 * filter array.
 *
 * @param {Array} data - The input data array containing objects with the specified property.
 * @param {string} property - The property name to extract values from.
 * @param {Array} [filter=[]] - The array of values to exclude from the result. Default is `[]`
 * @returns {Array} UniquePropertyValues - An array of unique values from the specified property.
 */
function returnUniqueArray(data, property, filter = []) {
    const allPropertyValues = data.flatMap((d) => d[property]).filter((value) => !filter.includes(value));
    const uniquePropertyValues = Array.from(new Set(allPropertyValues)).filter((a) => a !== '');
    return uniquePropertyValues;
}

/**
 * Filters anime data based on excluded types and genres.
 *
 * @param {array} data - The array of anime data to be filtered.
 * @returns {array} The filtered array of anime data.
 */
function filterAnimeData(data) {
    const excludedTypes = ['OVA', 'Special', 'Music', 'PV', 'TV Special'];
    const excludedGenres = ['Erotica', 'Hentai'];
    const filteredData = data.filter((d) => {
        return !excludedTypes.includes(d.type) && !d.genres.some((genre) => excludedGenres.includes(genre));
    });
    return filteredData;
}

/**
 * Returns filtered data based on unique values of a specified property.
 *
 * @param {Array} data - The input data array
 * @param {string} property - The property to filter by
 * @returns {Array} An array of objects with key-value pairs of unique values and their filtered data
 */
async function returnFilteredData(data, property) {
    const uniqueValues = returnUniqueArray(data, property);
    const result = uniqueValues.map((value) => {
        const filteredData = data.filter((d) => {
            if (Array.isArray(d[property])) {
                if (d[property].length === 0) {
                    return value === 'Unknown';
                }
                return d[property].includes(value);
            }
            return d[property] === value;
        });

        return {
            key: value,
            values: filteredData,
        };
    });

    return result;
}

export { returnFilteredData, filterAnimeData, returnUniqueArray };
