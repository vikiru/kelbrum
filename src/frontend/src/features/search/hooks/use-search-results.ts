import { useMemo } from 'react';

import type { AnimeCardItem } from '@/entities/anime/model/anime-schema';
import type { SearchFilters } from '@/features/search/hooks/use-search-filters';
import type { SearchCatalogueItem } from '@/features/search/model/search-catalogue';
import type { SearchSort } from '@/features/search/model/search-types';

import {
  getIndexedFilterIds,
  intersectIds,
  matchesNumericRange,
  resolveNumericFilterRanges,
} from '@/features/search/lib/search-filter-index';

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
    const [scoreFilter, yearFilter, episodesFilter] = resolveNumericFilterRanges(
      filters.scoreRange,
      filters.yearRange,
      filters.episodeRange,
    );

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
          matchesNumericRange(item.score, scoreFilter.minimum, scoreFilter.maximum, scoreFilter.enabled) &&
          matchesNumericRange(item.year, yearFilter.minimum, yearFilter.maximum, yearFilter.enabled) &&
          matchesNumericRange(item.episodes, episodesFilter.minimum, episodesFilter.maximum, episodesFilter.enabled),
      )
      .toSorted((a, b) => compareAnime(a, b, sort));

    return { items: results, total: results.length };
  }, [catalogueById, filters, indexedIds, query, sort]);
}

function compareAnime(a: AnimeCardItem, b: AnimeCardItem, sort: SearchSort): number {
  const direction = sort.endsWith('asc') ? 1 : -1;
  if (sort.startsWith('title')) return direction * a.title.localeCompare(b.title);
  if (sort.startsWith('year')) return compareNullableNumber(a.year, b.year, direction);
  return compareNullableNumber(a.score, b.score, direction);
}

function compareNullableNumber(a: number | null, b: number | null, direction: 1 | -1): number {
  if (a === null && b === null) return 0;
  if (a === null) return 1;
  if (b === null) return -1;
  return direction * (a - b);
}
