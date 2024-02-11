const fs = require("fs");
const { parse } = require("csv-parse");
const { AnimeEntry } = require("./AnimeEntry");
const entries = [];

fs.createReadStream("./data.csv")
  .pipe(parse({ delimiter: ",", from_line: 2 }))
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
     entries.push(animeEntry);
  })
  .on("end", function () {
    console.log(entries.length);  })
  .on("error", function (error) {
    console.log(error.message);
  });

