import { useCallback, useEffect, useState } from 'react';

import type { AnimeEntry } from '@/entities/anime/model/anime-schema';

import { useAnimeRecommendationBatches } from '@/entities/anime/hooks/use-anime-recommendation-batches';

export function useRecommendations(animeId: number, entry: AnimeEntry | null | undefined) {
  const recommendationsQuery = useAnimeRecommendationBatches(animeId, entry);
  const [loadMoreElement, updateLoadMoreElement] = useState<HTMLDivElement | null>(null);
  const setLoadMoreElement = useCallback((element: HTMLDivElement | null) => {
    updateLoadMoreElement(element);
  }, []);
  const hasNextPage = Boolean(recommendationsQuery.hasNextPage);
  const isFetchingNextPage = Boolean(recommendationsQuery.isFetchingNextPage);
  const isFetchNextPageError = Boolean(recommendationsQuery.isFetchNextPageError);
  const fetchNextPage = recommendationsQuery.fetchNextPage;

  useEffect(() => {
    if (!loadMoreElement || !hasNextPage || isFetchingNextPage || isFetchNextPageError) return;

    const observer = new IntersectionObserver(
      ([intersection]) => {
        if (intersection?.isIntersecting) void fetchNextPage();
      },
      { rootMargin: '0px 0px 640px' },
    );
    observer.observe(loadMoreElement);

    return () => observer.disconnect();
  }, [fetchNextPage, hasNextPage, isFetchNextPageError, isFetchingNextPage, loadMoreElement]);

  return {
    data: recommendationsQuery.data,
    isError: recommendationsQuery.isError,
    isFetchNextPageError,
    isFetchingNextPage,
    isPending: recommendationsQuery.isPending,
    hasNextPage,
    setLoadMoreElement,
    refetch: recommendationsQuery.refetch,
    fetchNextPage,
    recommendations: recommendationsQuery.data?.pages.flatMap((page) => page) ?? [],
  };
}
