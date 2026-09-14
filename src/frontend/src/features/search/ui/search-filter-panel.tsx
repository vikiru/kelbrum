import { SearchFilters, type SearchFiltersProps, type SearchFilterOptions } from '@/features/search/ui/search-filters';

export type SearchFilterPanelProps = SearchFiltersProps & {
  options: SearchFilterOptions;
};

export function SearchFilterPanel(props: SearchFilterPanelProps) {
  return <SearchFilters {...props} />;
}
