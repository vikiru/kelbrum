import { useQuery } from '@tanstack/react-query';

import {
  getSearchCatalogueQueryOptions,
  getSearchFilterOptionsQueryOptions,
  type SearchFilterOptions,
  type SearchCatalogueItem,
} from '@/features/search/model/search-catalogue';

export function useSearchCatalogue() {
  const catalogueQuery = useQuery(getSearchCatalogueQueryOptions());
  const filterOptionsQuery = useQuery(getSearchFilterOptionsQueryOptions());
  const error = catalogueQuery.error ?? filterOptionsQuery.error ?? null;

  return {
    catalogue: catalogueQuery.data ?? [],
    filterOptions: filterOptionsQuery.data ?? { genres: [], themes: [], demographics: [] },
    isLoading: catalogueQuery.isLoading || filterOptionsQuery.isLoading,
    error,
  } satisfies {
    catalogue: SearchCatalogueItem[];
    filterOptions: SearchFilterOptions;
    isLoading: boolean;
    error: Error | null;
  };
}
