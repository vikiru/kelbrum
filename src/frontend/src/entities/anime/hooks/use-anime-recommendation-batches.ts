import { useInfiniteQuery } from '@tanstack/react-query';

import type { AnimeEntry } from '@/entities/anime/model/anime-schema';

import { getAnimeRecommendationBatchQueryKey, loadAnimeRecommendationItems } from '@/entities/anime/api/anime-queries';

export const ANIME_RECOMMENDATION_BATCH_SIZE = 25;

export function useAnimeRecommendationBatches(animeId: number, entry: AnimeEntry | null | undefined) {
  return useInfiniteQuery({
    queryKey: getAnimeRecommendationBatchQueryKey(animeId, ANIME_RECOMMENDATION_BATCH_SIZE),
    initialPageParam: 0,
    queryFn: ({ pageParam }) => {
      const ids = entry?.recommendations.slice(pageParam, pageParam + ANIME_RECOMMENDATION_BATCH_SIZE) ?? [];
      return loadAnimeRecommendationItems(ids);
    },
    getNextPageParam: (_lastPage, _pages, lastPageParam) => {
      const nextOffset = lastPageParam + ANIME_RECOMMENDATION_BATCH_SIZE;
      return entry && nextOffset < entry.recommendations.length ? nextOffset : undefined;
    },
    staleTime: Infinity,
    gcTime: Infinity,
    refetchOnWindowFocus: false,
    enabled: Number.isInteger(animeId) && animeId > 0 && Boolean(entry),
  });
}
