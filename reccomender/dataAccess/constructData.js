const { cleanDuration, cleanPremiered, cleanRating } = require('../utils/clean');
const { handleMissingData } = require('../utils/fetchData');
const { filterAnimeData, writeData } = require('../utils/utils');
const { readAndProcessFile } = require('./readFile');

/**
 * Construct data file by reading input csv file and processing the data.
 *
 * @returns {Promise<Array>} The filtered and sorted anime data.
 */
async function constructDataFile() {
    console.log('Starting to construct data files by reading input csv file.');
    const animeCSV = await readAndProcessFile('../data/anime-dataset-2023.csv', 'AnimeEntry');
    let filteredData = filterAnimeData(animeCSV);
    filteredData = await handleMissingData(filteredData);
    filteredData.sort((a, b) => a.title.localeCompare(b.title));
    filteredData.forEach((entry, index) => {
        entry.id = index;
        entry.malID = parseInt(entry.malID, 10);
        entry.durationMinutes = cleanDuration(entry.durationText);
        entry.premiered = cleanPremiered(entry.premiered, entry.season, entry.year);
        entry.rating = cleanRating(entry.rating);
    });
    filteredData = filterAnimeData(filteredData);
    await writeData('entries.json', filteredData);
    return filteredData;
}
