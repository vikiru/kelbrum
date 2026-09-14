import { useQuery } from '@tanstack/react-query';

import type { AnimeEntry } from '@/entities/anime/model/anime-schema';

import { getAnimeRecommendationsQueryOptions } from '@/entities/anime/api/anime-queries';

export function useAnimeRecommendations(animeId: number, limit: number, entry: AnimeEntry | null | undefined) {
  const recommendationsQuery = useQuery({
    ...getAnimeRecommendationsQueryOptions(animeId, limit, entry),
    enabled: entry !== null && entry !== undefined,
  });

  return recommendationsQuery;
}
