import { useCallback, useState } from 'react';

export type SearchPageSize = 25 | 50;

export function useSearchPagination() {
  const [pageSize, setPageSize] = useState<SearchPageSize>(25);
  const [page, setPage] = useState(1);
  const resetPage = useCallback(() => setPage(1), []);

  function changePage(nextPage: number) {
    setPage(nextPage);
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'instant' : 'smooth' });
  }

  return { pageSize, setPageSize, page, resetPage, changePage };
}
