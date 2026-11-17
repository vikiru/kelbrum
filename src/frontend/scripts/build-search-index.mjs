import { Document } from 'flexsearch';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const dataDirectory = resolve(scriptDirectory, '../src/data');
const searchMetadataPath = resolve(dataDirectory, 'search/anime-metadata-search.json');
const outputPath = resolve(dataDirectory, 'search/flexsearch-index.json');

function normalizeSearchText(value) {
  return value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}

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
    .map(normalizeSearchText)
    .join(' ');
  index.add({ id, text });
}

const shards = {};
index.export((key, data) => {
  shards[key] = data;
});

await writeFile(outputPath, `${JSON.stringify({ version: 1, shards })}\n`);
console.info(`Built FlexSearch index for ${Object.keys(metadata).length} anime entries.`);
