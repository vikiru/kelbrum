import { useDeferredValue, useState } from 'react';

export function useSearchQuery() {
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query);

  function resetQuery() {
    setQuery('');
  }

  return {
    query,
    deferredQuery,
    isQueryStale: query !== deferredQuery,
    setQuery,
    resetQuery,
  };
}
