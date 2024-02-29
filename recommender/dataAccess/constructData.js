import { writeData } from '../dataAccess/writeFile';
import { cleanDuration, cleanPremiered, cleanRating } from '../utils/clean';
import { handleMissingData } from '../utils/fetchData';
import { filterAnimeData } from '../utils/filter';
import { readAndProcessFile } from './readFile';

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

export { constructDataFile };
