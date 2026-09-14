import { useCallback, useState } from 'react';

import type { SearchSort } from '@/features/search/model/search-types';

import { useSearchCatalogue } from '@/features/search/hooks/use-search-catalogue';
import { useSearchFilters, type SearchFilters } from '@/features/search/hooks/use-search-filters';
import { useSearchIndex } from '@/features/search/hooks/use-search-index';
import { useSearchPagination, type SearchPageSize } from '@/features/search/hooks/use-search-pagination';
import { useSearchQuery } from '@/features/search/hooks/use-search-query';
import { useSearchViewState } from '@/features/search/hooks/use-search-view-state';

export function useSearchScreenState() {
  const queryState = useSearchQuery();
  const filterState = useSearchFilters();
  const paginationState = useSearchPagination();
  const viewState = useSearchViewState();
  const [sort, setSort] = useState<SearchSort>('score-desc');
  const searchIndex = useSearchIndex(queryState.deferredQuery);
  const catalogueState = useSearchCatalogue();
  const { setQuery: updateQuery, resetQuery } = queryState;
  const { setFilters: updateFilters, updateFilter: updateFilterState, resetFilters } = filterState;
  const { resetPage, setPageSize: updatePageSize } = paginationState;
  const setQuery = useCallback(
    (query: string) => {
      updateQuery(query);
      resetPage();
    },
    [resetPage, updateQuery],
  );
  const setFilters = useCallback(
    (nextFilters: SearchFilters | ((currentFilters: SearchFilters) => SearchFilters)) => {
      updateFilters(nextFilters);
      resetPage();
    },
    [resetPage, updateFilters],
  );
  const setPageSize = useCallback(
    (nextPageSize: SearchPageSize) => {
      updatePageSize(nextPageSize);
      resetPage();
    },
    [resetPage, updatePageSize],
  );
  const updateFilter = useCallback(
    <Key extends keyof SearchFilters>(key: Key, value: SearchFilters[Key]) => {
      updateFilterState(key, value);
      resetPage();
    },
    [resetPage, updateFilterState],
  );
  const resetSearch = useCallback(() => {
    resetQuery();
    resetFilters();
    setSort('score-desc');
    resetPage();
  }, [resetFilters, resetPage, resetQuery]);

  return {
    query: queryState.query,
    deferredQuery: queryState.deferredQuery,
    isQueryStale: queryState.isQueryStale,
    filters: filterState.filters,
    page: paginationState.page,
    pageSize: paginationState.pageSize,
    changePage: paginationState.changePage,
    ...viewState,
    sort,
    setSort,
    setQuery,
    setFilters,
    updateFilter,
    setPageSize,
    resetSearch,
    ...searchIndex,
    ...catalogueState,
  };
}
