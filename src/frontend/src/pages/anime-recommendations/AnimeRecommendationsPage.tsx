import { Link, useParams } from '@tanstack/react-router';
import { ArrowLeft, LoaderCircle } from 'lucide-react';
import { useEffect } from 'react';

import { useAnimeDetails } from '@/entities/anime/hooks/use-anime-details';
import { getPreferredAnimeTitle } from '@/entities/anime/model/anime-details-model';
import { AnimeCard } from '@/entities/anime/ui/anime-card';
import { useRecommendations } from '@/features/recommendations/hooks/use-recommendations';
import { LoadingScreen } from '@/shared/components/loading-screen';
import { Navbar } from '@/shared/components/navbar';
import { PageContainer } from '@/shared/components/page-container';
import { Button } from '@/shared/components/ui/button';
import { updateDocumentMetaTags } from '@/shared/lib/document-meta-tags';
import { imageSrcSet } from '@/shared/lib/responsive-image-srcset';

export function AnimeRecommendationsPage() {
  const params = useParams({ from: '/anime/$id/$slug/recommendations' });
  const animeId = Number(params.id);
  const entryQuery = useAnimeDetails(animeId);
  const {
    data: recommendationsData,
    isError: recommendationsError,
    isFetchNextPageError,
    isFetchingNextPage,
    isPending: recommendationsPending,
    hasNextPage,
    setLoadMoreElement,
    refetch,
    fetchNextPage,
    recommendations,
  } = useRecommendations(animeId, entryQuery.data);

  useEffect(() => {
    if (!entryQuery.data) return;
    const title = getPreferredAnimeTitle(entryQuery.data);
    updateDocumentMetaTags(`${title} | Recommendations`, `View all of ${title}'s curated recommendations.`);
  }, [entryQuery.data]);

  if (entryQuery.isPending || recommendationsPending) {
    return <LoadingScreen label="Loading recommendations" />;
  }

  if (entryQuery.isError || !entryQuery.data || (recommendationsError && !recommendationsData)) {
    return (
      <main
        id="main-content"
        className="body-copy mx-auto flex min-h-screen max-w-3xl items-center justify-center px-4 py-24 text-center"
      >
        <div className="space-y-4">
          <p>Anime recommendations could not be loaded.</p>
          {recommendationsError && (
            <Button type="button" variant="outline" onClick={() => void refetch()}>
              Try again
            </Button>
          )}
        </div>
      </main>
    );
  }

  const entry = entryQuery.data;
  const title = entry.title_english?.trim() || entry.title;
  const imageWebp = entry.images?.webp?.image_url ?? '';
  const imageJpg = entry.images?.jpg?.image_url ?? '';
  const imageWebpSrcSet = imageSrcSet(entry.images?.webp);
  const imageJpgSrcSet = imageSrcSet(entry.images?.jpg);
  const recommendationCount = recommendations.length;
  const totalRecommendationCount = entry.recommendations.length;

  return (
    <main id="main-content" className="min-h-screen bg-background text-foreground">
      <Navbar />
      <PageContainer className="py-6 sm:py-8 lg:py-12">
        <Link
          to="/anime/$id/$slug"
          params={params}
          className="body-sm inline-flex min-h-11 items-center gap-2 rounded-md pr-3 text-muted-foreground transition-colors hover:bg-muted/60 hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
        >
          <ArrowLeft className="icon-sm" aria-hidden="true" />
          Back to anime
        </Link>
        <header className="mt-8 border-b pb-8 sm:mt-10 sm:pb-10">
          <div className="flex items-start gap-4 sm:gap-5">
            <picture className="hidden sm:block">
              {imageWebpSrcSet && <source type="image/webp" srcSet={imageWebpSrcSet} sizes="192px" />}
              <img
                src={imageJpg || imageWebp}
                srcSet={imageJpgSrcSet}
                sizes="192px"
                alt=""
                className="aspect-[2/3] w-20 rounded-md object-cover ring-1 ring-border sm:w-24"
                loading="eager"
                decoding="async"
              />
            </picture>
            <div className="min-w-0 flex-1">
              <p className="body-sm font-medium tracking-[0.12em] text-muted-foreground uppercase">
                Catalogue recommendations
              </p>
              <h1 className="heading-h2 mt-2 max-w-full wrap-break-word">{title}</h1>
              <p className="body-copy mt-3 max-w-none text-muted-foreground">
                A ranked set of titles with similar appeal, starting with the strongest matches.
              </p>
            </div>
          </div>
        </header>

        <section className="mt-8 sm:mt-10" aria-labelledby="recommendations-heading">
          <div className="mb-5 flex items-end justify-between gap-4 sm:mb-6">
            <div>
              <h2 id="recommendations-heading" className="heading-h5">
                Recommended anime
              </h2>
              <p className="body-sm mt-1 text-muted-foreground">
                {hasNextPage
                  ? `Showing ${recommendationCount} of ${totalRecommendationCount} titles`
                  : `${recommendationCount} ${recommendationCount === 1 ? 'title' : 'titles'}`}
              </p>
            </div>
          </div>
          {recommendationCount > 0 ? (
            <ul
              className="below-fold-content anime-card-grid anime-card-grid--five-column gap-4"
              aria-busy={isFetchingNextPage}
            >
              {recommendations.map((item, index) => (
                <li key={item.malId}>
                  <AnimeCard item={item} rank={index + 1} />
                </li>
              ))}
            </ul>
          ) : (
            <div className="body-copy rounded-lg border border-dashed p-8 text-center text-muted-foreground">
              No recommendations are available for this title yet.
            </div>
          )}
          {hasNextPage && (
            <div ref={setLoadMoreElement} className="mt-8 flex min-h-12 items-center justify-center" aria-live="polite">
              {isFetchingNextPage && (
                <>
                  <LoaderCircle className="size-5 animate-spin text-muted-foreground" aria-hidden="true" />
                  <span className="sr-only">Loading more recommendations</span>
                </>
              )}
              {isFetchNextPageError && (
                <Button type="button" variant="outline" onClick={() => void fetchNextPage()}>
                  Try loading more recommendations
                </Button>
              )}
            </div>
          )}
        </section>
      </PageContainer>
    </main>
  );
}
