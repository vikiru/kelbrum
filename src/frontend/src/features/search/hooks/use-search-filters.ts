import { useState } from 'react';

export type NumericRange = [string, string];

export interface SearchFilters {
  type: string;
  rating: string;
  demographic: string;
  genres: string[];
  themes: string[];
  scoreRange: [number, number];
  yearRange: NumericRange;
  episodeRange: NumericRange;
}

const initialFilters: SearchFilters = {
  type: 'all',
  rating: 'all',
  demographic: 'all',
  genres: [],
  themes: [],
  scoreRange: [0, 10],
  yearRange: ['', ''],
  episodeRange: ['', ''],
};

export function useSearchFilters() {
  const [filters, setFilters] = useState<SearchFilters>(initialFilters);

  function updateFilter<Key extends keyof SearchFilters>(key: Key, value: SearchFilters[Key]) {
    setFilters((currentFilters) => ({ ...currentFilters, [key]: value }));
  }

  function resetFilters() {
    setFilters(initialFilters);
  }

  return {
    filters,
    setFilters,
    updateFilter,
    resetFilters,
  };
}
