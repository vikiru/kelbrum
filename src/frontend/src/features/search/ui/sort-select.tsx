import { ArrowDown01, ArrowDownAZ, ArrowDownWideNarrow, ArrowUp01, ArrowUpAZ, ArrowUpWideNarrow } from 'lucide-react';
import { memo, useId } from 'react';

import type { SearchSort } from '@/features/search/model/search-types';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/components/ui/select';

export function isSearchSort(value: unknown): value is SearchSort {
  return (
    value === 'title-asc' ||
    value === 'title-desc' ||
    value === 'score-asc' ||
    value === 'score-desc' ||
    value === 'year-asc' ||
    value === 'year-desc'
  );
}

export interface SortSelectProps {
  value: SearchSort;
  onChange: (value: SearchSort) => void;
  showLabel?: boolean;
}

export const SortSelect = memo(function SortSelect({ value, onChange, showLabel = false }: SortSelectProps) {
  const labelId = useId();
  const select = (
    <Select
      value={value}
      onValueChange={(nextValue) => {
        if (isSearchSort(nextValue)) onChange(nextValue);
      }}
    >
      <SelectTrigger
        className="h-11 min-w-44"
        aria-label={showLabel ? undefined : 'Sort results'}
        aria-labelledby={showLabel ? labelId : undefined}
      >
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
  );

  if (!showLabel) return select;

  return (
    <div className="body-sm flex items-center gap-2 text-muted-foreground">
      <span id={labelId}>Sort</span>
      {select}
    </div>
  );
});
