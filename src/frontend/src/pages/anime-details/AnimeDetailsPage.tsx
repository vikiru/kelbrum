import { useParams } from '@tanstack/react-router';
import { useEffect } from 'react';

import { useAnimeDetails } from '@/entities/anime/hooks/use-anime-details';
import { useAnimeRecommendations } from '@/entities/anime/hooks/use-anime-recommendations';
import { useRandomRecommendations } from '@/entities/anime/hooks/use-random-recommendations';
import {
  createAnimePageModel,
  createAnimeDetailFields,
  getPreferredAnimeTitle,
} from '@/entities/anime/model/anime-details-model';
import { AnimeDetailsHero } from '@/entities/anime/ui/anime-details-hero';
import { AnimeDetailsInfo } from '@/entities/anime/ui/anime-details-info';
import { AnimeDetailsRecommendations } from '@/entities/anime/ui/anime-details-recommendations';
import { LoadingScreen } from '@/shared/components/loading-screen';
import { Navbar } from '@/shared/components/navbar';
import { PageContainer } from '@/shared/components/page-container';
import { Separator } from '@/shared/components/ui/separator';
import { updateDocumentMetaTags } from '@/shared/lib/document-meta-tags';

export function AnimeDetailsPage() {
  const params = useParams({ from: '/anime/$id/$slug' });
  const animeId = Number(params.id);
  const animeQuery = useAnimeDetails(animeId);
  const recommendationsQuery = useAnimeRecommendations(animeId, 10, animeQuery.data);
  const randomRecommendations = useRandomRecommendations(recommendationsQuery.data, 10);

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
  const recommendations = randomRecommendations ?? [];

  return (
    <main id="main-content" className="min-h-screen bg-background text-foreground">
      <Navbar />

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

        {(recommendationsQuery.isPending || recommendationsQuery.isError || recommendations.length > 0) && (
          <AnimeDetailsRecommendations
            animeId={params.id}
            slug={params.slug}
            items={recommendations}
            totalCount={entry.recommendations.length}
            isLoading={recommendationsQuery.isPending}
            isError={recommendationsQuery.isError}
          />
        )}
      </PageContainer>
    </main>
  );
}
