import { useMemo, useState } from 'react';

interface SearchSuggestionItem {
  malId: number;
}

export function useSearchSuggestions<T extends SearchSuggestionItem>(query: string, items: readonly T[]) {
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(0);
  const suggestions = useMemo(() => (query.trim() ? items.slice(0, 10) : []), [items, query]);

  function resetActiveSuggestion() {
    setActiveSuggestionIndex(0);
  }

  function moveActiveSuggestion(direction: 1 | -1) {
    setActiveSuggestionIndex((index) => Math.max(0, Math.min(index + direction, Math.max(0, suggestions.length - 1))));
  }

  return {
    suggestions,
    activeSuggestionIndex,
    setActiveSuggestionIndex,
    resetActiveSuggestion,
    moveActiveSuggestion,
  };
}
