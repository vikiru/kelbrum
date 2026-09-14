import { createFileRoute } from '@tanstack/react-router';

import { HomePage } from '@/pages/home/HomePage';

export const Route = createFileRoute('/')({
  component: HomePage,
  head: () => ({
    links: [{ rel: 'canonical', href: '/' }],
    meta: [
      { title: 'Discover your next favourite anime | Kelbrum' },
      {
        name: 'description',
        content:
          'Find anime through curated picks, detailed metadata, and recommendations based on titles you already enjoy.',
      },
      { property: 'og:type', content: 'website' },
      { property: 'og:title', content: 'Discover your next favourite anime | Kelbrum' },
      {
        property: 'og:description',
        content:
          'Find anime through curated picks, detailed metadata, and recommendations based on titles you already enjoy.',
      },
      { name: 'twitter:card', content: 'summary' },
      { name: 'twitter:title', content: 'Discover your next favourite anime | Kelbrum' },
      {
        name: 'twitter:description',
        content:
          'Find anime through curated picks, detailed metadata, and recommendations based on titles you already enjoy.',
      },
    ],
  }),
});
