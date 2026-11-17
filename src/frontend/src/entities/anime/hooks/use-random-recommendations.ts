import { useEffect, useState } from 'react';

import { fisherYatesShuffle } from '@/shared/lib/fisher-yates-shuffle';

export function useRandomRecommendations<T>(items: readonly T[] | undefined, limit: number): T[] {
  const [recommendations, setRecommendations] = useState<T[]>(() => (items ?? []).slice(0, limit));

  useEffect(() => {
    const availableItems = items ?? [];
    if (availableItems.length <= limit) {
      setRecommendations(availableItems.slice(0, limit));
      return;
    }
    setRecommendations(fisherYatesShuffle(availableItems).slice(0, limit));
  }, [items, limit]);

  return recommendations;
}
