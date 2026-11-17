import { useInfiniteQuery } from '@tanstack/react-query';

import type { AnimeEntry } from '@/entities/anime/model/anime-schema';

import { getAnimeRecommendationBatchesQueryOptions } from '@/entities/anime/api/anime-queries';

export function useAnimeRecommendationBatches(animeId: number, entry: AnimeEntry | null | undefined) {
  return useInfiniteQuery(getAnimeRecommendationBatchesQueryOptions(animeId, entry));
}
