import {
  ArrowDown01,
  ArrowDownAZ,
  ArrowDownWideNarrow,
  ArrowUp01,
  ArrowUpAZ,
  ArrowUpWideNarrow,
  LoaderCircle,
  X,
} from 'lucide-react';

import type { AnimeCardItem } from '@/entities/anime/model/anime-schema';
import type { SearchSort } from '@/features/search/model/search-types';

import { AnimeCard } from '@/entities/anime/ui/anime-card';
import { SearchPagination } from '@/features/search/ui/search-pagination';
import { Button } from '@/shared/components/ui/button';
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from '@/shared/components/ui/empty';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/components/ui/select';
import { Separator } from '@/shared/components/ui/separator';

const numberFormatter = new Intl.NumberFormat('en-US');

export interface SearchFilterChip {
  label: string;
  remove: () => void;
}

interface SearchResultsProps {
  results: readonly AnimeCardItem[];
  isSearching: boolean;
  isUpdating: boolean;
  isCatalogueLoading: boolean;
  catalogueError: Error | null;
  activeFilters: readonly SearchFilterChip[];
  totalResults: number;
  resultStart: number;
  resultEnd: number;
  currentPage: number;
  pageCount: number;
  pageSize: 25 | 50;
  sort: SearchSort;
  onSortChange: (value: SearchSort) => void;
  onPageSizeChange: (value: 25 | 50) => void;
  onReset: () => void;
  onPageChange: (page: number) => void;
}

export function SearchResults({
  results,
  isSearching,
  isUpdating,
  isCatalogueLoading,
  catalogueError,
  activeFilters,
  totalResults,
  resultStart,
  resultEnd,
  currentPage,
  pageCount,
  pageSize,
  sort,
  onSortChange,
  onPageSizeChange,
  onReset,
  onPageChange,
}: SearchResultsProps) {
  return (
    <section className="min-w-0 lg:col-span-4" aria-labelledby="search-results-heading">
      <h2 id="search-results-heading" className="sr-only">
        Search results
      </h2>
      <SearchToolbar
        totalResults={totalResults}
        resultStart={resultStart}
        resultEnd={resultEnd}
        sort={sort}
        pageSize={pageSize}
        onSortChange={onSortChange}
        onPageSizeChange={onPageSizeChange}
        onReset={onReset}
      />
      <SearchActiveFilters filters={activeFilters} />
      <Separator className="my-6" />
      {isCatalogueLoading ? (
        <output
          className="flex min-h-80 items-center justify-center rounded-lg border bg-background"
          aria-label="Loading anime"
        >
          <LoaderCircle
            className="size-8 animate-spin text-muted-foreground motion-reduce:animate-none"
            aria-hidden="true"
          />
        </output>
      ) : catalogueError ? (
        <Empty className="min-h-80 bg-background">
          <EmptyHeader>
            <EmptyTitle>Could not load the catalogue</EmptyTitle>
            <EmptyDescription>Refresh the page and try again.</EmptyDescription>
          </EmptyHeader>
        </Empty>
      ) : isUpdating || isSearching ? (
        <output className="flex min-h-80 items-center justify-center rounded-lg border bg-background text-muted-foreground">
          {isUpdating ? 'Updating results…' : 'Searching titles…'}
        </output>
      ) : results.length > 0 ? (
        <div className="anime-card-grid gap-6">
          {results.map((item) => (
            <AnimeCard key={item.malId} item={item} />
          ))}
        </div>
      ) : (
        <Empty className="min-h-80 bg-background">
          <EmptyHeader>
            <EmptyTitle>No anime match those criteria</EmptyTitle>
            <EmptyDescription>Try removing a filter or searching another title.</EmptyDescription>
          </EmptyHeader>
          <Button variant="outline" onClick={onReset}>
            Clear search
          </Button>
        </Empty>
      )}
      <SearchPagination currentPage={currentPage} pageCount={pageCount} onPageChange={onPageChange} />
    </section>
  );
}

function SearchToolbar({
  totalResults,
  resultStart,
  resultEnd,
  sort,
  pageSize,
  onSortChange,
  onPageSizeChange,
  onReset,
}: Omit<
  SearchResultsProps,
  | 'results'
  | 'isSearching'
  | 'isUpdating'
  | 'isCatalogueLoading'
  | 'catalogueError'
  | 'activeFilters'
  | 'currentPage'
  | 'pageCount'
  | 'onPageChange'
>) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4">
      <p className="body-sm text-muted-foreground">
        <span className="font-medium text-foreground">
          {totalResults === 0
            ? 'No matching titles'
            : `Showing ${formatCount(resultStart)}–${formatCount(resultEnd)} of ${formatCount(totalResults)} titles`}
        </span>
      </p>
      <div className="hidden items-center gap-4 lg:flex">
        <div className="relative z-20">
          <SortSelect value={sort} onChange={onSortChange} />
        </div>
        <div className="relative z-10">
          <Select
            value={String(pageSize)}
            onValueChange={(value) => {
              if (value === '25') onPageSizeChange(25);
              if (value === '50') onPageSizeChange(50);
            }}
          >
            <SelectTrigger className="h-11 w-28">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="25">25 / page</SelectItem>
              <SelectItem value="50">50 / page</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button variant="ghost" size="sm" onClick={onReset}>
          Clear all
        </Button>
      </div>
    </div>
  );
}

function SearchActiveFilters({ filters }: { filters: readonly SearchFilterChip[] }) {
  if (filters.length === 0) return null;
  return (
    <div className="mt-4 flex flex-wrap items-center gap-2" aria-label="Active filters">
      <span className="body-sm text-muted-foreground">Filters</span>
      {filters.map((filter) => (
        <button
          key={filter.label}
          type="button"
          onClick={filter.remove}
          className="body-sm inline-flex min-h-9 items-center gap-1.5 rounded-full bg-secondary px-3 py-1 text-secondary-foreground transition-colors hover:bg-secondary/80 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none motion-reduce:transition-none"
        >
          {filter.label}
          <X className="icon-xs" aria-hidden="true" />
        </button>
      ))}
    </div>
  );
}

function SortSelect({
  value,
  onChange,
}: {
  value: SearchResultsProps['sort'];
  onChange: SearchResultsProps['onSortChange'];
}) {
  return (
    <div className="body-sm flex items-center gap-2 text-muted-foreground">
      <span id="search-sort-label">Sort</span>
      <Select
        value={value}
        onValueChange={(nextValue) => {
          if (
            nextValue === 'title-asc' ||
            nextValue === 'title-desc' ||
            nextValue === 'score-asc' ||
            nextValue === 'score-desc' ||
            nextValue === 'year-asc' ||
            nextValue === 'year-desc'
          )
            onChange(nextValue);
        }}
      >
        <SelectTrigger className="h-11 min-w-44" aria-labelledby="search-sort-label">
          <SelectValue />
        </SelectTrigger>
        <SelectContent className="z-[60]">
          <SelectItem value="title-asc">
            <ArrowDownAZ data-icon="inline-start" /> Title A–Z
          </SelectItem>
          <SelectItem value="title-desc">
            <ArrowUpAZ data-icon="inline-start" /> Title Z–A
          </SelectItem>
          <SelectItem value="score-desc">
            <ArrowDownWideNarrow data-icon="inline-start" /> Score high to low
          </SelectItem>
          <SelectItem value="score-asc">
            <ArrowUpWideNarrow data-icon="inline-start" /> Score low to high
          </SelectItem>
          <SelectItem value="year-desc">
            <ArrowDown01 data-icon="inline-start" /> Year newest first
          </SelectItem>
          <SelectItem value="year-asc">
            <ArrowUp01 data-icon="inline-start" /> Year oldest first
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}

function formatCount(value: number): string {
  return numberFormatter.format(value);
}
