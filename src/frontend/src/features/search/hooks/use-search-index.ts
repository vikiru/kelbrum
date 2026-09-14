import { useQuery } from '@tanstack/react-query';

import { findAnimeIdsByQuery } from '@/features/search/search-client';

export function useSearchIndex(query: string) {
  const normalizedQuery = query.trim();
  const indexQuery = useQuery({
    queryKey: ['search', 'index', normalizedQuery],
    queryFn: () => findAnimeIdsByQuery(normalizedQuery),
    enabled: Boolean(normalizedQuery),
    staleTime: Infinity,
    gcTime: Infinity,
    refetchOnWindowFocus: false,
  });

  return {
    indexedIds: indexQuery.data ?? [],
    isSearching: Boolean(normalizedQuery) && indexQuery.isLoading,
    error: normalizedQuery
      ? indexQuery.error instanceof Error
        ? indexQuery.error
        : indexQuery.error
          ? new Error('Failed to search the catalogue')
          : null
      : null,
  };
}
