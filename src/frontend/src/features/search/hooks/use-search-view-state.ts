import { useState } from 'react';

export function useSearchViewState() {
  const [filtersOpen, setFiltersOpen] = useState(false);

  return { filtersOpen, setFiltersOpen };
}
