import { useQuery } from '@tanstack/react-query';

import { findAnimeIdsByQuery } from '@/features/search/search-client';
import { normalizeSearchText } from '@/features/search/search-config';

export function useSearchIndex(query: string, limit: number) {
  const normalizedQuery = normalizeSearchText(query);
  const indexQuery = useQuery({
    queryKey: ['search', 'index', normalizedQuery, limit],
    queryFn: () => findAnimeIdsByQuery(normalizedQuery, limit),
    enabled: Boolean(normalizedQuery) && limit > 0,
    placeholderData: (previousData) => previousData,
    staleTime: Infinity,
    gcTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  return {
    indexedIds: indexQuery.data ?? [],
    isSearching: Boolean(normalizedQuery) && indexQuery.isFetching,
    error: normalizedQuery
      ? indexQuery.error instanceof Error
        ? indexQuery.error
        : indexQuery.error
          ? new Error('Failed to search the catalogue')
          : null
      : null,
  };
}
