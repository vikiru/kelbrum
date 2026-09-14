import { queryOptions } from '@tanstack/react-query';

import { AnimeCardItemSchema, AnimeSearchIndexSchema, type AnimeCardItem } from '@/entities/anime/model/anime-schema';

interface SearchMetadataRecord {
  score: number | null;
  title: string;
  titleEnglish?: string | null;
  titleJapanese?: string | null;
  images?: AnimeCardItem['images'];
  year: number | null;
  type: string | null;
  rating: string | null;
  episodes: number | null;
  genres: string[];
  themes: string[];
  demographics: string[];
}

const searchMetadataUrls = import.meta.glob<string>('/src/data/search/anime-metadata-search.json', {
  query: '?url&no-inline',
  import: 'default',
  eager: true,
});

const searchMetadataUrl = Object.values(searchMetadataUrls)[0];
let searchCataloguePromise: Promise<SearchCatalogueItem[]> | undefined;

export interface SearchCatalogueItem extends AnimeCardItem {
  type: string | null;
  rating: string | null;
  episodes: number | null;
  genres: string[];
  themes: string[];
  demographics: string[];
}

export interface SearchFilterOptions {
  genres: string[];
  themes: string[];
  demographics: string[];
}

export function loadSearchCatalogue(): Promise<SearchCatalogueItem[]> {
  searchCataloguePromise ??= fetchSearchMetadata().then((metadata) =>
    Object.values(metadata).map((rawItem) => {
      const item = AnimeCardItemSchema.parse({ ...rawItem, score: rawItem.score ?? 0 });
      return {
        ...item,
        type: rawItem.type,
        rating: rawItem.rating,
        episodes: rawItem.episodes,
        genres: rawItem.genres,
        themes: rawItem.themes,
        demographics: rawItem.demographics,
      };
    }),
  );
  return searchCataloguePromise;
}

export async function loadSearchFilterOptions(): Promise<SearchFilterOptions> {
  const metadata = await fetchSearchMetadata();
  return {
    genres: [...new Set(Object.values(metadata).flatMap((item) => item.genres))].toSorted(),
    themes: [...new Set(Object.values(metadata).flatMap((item) => item.themes))].toSorted(),
    demographics: [...new Set(Object.values(metadata).flatMap((item) => item.demographics))].toSorted(),
  };
}

let searchMetadataPromise: Promise<Record<string, SearchMetadataRecord>> | undefined;

export const searchQueryKeys = {
  all: ['search'] as const,
  catalogue: () => [...searchQueryKeys.all, 'catalogue'] as const,
  filterOptions: () => [...searchQueryKeys.all, 'filter-options'] as const,
};

export function getSearchCatalogueQueryOptions() {
  return queryOptions({
    queryKey: searchQueryKeys.catalogue(),
    queryFn: loadSearchCatalogue,
    staleTime: Infinity,
    gcTime: Infinity,
    refetchOnWindowFocus: false,
  });
}

export function getSearchFilterOptionsQueryOptions() {
  return queryOptions({
    queryKey: searchQueryKeys.filterOptions(),
    queryFn: loadSearchFilterOptions,
    staleTime: Infinity,
    gcTime: Infinity,
    refetchOnWindowFocus: false,
  });
}

function fetchSearchMetadata(): Promise<Record<string, SearchMetadataRecord>> {
  if (!searchMetadataPromise) {
    searchMetadataPromise = (async () => {
      if (!searchMetadataUrl) throw new Error('Search metadata asset URL is unavailable');
      const response = await fetch(searchMetadataUrl);
      if (!response.ok) throw new Error(`Failed to load search metadata: ${response.status}`);
      return AnimeSearchIndexSchema.parse(await response.json());
    })();
  }
  return searchMetadataPromise;
}
