const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));


async function fetchData(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  }
  
  function delay() {
    return new Promise((resolve) => {
        setTimeout(resolve, 1000);
    });
  }
  
  async function fetchMissingData(data){
    const length = data.length;
    const baseQuery = 'https://api.jikan.moe/v4/anime?q='
    for (const entry of data){
      if (!("japaneseTitle" in entry)){
        const index = data.indexOf(entry) + 1;
        console.log(`Retrieving missing data for entry (${index} / ${length})`);
        const title = entry.title;
        const url = baseQuery + `${title}&limit=1`;
        const result = await fetchData(url);
        const resultData = result.data[0];
        entry.malID = resultData.mal_id;
        entry.trailer = resultData.trailer.url || '';
        entry.englishTitle = resultData.title_english || '';
        entry.japaneseTitle = resultData.title_japanese || '';
        entry.synonyms = resultData.title_synonyms || [];
        entry.source = resultData.source || '';
        entry.airedFrom = resultData.aired.from || '';
        entry.airedTo = resultData.aired.to || '';
        entry.scoredBy = resultData.scored_by || '';
        entry.popularity = resultData.popularity || '0';
        entry.favourites = resultData.favorites || '';
        entry.synopsis = resultData.synopsis || '';
        entry.season = resultData.season || '';
        entry.year = resultData.year || '';
        entry.producers = resultData.producers.map(producer => producer.name) || [];
        entry.studios = resultData.studios.map(studio => studio.name) || [];
        const explicit_genres = resultData.explicit_genres.map(genre => genre.name) ||  [];
        const genres = resultData.genres.map(genre => genre.name) || [];
        const demographics = resultData.demographics.map(demographic => demographic.name) || [];
        const themes = resultData.themes.map(theme => theme.name) || [];
        entry.genres = [...explicit_genres, ...genres, ...demographics, ...themes];
        await delay();
        await writeFile('updatedEntries.json', data);
      }
    }
  }