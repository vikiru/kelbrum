import { createFileRoute, notFound } from '@tanstack/react-router';

import { getAnimeDetailsQueryOptions } from '@/entities/anime/api/anime-queries';
import { AnimeRecommendationsPage } from '@/pages/anime-recommendations/AnimeRecommendationsPage';
import { LoadingScreen } from '@/shared/components/loading-screen';

export const Route = createFileRoute('/anime/$id/$slug/recommendations')({
  ssr: false,
  pendingComponent: () => <LoadingScreen label="Loading recommendations" />,
  loader: async ({ context, params }) => {
    const animeId = Number(params.id);
    if (!Number.isInteger(animeId) || animeId <= 0) {
      throw notFound();
    }
    const entry = await context.queryClient.ensureQueryData(getAnimeDetailsQueryOptions(animeId));
    if (!entry) {
      throw notFound();
    }
    return entry;
  },
  component: AnimeRecommendationsPage,
  head: ({ params }) => ({
    meta: [
      { title: `Recommendations for ${params.slug.replaceAll('-', ' ')} | Kelbrum` },
      { name: 'description', content: 'Browse anime recommendations matched to this title on Kelbrum.' },
      { name: 'robots', content: 'noindex, follow' },
    ],
  }),
});
