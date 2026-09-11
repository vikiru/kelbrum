import { Document } from 'flexsearch';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const dataDirectory = resolve(scriptDirectory, '../src/data');
const searchMetadataPath = resolve(dataDirectory, 'search/anime-metadata-search.json');
const outputPath = resolve(dataDirectory, 'search/flexsearch-index.json');

const metadata = JSON.parse(await readFile(searchMetadataPath, 'utf8'));
const index = new Document({
  tokenize: 'forward',
  document: {
    id: 'id',
    index: ['text'],
    store: ['id', 'text'],
  },
});

for (const [id, item] of Object.entries(metadata)) {
  const text = [item.title, item.titleEnglish, item.titleJapanese, ...item.genres, ...item.themes, ...item.studios]
    .filter((value) => typeof value === 'string' && value.length > 0)
    .join(' ');
  index.add({ id, text });
}

const shards = {};
index.export((key, data) => {
  shards[key] = data;
});

const docs = Object.entries(metadata).map(([id, item]) => ({
  id,
  text: [item.title, item.titleEnglish, item.titleJapanese, ...item.genres, ...item.themes, ...item.studios]
    .filter((value) => typeof value === 'string' && value.length > 0)
    .join(' '),
}));

await writeFile(outputPath, `${JSON.stringify({ version: 1, docs, shards })}\n`);
console.info(`Built FlexSearch index for ${Object.keys(metadata).length} anime entries.`);
