import { createFileRoute } from '@tanstack/react-router';

import { AnimeDetailsPage } from '@/pages/anime-details/AnimeDetailsPage';

export const Route = createFileRoute('/anime/$id/$slug/')({
  component: AnimeDetailsPage,
});
