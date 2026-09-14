import { createRouter as createTanStackRouter } from '@tanstack/react-router';

import { routeTree } from '@/routeTree.gen';
import { createQueryClient } from '@/shared/api/query-client';

export function getRouter() {
  const router = createTanStackRouter({
    routeTree,
    context: { queryClient: createQueryClient() },
    scrollRestoration: true,
    defaultPreload: 'intent',
    defaultPreloadStaleTime: Infinity,
  });

  return router;
}

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof getRouter>;
  }
}
