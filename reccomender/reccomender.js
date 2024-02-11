const fs = require("fs");
const tf = require('@tensorflow/tfjs');
const { parse } = require("csv-parse");
const { AnimeEntry } = require("./AnimeEntry");


const entries = [];

const readAndParseCSV = () => {
  return new Promise((resolve, reject) => {
    fs.createReadStream("./data.csv")
      .pipe(parse({ delimiter: ",", from_line:  2 }))
      .on("data", function (row) {
         const id = row[0];
         const title = row[1];
         const rank = row[2];
         const type = row[3];
         const episodeCount = row[4];
         const aired = row[5];
         const members = row[6];
         const malURL = row[7];
         const imageURL = row[8];
         const score = row[9];
         const animeEntry = new AnimeEntry(id, title, rank, type, episodeCount, aired, members, malURL, imageURL, score);
         if (type === 'TV'){
            entries.push(animeEntry);
         }
      })
      .on("end", resolve)
      .on("error", reject);
  });
};

readAndParseCSV()
  .then(() => {
    console.log(entries.length);
  })
  .catch((error) => {
    console.error("Error reading and parsing CSV:", error);
  });



  // initially content based filtering, then allow for collaborative approach based on user input
  // normalize certain properties, one hot encode genres, etc..
  // overlap similarity, jaccard similarity, cosine similarity,
  // k means, cosine similarity, unsupervised learning, content, collaborative filter, hybrid, get missing data from JikanAPI.
  // missing data: trailer, english/japanese title, source?, aired (update to use timestamp), scoredBy, popularity, favorites, studios, season, year, genres, 