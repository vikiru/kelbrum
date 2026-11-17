import filterIndexData from '@/data/filter-index.json';
import { AnimeFilterIndexSchema } from '@/entities/anime/model/anime-schema';
import {
  formatIndexRatingKey,
  formatIndexTaxonomyKey,
  formatIndexTypeKey,
} from '@/features/search/lib/search-filter-formatting';

const filterIndex = AnimeFilterIndexSchema.parse(filterIndexData);
const filterIndexPositionById = new Map(filterIndex.ids.map((id, index) => [id, index]));

const FILTER_SCORE_MIN = 0;
const FILTER_SCORE_MAX = 10;
const FILTER_YEAR_MIN = 1917;
const FILTER_YEAR_MAX = 2026;
const FILTER_EPISODES_MIN = 1;
const FILTER_EPISODES_MAX = 3000;

export {
  FILTER_EPISODES_MAX,
  FILTER_EPISODES_MIN,
  FILTER_SCORE_MAX,
  FILTER_SCORE_MIN,
  FILTER_YEAR_MAX,
  FILTER_YEAR_MIN,
};

export interface NumericFilterRange {
  field: 'score' | 'year' | 'episodes';
  minimum: number;
  maximum: number;
  enabled: boolean;
}

function parseNumericBound(raw: string, fallback: number): number {
  const trimmed = raw.trim();
  if (!trimmed) return fallback;
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : fallback;
}

export function resolveNumericFilterRanges(
  scoreRange: readonly [number, number],
  yearRange: readonly [string, string],
  episodeRange: readonly [string, string],
): readonly [NumericFilterRange, NumericFilterRange, NumericFilterRange] {
  return [
    {
      field: 'score',
      minimum: scoreRange[0],
      maximum: scoreRange[1],
      enabled: scoreRange[0] !== FILTER_SCORE_MIN || scoreRange[1] !== FILTER_SCORE_MAX,
    },
    {
      field: 'year',
      minimum: parseNumericBound(yearRange[0], 0),
      maximum: parseNumericBound(yearRange[1], Number.POSITIVE_INFINITY),
      enabled: yearRange.some((bound) => bound.trim().length > 0),
    },
    {
      field: 'episodes',
      minimum: parseNumericBound(episodeRange[0], 0),
      maximum: parseNumericBound(episodeRange[1], Number.POSITIVE_INFINITY),
      enabled: episodeRange.some((bound) => bound.trim().length > 0),
    },
  ];
}

export function matchesNumericRange(value: number | null, minimum: number, maximum: number, enabled: boolean): boolean {
  if (!enabled) return true;
  return value !== null && value >= minimum && value <= maximum;
}

export function getIndexedFilterIds(
  type: string,
  rating: string,
  demographic: string,
  genres: readonly string[],
  themes: readonly string[],
  scoreRange: readonly [number, number],
  yearRange: readonly [string, string],
  episodeRange: readonly [string, string],
): Set<number> {
  let ids = new Set(filterIndex.ids);
  const categories: Array<[string, string]> = [];
  if (type !== 'all') categories.push(['anime_type', formatIndexTypeKey(type)]);
  if (rating !== 'all') categories.push(['rating', formatIndexRatingKey(rating)]);
  if (demographic !== 'all') categories.push(['demographic', formatIndexTaxonomyKey(demographic)]);
  genres.forEach((genre) => categories.push(['genre', formatIndexTaxonomyKey(genre)]));
  themes.forEach((theme) => categories.push(['theme', formatIndexTaxonomyKey(theme)]));

  for (const [field, value] of categories) {
    const postings = filterIndex.categorical[field]?.[value];
    if (postings === undefined) return new Set();
    ids = intersectIds(ids, postings);
  }

  for (const { field, minimum, maximum, enabled } of resolveNumericFilterRanges(scoreRange, yearRange, episodeRange)) {
    if (!enabled) continue;
    const values = filterIndex.numeric[field];
    if (!values) continue;
    ids = new Set(
      [...ids].filter((id) => {
        const index = filterIndexPositionById.get(id);
        if (index === undefined) return false;
        return matchesNumericRange(values[index] ?? null, minimum, maximum, enabled);
      }),
    );
  }
  return ids;
}

export function intersectIds(currentIds: Set<number>, ids: Iterable<number>): Set<number> {
  const intersection = new Set<number>();
  for (const id of ids) {
    if (currentIds.has(id)) intersection.add(id);
  }
  return intersection;
}
