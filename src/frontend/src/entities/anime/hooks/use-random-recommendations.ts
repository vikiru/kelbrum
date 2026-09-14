import { useMemo } from 'react';

import { useMounted } from '@/shared/hooks/use-mounted';
import { fisherYatesShuffle } from '@/shared/lib/fisher-yates-shuffle';

export function useRandomRecommendations<T>(items: readonly T[] | undefined, limit: number): T[] {
  const mounted = useMounted();

  return useMemo(
    () => (mounted ? fisherYatesShuffle(items ?? []).slice(0, limit) : (items ?? []).slice(0, limit)),
    [items, limit, mounted],
  );
}
