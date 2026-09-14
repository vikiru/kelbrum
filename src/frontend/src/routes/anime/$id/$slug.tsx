import { createFileRoute, Outlet } from '@tanstack/react-router';

import { getAnimeDetailsQueryOptions, getAnimeRecommendationsQueryOptions } from '@/entities/anime/api/anime-queries';
import { LoadingScreen } from '@/shared/components/loading-screen';

export const Route = createFileRoute('/anime/$id/$slug')({
  ssr: false,
  pendingComponent: () => <LoadingScreen label="Loading anime details" />,
  loader: async ({ context, params }) => {
    const animeId = Number(params.id);
    const entry = await context.queryClient.ensureQueryData(getAnimeDetailsQueryOptions(animeId));
    void context.queryClient.prefetchQuery(getAnimeRecommendationsQueryOptions(animeId, 10, entry));
    return entry;
  },
  component: AnimeDetailsLayout,
  head: ({ params }) => ({
    meta: [
      { title: `${params.slug.replaceAll('-', ' ')} | Kelbrum` },
      { name: 'description', content: 'View anime details, metadata, and recommendations on Kelbrum.' },
      { name: 'robots', content: 'noindex, follow' },
    ],
  }),
});

function AnimeDetailsLayout() {
  return <Outlet />;
}
