import { createFileRoute } from '@tanstack/react-router';

import {
  getSearchCatalogueQueryOptions,
  getSearchFilterOptionsQueryOptions,
} from '@/features/search/model/search-catalogue';
import { SearchScreen } from '@/features/search/ui/search-page';

export const Route = createFileRoute('/search')({
  loader: async ({ context }) => {
    if (typeof window === 'undefined') return;
    await Promise.all([
      context.queryClient.ensureQueryData(getSearchCatalogueQueryOptions()),
      context.queryClient.ensureQueryData(getSearchFilterOptionsQueryOptions()),
    ]);
  },
  component: SearchScreen,
  head: () => ({
    meta: [
      { title: 'Search Anime | Kelbrum' },
      {
        name: 'description',
        content: 'Search by title or browse the catalogue using filters to find something you want to watch.',
      },
      { name: 'robots', content: 'noindex, follow' },
    ],
  }),
});
