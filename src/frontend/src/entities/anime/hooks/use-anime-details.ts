import { useQuery } from '@tanstack/react-query';

import { getAnimeDetailsQueryOptions } from '@/entities/anime/api/anime-queries';

export function useAnimeDetails(animeId: number) {
  return useQuery(getAnimeDetailsQueryOptions(animeId));
}
