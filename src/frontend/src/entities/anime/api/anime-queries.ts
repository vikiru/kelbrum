import { queryOptions } from '@tanstack/react-query';
import { z } from 'zod';

import { getAnimeChunkFilename, getAnimeChunkRange } from '@/entities/anime/api/chunk-ranges';
import {
  AnimeCardItemsSchema,
  AnimeCardMetadataChunkSchema,
  AnimeEntrySchema,
  type AnimeCardItem,
  type AnimeEntry,
} from '@/entities/anime/model/anime-schema';

const metadataChunkUrls = import.meta.glob<string>('/src/data/metadata-*.json', {
  query: '?url&no-inline',
  import: 'default',
  eager: true,
});
const metadataChunkUrlsByPath = new Map(Object.entries(metadataChunkUrls));

const fullAnimeEntryChunkUrls = import.meta.glob<string>('/src/data/full/full-*.json', {
  query: '?url&no-inline',
  import: 'default',
  eager: true,
});
const fullAnimeEntryChunkUrlsByPath = new Map(Object.entries(fullAnimeEntryChunkUrls));

const STATIC_QUERY_OPTIONS = {
  staleTime: Infinity,
  gcTime: Infinity,
  refetchOnWindowFocus: false,
} as const;

export const animeQueryKeys = {
  all: ['anime'] as const,
};

export function getAnimeMetadataQueryOptions(animeId: number) {
  const isValidAnimeId = Number.isInteger(animeId) && animeId > 0;
  const path = isValidAnimeId ? `/src/data/${getAnimeChunkFilename('metadata', getAnimeChunkRange(animeId))}` : null;

  return queryOptions<AnimeCardItem | null>({
    queryKey: [...animeQueryKeys.all, 'metadata', animeId] as const,
    queryFn: async () => {
      if (!path) return null;
      const chunk = await loadChunk(metadataChunkUrlsByPath, path);
      if (!chunk) return null;

      const parsed = AnimeCardMetadataChunkSchema.parse(chunk);

      const rawItem = parsed[String(animeId)];
      return rawItem === undefined ? null : AnimeCardItemsSchema.element.parse(rawItem);
    },
    ...STATIC_QUERY_OPTIONS,
    enabled: isValidAnimeId,
  });
}

export function getAnimeDetailsQueryOptions(animeId: number) {
  const isValidAnimeId = Number.isInteger(animeId) && animeId > 0;
  const path = isValidAnimeId
    ? `/src/data/full/${getAnimeChunkFilename('full', getAnimeChunkRange(animeId, 500))}`
    : null;

  return queryOptions<AnimeEntry | null>({
    queryKey: [...animeQueryKeys.all, 'entry', animeId] as const,
    queryFn: async () => {
      if (!path) return null;
      const chunk = await loadChunk(fullAnimeEntryChunkUrlsByPath, path);
      if (!chunk) return null;

      const parsedChunk = z.record(z.string(), AnimeEntrySchema).parse(chunk);

      const rawEntry = parsedChunk[String(animeId)];
      return rawEntry === undefined ? null : AnimeEntrySchema.parse(rawEntry);
    },
    ...STATIC_QUERY_OPTIONS,
    enabled: isValidAnimeId,
  });
}

export function getAnimeRecommendationsQueryOptions(animeId: number, limit = 5, entry?: AnimeEntry | null) {
  const isValidAnimeId = Number.isInteger(animeId) && animeId > 0;
  return queryOptions<AnimeCardItem[]>({
    queryKey: [...animeQueryKeys.all, 'recommendations', animeId, limit] as const,
    queryFn: async () => {
      if (!entry) return [];
      return loadAnimeRecommendationItems(entry.recommendations.slice(0, limit));
    },
    ...STATIC_QUERY_OPTIONS,
    enabled: isValidAnimeId && Boolean(entry),
  });
}

export async function loadAnimeRecommendationItems(ids: readonly number[]): Promise<AnimeCardItem[]> {
  if (ids.length === 0) return [];
  const paths = [...new Set(ids.map((id) => `/src/data/${getAnimeChunkFilename('metadata', getAnimeChunkRange(id))}`))];
  const chunks = await Promise.all(paths.map((path) => loadChunk(metadataChunkUrlsByPath, path)));
  const recordsByPath = new Map<string, Record<string, unknown>>();

  paths.forEach((path, index) => {
    const chunk = chunks[index];
    if (chunk) recordsByPath.set(path, z.record(z.string(), z.unknown()).parse(chunk));
  });

  return ids.flatMap((id) => {
    const path = `/src/data/${getAnimeChunkFilename('metadata', getAnimeChunkRange(id))}`;
    const record = recordsByPath.get(path);
    if (!record) return [];

    const parsedItem = AnimeCardItemsSchema.element.safeParse(record[String(id)]);
    return parsedItem.success ? [parsedItem.data] : [];
  });
}

export function getAnimeRecommendationBatchQueryKey(animeId: number, limit: number) {
  return [...animeQueryKeys.all, 'recommendation-batches', animeId, limit] as const;
}

const chunkCache = new Map<string, Promise<unknown>>();

async function loadChunk(urls: ReadonlyMap<string, string>, path: string): Promise<unknown> {
  const url = urls.get(path);
  if (!url) throw new Error(`Anime data asset is unavailable: ${path}`);

  let request = chunkCache.get(url);
  if (!request) {
    request = fetch(url)
      .then(async (response) => {
        if (!response.ok) throw new Error(`Failed to load anime data: ${response.status}`);
        return response.json();
      })
      .catch((error: unknown) => {
        chunkCache.delete(url);
        throw error;
      });
    chunkCache.set(url, request);
  }

  return request;
}
