import { useMemo } from 'react';

import { useMounted } from '@/shared/hooks/use-mounted';
import { fisherYatesShuffle } from '@/shared/lib/fisher-yates-shuffle';

export function useRandomRecommendations<T>(items: readonly T[] | undefined, limit: number): T[] {
  const mounted = useMounted();

  return useMemo(() => {
    const availableItems = items ?? [];
    if (availableItems.length <= limit || !mounted) {
      return availableItems.slice(0, limit);
    }
    return fisherYatesShuffle(availableItems).slice(0, limit);
  }, [items, limit, mounted]);
}
