import type { Document } from 'flexsearch';

import { z } from 'zod';

import { normalizeSearchText, searchIndexOptions, type AnimeSearchHit } from '@/features/search/search-config';

let searchIndexPromise: Promise<Document<AnimeSearchHit>> | undefined;
const searchIndexUrls = import.meta.glob<string>('/src/data/search/flexsearch-index.json', {
  query: '?url&no-inline',
  import: 'default',
  eager: true,
});
const searchIndexUrl = Object.values(searchIndexUrls)[0];

export function loadSearchIndex(): Promise<Document<AnimeSearchHit>> {
  searchIndexPromise ??= Promise.all([import('flexsearch'), fetchSearchIndex()]).then(([{ Document }, searchIndex]) => {
    const client = new Document<AnimeSearchHit>(searchIndexOptions);
    for (const [key, data] of Object.entries(searchIndex.shards)) client.import(key, data);
    return client;
  });
  return searchIndexPromise;
}

async function fetchSearchIndex() {
  if (!searchIndexUrl) throw new Error('Search index asset URL is unavailable');
  const response = await fetch(searchIndexUrl);
  if (!response.ok) throw new Error(`Failed to load search index: ${response.status}`);
  return z.object({ shards: z.record(z.string(), z.string()) }).parse(await response.json());
}

export async function findAnimeIdsByQuery(query: string, limit: number): Promise<string[]> {
  const searchIndexClient = await loadSearchIndex();
  const normalizedQuery = normalizeSearchText(query);
  if (!normalizedQuery || limit <= 0) return [];
  return searchIndexClient.search(normalizedQuery, { limit }).flatMap((field) => field.result.map(String));
}
