import { ANIME_TYPE_LABELS } from '@/entities/anime/model/anime-type';
import { ANIME_GENRE_LABELS } from '@/entities/anime/model/genres';
import { ANIME_THEME_LABELS } from '@/entities/anime/model/themes';

const DISPLAY_FILTER_LABELS: Record<string, string> = {
  ...ANIME_GENRE_LABELS,
  ...ANIME_THEME_LABELS,
  ...ANIME_TYPE_LABELS,
};

const INDEX_CATEGORY_LABELS: Record<string, string> = {
  ...ANIME_GENRE_LABELS,
  ...ANIME_THEME_LABELS,
};

const RATING_FILTER_KEYS: Record<string, string> = {
  G: 'G',
  PG: 'PG',
  'PG-13': 'PG-13',
  R: 'R',
  'R+': 'R+',
  RX: 'Rx',
  UNKNOWN: 'Unknown',
};

export function formatFilterValue(value: string): string {
  return (
    DISPLAY_FILTER_LABELS[value] ?? value.replaceAll('_', ' ').replace(/\b\w/g, (character) => character.toUpperCase())
  );
}

export function formatIndexTypeKey(value: string): string {
  return value.trim().toUpperCase();
}

export function formatIndexRatingKey(value: string): string {
  return RATING_FILTER_KEYS[value.trim().toUpperCase()] ?? value;
}

export function formatIndexTaxonomyKey(value: string): string {
  return (
    INDEX_CATEGORY_LABELS[value] ?? value.replaceAll('_', ' ').replace(/\b\w/g, (character) => character.toUpperCase())
  );
}
