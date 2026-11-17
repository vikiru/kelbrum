import { useParams } from '@tanstack/react-router';
import { useEffect, useMemo, useState } from 'react';

import { ANIME_RECOMMENDATION_BATCH_SIZE } from '@/entities/anime/api/anime-queries';
import { useAnimeDetails } from '@/entities/anime/hooks/use-anime-details';
import { useAnimeRecommendationBatches } from '@/entities/anime/hooks/use-anime-recommendation-batches';
import {
  createAnimePageModel,
  createAnimeDetailFields,
  getPreferredAnimeTitle,
} from '@/entities/anime/model/anime-details-model';
import { AnimeDetailsHero } from '@/entities/anime/ui/anime-details-hero';
import { AnimeDetailsInfo } from '@/entities/anime/ui/anime-details-info';
import { AnimeDetailsRecommendations } from '@/entities/anime/ui/anime-details-recommendations';
import { LoadingScreen } from '@/shared/components/loading-screen';
import { PageContainer } from '@/shared/components/page-container';
import { Separator } from '@/shared/components/ui/separator';
import { updateDocumentMetaTags } from '@/shared/lib/document-meta-tags';
import { fisherYatesShuffle } from '@/shared/lib/fisher-yates-shuffle';

const DETAILS_RECOMMENDATION_LIMIT = 10;
const RELOAD_RECOMMENDATION_POOL_LIMIT = 50;
const RELOAD_RECOMMENDATION_BATCH_COUNT = Math.ceil(RELOAD_RECOMMENDATION_POOL_LIMIT / ANIME_RECOMMENDATION_BATCH_SIZE);

export function AnimeDetailsPage() {
  const params = useParams({ from: '/anime/$id/$slug' });
  const animeId = Number(params.id);
  const animeQuery = useAnimeDetails(animeId);
  const {
    data: recommendationsData,
    fetchNextPage,
    hasNextPage,
    isError: recommendationsError,
    isFetchingNextPage,
    isFetchNextPageError,
    isPending: recommendationsPending,
  } = useAnimeRecommendationBatches(animeId, animeQuery.data);
  const recommendationPageCount = recommendationsData?.pages.length ?? 0;
  const browserReloadPath = useMemo(() => getBrowserReloadPath(), []);
  // Client navigation keeps rank order; a browser reload opts into top-pool variety.
  const isReloadOfCurrentAnime =
    browserReloadPath !== null && typeof window !== 'undefined' && browserReloadPath === window.location.pathname;
  const hasLoadedShufflePool =
    recommendationPageCount >= RELOAD_RECOMMENDATION_BATCH_COUNT || !hasNextPage || isFetchNextPageError;
  const isLoadingShufflePool = isReloadOfCurrentAnime && !hasLoadedShufflePool && !recommendationsError;

  useEffect(() => {
    if (
      !isReloadOfCurrentAnime ||
      !hasNextPage ||
      isFetchingNextPage ||
      recommendationPageCount >= RELOAD_RECOMMENDATION_BATCH_COUNT
    ) {
      return;
    }
    void fetchNextPage();
  }, [isReloadOfCurrentAnime, recommendationPageCount, fetchNextPage, hasNextPage, isFetchingNextPage]);

  const topRecommendations = useMemo(() => {
    if (isLoadingShufflePool) return [];
    return recommendationsData?.pages.flatMap((page) => page).slice(0, RELOAD_RECOMMENDATION_POOL_LIMIT) ?? [];
  }, [recommendationsData, isLoadingShufflePool]);

  const [recommendations, setRecommendations] = useState(() =>
    topRecommendations.slice(0, DETAILS_RECOMMENDATION_LIMIT),
  );

  useEffect(() => {
    if (isLoadingShufflePool) {
      setRecommendations([]);
      return;
    }
    const candidates = isReloadOfCurrentAnime ? fisherYatesShuffle(topRecommendations) : topRecommendations;
    setRecommendations(candidates.slice(0, DETAILS_RECOMMENDATION_LIMIT));
  }, [topRecommendations, isLoadingShufflePool, isReloadOfCurrentAnime]);

  useEffect(() => {
    if (!animeQuery.data) return;
    const title = getPreferredAnimeTitle(animeQuery.data);
    updateDocumentMetaTags(`${title} | Kelbrum`, `Read more about ${title} and see its curated recommendations.`);
  }, [animeQuery.data]);

  if (!Number.isInteger(animeId) || animeId < 1) {
    return (
      <main id="main-content" className="body-copy mx-auto min-h-screen max-w-3xl px-4 py-24 text-center">
        Anime details could not be found.
      </main>
    );
  }

  if (animeQuery.isPending) {
    return <LoadingScreen label="Loading anime details" />;
  }

  if (animeQuery.isError || !animeQuery.data) {
    return (
      <main id="main-content" className="body-copy mx-auto min-h-screen max-w-3xl px-4 py-24 text-center">
        Anime details could not be found.
      </main>
    );
  }

  const entry = animeQuery.data;
  const anime = createAnimePageModel(entry);

  return (
    <main id="main-content" className="min-h-screen bg-background text-foreground">
      <PageContainer className="py-8 lg:py-12">
        <AnimeDetailsHero
          anime={anime}
          images={entry.images}
          trailerUrl={entry.trailer?.url ?? null}
          malUrl={entry.url}
          animeId={animeId}
        />

        <Separator className="my-14" />

        <AnimeDetailsInfo details={createAnimeDetailFields(anime)} />

        <Separator className="my-14" />

        {(recommendationsPending || isLoadingShufflePool || recommendationsError || recommendations.length > 0) && (
          <AnimeDetailsRecommendations
            animeId={params.id}
            slug={params.slug}
            items={recommendations}
            totalCount={entry.recommendations.length}
            isLoading={recommendationsPending || isLoadingShufflePool}
            isError={recommendationsError}
          />
        )}
      </PageContainer>
    </main>
  );
}

function getBrowserReloadPath(): string | null {
  if (typeof window === 'undefined') return null;
  const [navigation] = window.performance.getEntriesByType('navigation');
  if (!(navigation instanceof PerformanceNavigationTiming) || navigation.type !== 'reload') return null;
  return new URL(navigation.name).pathname;
}
