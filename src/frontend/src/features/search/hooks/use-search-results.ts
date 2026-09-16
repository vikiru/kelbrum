import { useMemo } from 'react';

import type { AnimeCardItem } from '@/entities/anime/model/anime-schema';
import type { SearchFilters } from '@/features/search/hooks/use-search-filters';
import type { SearchCatalogueItem } from '@/features/search/model/search-catalogue';
import type { SearchSort } from '@/features/search/model/search-types';

import { getIndexedFilterIds, intersectIds } from '@/features/search/lib/search-filter-index';

interface SearchResultsOptions {
  catalogue: readonly SearchCatalogueItem[];
  indexedIds: readonly string[];
  query: string;
  filters: SearchFilters;
  sort: SearchSort;
}

export interface SearchResultSet {
  items: AnimeCardItem[];
  total: number;
}

export function useSearchResults(options: SearchResultsOptions): SearchResultSet {
  const { catalogue, indexedIds, query, filters, sort } = options;
  const catalogueById = useMemo(() => new Map(catalogue.map((item) => [item.malId, item])), [catalogue]);

  return useMemo(() => {
    const matchingIds = query.trim() ? new Set(indexedIds.map(Number)) : null;
    const filterIds = getIndexedFilterIds(
      filters.type,
      filters.rating,
      filters.demographic,
      filters.genres,
      filters.themes,
      filters.scoreRange,
      filters.yearRange,
      filters.episodeRange,
    );
    const candidateIds = matchingIds ? intersectIds(filterIds, matchingIds) : filterIds;
    const minYear = Number(filters.yearRange[0]) || 0;
    const maxYear = Number(filters.yearRange[1]) || Number.POSITIVE_INFINITY;
    const minEpisodes = Number(filters.episodeRange[0]) || 0;
    const maxEpisodes = Number(filters.episodeRange[1]) || Number.POSITIVE_INFINITY;

    const results = [...candidateIds]
      .map((id) => catalogueById.get(id))
      .filter((item): item is SearchCatalogueItem => item !== undefined)
      .filter(
        (item) =>
          (filters.type === 'all' || item.type === filters.type) &&
          (filters.rating === 'all' || item.rating === filters.rating) &&
          (filters.demographic === 'all' || item.demographics.includes(filters.demographic)) &&
          filters.genres.every((value) => item.genres.includes(value)) &&
          filters.themes.every((value) => item.themes.includes(value)) &&
          (item.score ?? 0) >= filters.scoreRange[0] &&
          (item.score ?? 0) <= filters.scoreRange[1] &&
          (item.year ?? 0) >= minYear &&
          (item.year ?? 0) <= maxYear &&
          (item.episodes ?? 0) >= minEpisodes &&
          (item.episodes ?? 0) <= maxEpisodes,
      )
      .toSorted((a, b) => compareAnime(a, b, sort));

    return { items: results, total: results.length };
  }, [catalogueById, filters, indexedIds, query, sort]);
}

function compareAnime(a: AnimeCardItem, b: AnimeCardItem, sort: SearchSort): number {
  const direction = sort.endsWith('asc') ? 1 : -1;
  if (sort.startsWith('title')) return direction * a.title.localeCompare(b.title);
  if (sort.startsWith('year')) return direction * ((a.year ?? 0) - (b.year ?? 0));
  return direction * ((a.score ?? 0) - (b.score ?? 0));
}
