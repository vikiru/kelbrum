import {
  ArrowDown01,
  ArrowDownAZ,
  ArrowDownWideNarrow,
  ArrowUp01,
  ArrowUpAZ,
  ArrowUpWideNarrow,
  SlidersHorizontal,
} from 'lucide-react';
import { useId } from 'react';

import type { SearchSort } from '@/features/search/model/search-types';

import { ANIME_TYPES } from '@/entities/anime/model/anime-constants';
import { formatFilterValue } from '@/features/search/lib/search-filter-formatting';
import {
  FILTER_EPISODES_MAX,
  FILTER_EPISODES_MIN,
  FILTER_SCORE_MAX,
  FILTER_SCORE_MIN,
  FILTER_YEAR_MAX,
  FILTER_YEAR_MIN,
} from '@/features/search/lib/search-filter-index';
import { Button } from '@/shared/components/ui/button';
import { Combobox, ComboboxContent, ComboboxInput, ComboboxItem, ComboboxList } from '@/shared/components/ui/combobox';
import { Field, FieldLabel } from '@/shared/components/ui/field';
import { Input } from '@/shared/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/components/ui/select';
import { Separator } from '@/shared/components/ui/separator';
import { Slider } from '@/shared/components/ui/slider';

export interface SearchFiltersProps {
  typeFilter: string;
  ratingFilter: string;
  demographicFilter: string;
  genreFilters: string[];
  themeFilters: string[];
  scoreRange: [number, number];
  yearRange: [string, string];
  episodeRange: [string, string];
  onReset: () => void;
  onTypeChange: (value: string) => void;
  onRatingChange: (value: string) => void;
  onDemographicChange: (value: string) => void;
  onGenresChange: (values: string[]) => void;
  onThemesChange: (values: string[]) => void;
  onScoreChange: (values: [number, number]) => void;
  onYearChange: (values: [string, string]) => void;
  onEpisodesChange: (values: [string, string]) => void;
}

export interface SearchFilterOptions {
  genres: readonly string[];
  themes: readonly string[];
  demographics: readonly string[];
}

export function SearchFilters({ options, ...props }: SearchFiltersProps & { options: SearchFilterOptions }) {
  return (
    <section aria-labelledby="search-filters-heading" className="flex flex-col gap-7">
      <div className="flex items-start gap-4">
        <div className="flex min-w-0 flex-1 items-start gap-3">
          <SlidersHorizontal className="icon-md mt-0.5 text-muted-foreground" aria-hidden="true" />
          <div>
            <h2 id="search-filters-heading" className="body-copy font-semibold">
              Filters
            </h2>
            <p className="body-sm mt-1 text-muted-foreground">Refine by type, rating, ranges, genres, or themes.</p>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={props.onReset}>
          Reset
        </Button>
      </div>
      <div className="flex flex-col gap-6">
        <FilterField
          label="Type"
          value={props.typeFilter}
          onChange={props.onTypeChange}
          options={['all', ANIME_TYPES.TV, ANIME_TYPES.MOVIE, ANIME_TYPES.ONA]}
        />
        <FilterField
          label="Rating"
          value={props.ratingFilter}
          onChange={props.onRatingChange}
          options={['all', 'G', 'PG', 'PG-13', 'R', 'R+']}
        />
        <FilterField
          label="Demographics"
          value={props.demographicFilter}
          onChange={props.onDemographicChange}
          options={['all', ...options.demographics]}
        />
      </div>
      <Separator />
      <div className="flex flex-col gap-6">
        <Field>
          <span className="font-heading text-sm font-medium">Score</span>
          <div className="flex flex-col gap-3">
            <div className="body-sm flex justify-between text-muted-foreground">
              <span>{props.scoreRange[0].toFixed(1)}</span>
              <span>{props.scoreRange[1].toFixed(1)}</span>
            </div>
            <Slider
              aria-label="Score range"
              value={props.scoreRange}
              min={FILTER_SCORE_MIN}
              max={FILTER_SCORE_MAX}
              step={0.1}
              onValueChange={(value) => {
                if (Array.isArray(value) && value.length === 2) props.onScoreChange([value[0], value[1]]);
              }}
            />
          </div>
        </Field>
        <div className="flex flex-col gap-2">
          <span className="font-heading text-sm font-medium">Year</span>
          <RangeInputs
            label="Year"
            values={props.yearRange}
            min={FILTER_YEAR_MIN}
            max={FILTER_YEAR_MAX}
            onChange={props.onYearChange}
          />
        </div>
        <div className="flex flex-col gap-2">
          <span className="font-heading text-sm font-medium">Episodes</span>
          <RangeInputs
            label="Episodes"
            values={props.episodeRange}
            min={FILTER_EPISODES_MIN}
            max={FILTER_EPISODES_MAX}
            onChange={props.onEpisodesChange}
          />
        </div>
      </div>
      <Separator />
      <div className="flex flex-col gap-6">
        <TaxonomyField
          label="Genres"
          options={options.genres}
          value={props.genreFilters}
          onChange={props.onGenresChange}
        />
        <TaxonomyField
          label="Themes"
          options={options.themes}
          value={props.themeFilters}
          onChange={props.onThemesChange}
        />
      </div>
    </section>
  );
}

export function SortSelect({ value, onChange }: { value: SearchSort; onChange: (value: SearchSort) => void }) {
  return (
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
      <SelectTrigger className="h-11 min-w-44" aria-label="Sort results">
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
}

function FilterField({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: readonly string[];
}) {
  return (
    <Field>
      <FieldLabel>{label}</FieldLabel>
      <Select
        value={value}
        onValueChange={(nextValue) => {
          if (nextValue) onChange(nextValue);
        }}
      >
        <SelectTrigger className="h-10 w-full">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option} value={option}>
              {option === 'all' ? 'Any' : formatFilterValue(option)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </Field>
  );
}

function RangeInputs({
  label,
  values,
  min,
  max,
  onChange,
}: {
  label: string;
  values: [string, string];
  min: number;
  max: number;
  onChange: (values: [string, string]) => void;
}) {
  const inputId = useId();

  return (
    <div className="grid grid-cols-2 gap-2">
      <Input
        id={`${inputId}-minimum`}
        type="number"
        placeholder="From"
        min={min}
        max={max}
        value={values[0]}
        onChange={(event) => onChange([event.target.value, values[1]])}
        aria-label={`${label} minimum`}
      />
      <Input
        id={`${inputId}-maximum`}
        type="number"
        placeholder="To"
        min={min}
        max={max}
        value={values[1]}
        onChange={(event) => onChange([values[0], event.target.value])}
        aria-label={`${label} maximum`}
      />
    </div>
  );
}

function TaxonomyField({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: readonly string[];
  value: string[];
  onChange: (values: string[]) => void;
}) {
  return (
    <Field>
      <FieldLabel>{label}</FieldLabel>
      <Combobox
        multiple
        value={value}
        onValueChange={(nextValue) => {
          if (Array.isArray(nextValue)) onChange(nextValue);
        }}
      >
        <ComboboxInput showTrigger={false} placeholder={`Search ${label.toLowerCase()}`} />
        <ComboboxContent>
          <ComboboxList>
            {options.map((option) => (
              <ComboboxItem key={option} value={option}>
                {formatFilterValue(option)}
              </ComboboxItem>
            ))}
          </ComboboxList>
        </ComboboxContent>
      </Combobox>
    </Field>
  );
}
