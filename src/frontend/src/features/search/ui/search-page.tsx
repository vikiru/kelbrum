import { useNavigate } from '@tanstack/react-router';
import { Filter } from 'lucide-react';
import { useEffect } from 'react';

import { useSearchResults } from '@/features/search/hooks/use-search-results';
import { useSearchScreenState } from '@/features/search/hooks/use-search-screen-state';
import { useSearchSuggestions } from '@/features/search/hooks/use-search-suggestions';
import { formatFilterValue } from '@/features/search/lib/search-filter-formatting';
import { SearchFilterPanel } from '@/features/search/ui/search-filter-panel';
import { SortSelect } from '@/features/search/ui/search-filters';
import { SearchHeader } from '@/features/search/ui/search-header';
import { SearchResults } from '@/features/search/ui/search-results';
import { Navbar } from '@/shared/components/navbar';
import { PageContainer } from '@/shared/components/page-container';
import { Button } from '@/shared/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/components/ui/select';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/shared/components/ui/sheet';
import { slugify } from '@/shared/lib/slugify';

const numberFormatter = new Intl.NumberFormat('en-US');

export function SearchScreen() {
  const navigate = useNavigate();
  const {
    query,
    deferredQuery,
    isQueryStale,
    setQuery,
    sort,
    setSort,
    pageSize,
    setPageSize,
    page,
    filtersOpen,
    setFiltersOpen,
    filters,
    updateFilter,
    resetSearch,
    changePage,
    indexedIds,
    isSearching,
    error: indexError,
    catalogue: searchCatalogue,
    filterOptions: searchFilterOptions,
    isLoading: isCatalogueLoading,
    error: catalogueError,
  } = useSearchScreenState();
  const {
    type: typeFilter,
    rating: ratingFilter,
    demographic: demographicFilter,
    genres: genreFilters,
    themes: themeFilters,
    scoreRange,
    yearRange,
    episodeRange,
  } = filters;
  const resetFilters = resetSearch;
  const filterPanelProps = {
    options: searchFilterOptions,
    onReset: resetFilters,
    typeFilter,
    onTypeChange: (value: string) => updateFilter('type', value),
    ratingFilter,
    onRatingChange: (value: string) => updateFilter('rating', value),
    demographicFilter,
    onDemographicChange: (value: string) => updateFilter('demographic', value),
    genreFilters,
    onGenresChange: (values: string[]) => updateFilter('genres', values),
    themeFilters,
    onThemesChange: (values: string[]) => updateFilter('themes', values),
    scoreRange,
    onScoreChange: (values: [number, number]) => updateFilter('scoreRange', values),
    yearRange,
    onYearChange: (values: [string, string]) => updateFilter('yearRange', values),
    episodeRange,
    onEpisodesChange: (values: [string, string]) => updateFilter('episodeRange', values),
  };

  const resultSet = useSearchResults({
    catalogue: searchCatalogue,
    indexedIds,
    query: deferredQuery,
    filters,
    sort,
  });
  const allResults = resultSet.items;
  const pageCount = Math.max(1, Math.ceil(allResults.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const results = allResults.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  const resultStart = allResults.length === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const resultEnd = Math.min(currentPage * pageSize, allResults.length);
  const activeFilters = [
    typeFilter !== 'all' && {
      label: `Type: ${formatFilterValue(typeFilter)}`,
      remove: () => updateFilter('type', 'all'),
    },
    ratingFilter !== 'all' && { label: `Rating: ${ratingFilter}`, remove: () => updateFilter('rating', 'all') },
    demographicFilter !== 'all' && {
      label: `Demographic: ${formatFilterValue(demographicFilter)}`,
      remove: () => updateFilter('demographic', 'all'),
    },
    genreFilters.length > 0 && {
      label: `Genres: ${genreFilters.length} selected`,
      remove: () => updateFilter('genres', []),
    },
    themeFilters.length > 0 && {
      label: `Themes: ${themeFilters.length} selected`,
      remove: () => updateFilter('themes', []),
    },
    (scoreRange[0] > 0 || scoreRange[1] < 10) && {
      label: `Score: ${scoreRange[0]}–${scoreRange[1]}`,
      remove: () => updateFilter('scoreRange', [0, 10]),
    },
    yearRange.some(Boolean) && {
      label: `Year: ${yearRange.filter(Boolean).join('–')}`,
      remove: () => updateFilter('yearRange', ['', '']),
    },
    episodeRange.some(Boolean) && {
      label: `Episodes: ${episodeRange.filter(Boolean).join('–')}`,
      remove: () => updateFilter('episodeRange', ['', '']),
    },
  ].filter((filter): filter is { label: string; remove: () => void } => Boolean(filter));
  const { suggestions, activeSuggestionIndex, setActiveSuggestionIndex, resetActiveSuggestion, moveActiveSuggestion } =
    useSearchSuggestions(deferredQuery, allResults);

  const searchError = indexError ?? catalogueError;

  useEffect(() => {
    const activeSuggestion = suggestions[activeSuggestionIndex];
    if (activeSuggestion) {
      const suggestion = document.getElementById(`search-suggestion-${activeSuggestion.malId}`);
      suggestion?.scrollIntoView({ block: 'nearest' });
    }
  }, [activeSuggestionIndex, suggestions]);

  function selectSuggestion(index: number) {
    const item = suggestions[index];
    if (!item) return;
    const title = item.titleEnglish?.trim() || item.title;
    void navigate({ to: '/anime/$id/$slug', params: { id: String(item.malId), slug: slugify(title) } });
  }

  return (
    <main id="main-content" className="min-h-screen bg-muted/20 text-foreground">
      <Navbar />
      <PageContainer className="py-10 lg:py-14">
        <Sheet open={filtersOpen} onOpenChange={setFiltersOpen}>
          <SearchHeader
            query={query}
            suggestions={suggestions}
            activeSuggestionIndex={activeSuggestionIndex}
            onQueryChange={setQuery}
            onActiveSuggestionChange={setActiveSuggestionIndex}
            onMoveSuggestion={moveActiveSuggestion}
            onSelectSuggestion={selectSuggestion}
            onResetActiveSuggestion={resetActiveSuggestion}
            actions={
              <SheetTrigger
                render={
                  <button
                    type="button"
                    aria-label="Refine search filters"
                    className="inline-flex min-h-14 shrink-0 items-center justify-center gap-2 rounded-lg border border-border bg-background px-3 text-sm font-medium text-foreground transition-[background-color,border-color,color,box-shadow] hover:bg-muted/60 focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 focus-visible:outline-none motion-reduce:transition-none"
                  />
                }
              >
                <Filter data-icon="inline-start" /> Refine
              </SheetTrigger>
            }
          />
          <SheetContent side="bottom" className="flex max-h-[88vh] flex-col rounded-t-2xl">
            <SheetHeader className="text-left">
              <SheetTitle>Refine results</SheetTitle>
              <SheetDescription>Choose what matters to you. Changes update the list when you’re done.</SheetDescription>
            </SheetHeader>
            <div className="min-h-0 flex-1 overflow-y-auto px-4 pb-24">
              <div className="mb-6 border-b pb-6">
                <p className="body-sm mb-2 font-medium text-foreground">Sort results</p>
                <SortSelect value={sort} onChange={setSort} />
                <p className="body-sm mt-4 mb-2 font-medium text-foreground">Titles per page</p>
                <Select
                  value={String(pageSize)}
                  onValueChange={(value) => {
                    if (value === '25') setPageSize(25);
                    if (value === '50') setPageSize(50);
                  }}
                >
                  <SelectTrigger className="h-11 w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="25">25 / page</SelectItem>
                    <SelectItem value="50">50 / page</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <SearchFilterPanel {...filterPanelProps} />
            </div>
            <div className="absolute inset-x-0 bottom-0 flex gap-3 border-t bg-background p-4">
              <Button variant="ghost" className="min-h-11" onClick={resetFilters}>
                Clear all
              </Button>
              <Button className="min-h-11 flex-1" onClick={() => setFiltersOpen(false)}>
                Show {formatCount(allResults.length)} titles
              </Button>
            </div>
          </SheetContent>
        </Sheet>
        <div className="mt-12 grid gap-10 lg:grid-cols-5 lg:gap-x-8">
          <aside className="hidden lg:col-span-1 lg:block">
            <div className="rounded-2xl bg-background p-6 shadow-sm ring-1 ring-foreground/10">
              <SearchFilterPanel {...filterPanelProps} />
            </div>
          </aside>
          <SearchResults
            results={results}
            isSearching={isSearching}
            isUpdating={isQueryStale}
            isCatalogueLoading={isCatalogueLoading || (searchCatalogue.length === 0 && !catalogueError)}
            catalogueError={searchError}
            activeFilters={activeFilters}
            totalResults={allResults.length}
            resultStart={resultStart}
            resultEnd={resultEnd}
            currentPage={currentPage}
            pageCount={pageCount}
            pageSize={pageSize}
            sort={sort}
            onSortChange={setSort}
            onPageSizeChange={(nextPageSize) => {
              setPageSize(nextPageSize);
            }}
            onReset={resetFilters}
            onPageChange={changePage}
          />
        </div>
      </PageContainer>
    </main>
  );
}

function formatCount(value: number): string {
  return numberFormatter.format(value);
}
