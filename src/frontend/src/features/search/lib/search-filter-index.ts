import filterIndexData from '@/data/filter-index.json';
import { AnimeFilterIndexSchema } from '@/entities/anime/model/anime-schema';
import { formatFilterValue } from '@/features/search/lib/search-filter-formatting';

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
  if (type !== 'all') categories.push(['anime_type', type.toUpperCase()]);
  if (rating !== 'all') categories.push(['rating', rating.toUpperCase()]);
  if (demographic !== 'all') categories.push(['demographic', formatFilterValue(demographic)]);
  genres.forEach((genre) => categories.push(['genre', formatFilterValue(genre)]));
  themes.forEach((theme) => categories.push(['theme', formatFilterValue(theme)]));
  for (const [field, value] of categories) {
    const postings = filterIndex.categorical[field]?.[value];
    if (postings) ids = intersectIds(ids, postings);
  }
  for (const [field, minimum, maximum, enabled] of [
    ['score', scoreRange[0], scoreRange[1], scoreRange[0] !== 0 || scoreRange[1] !== 10],
    ['year', Number(yearRange[0]) || 0, Number(yearRange[1]) || Number.POSITIVE_INFINITY, yearRange.some(Boolean)],
    [
      'episodes',
      Number(episodeRange[0]) || 0,
      Number(episodeRange[1]) || Number.POSITIVE_INFINITY,
      episodeRange.some(Boolean),
    ],
  ] as const) {
    if (!enabled) continue;
    const values = filterIndex.numeric[field];
    if (!values) continue;
    ids = new Set(
      [...ids].filter((id) => {
        const index = filterIndexPositionById.get(id);
        if (index === undefined) return false;
        const value = values[index];
        return value !== null && value >= minimum && value <= maximum;
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
