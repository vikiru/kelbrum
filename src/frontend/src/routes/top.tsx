import { createFileRoute } from '@tanstack/react-router';

import { TopRankedPage } from '@/pages/top/TopRankedPage';

export const Route = createFileRoute('/top')({
  component: TopRankedPage,
  head: () => ({
    meta: [
      { title: 'Top 100 Anime | Kelbrum' },
      {
        name: 'description',
        content:
          'The highest-rated anime in the catalogue, ranked by score. See what made the Top 100 and find something worth watching.',
      },
      { name: 'robots', content: 'noindex, follow' },
    ],
  }),
});
