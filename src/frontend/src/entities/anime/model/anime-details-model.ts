import type { AnimeEntry } from '@/entities/anime/model/anime-schema';

import { ANIME_TYPES } from '@/entities/anime/model/anime-constants';

export interface AnimePageModel {
  title: string;
  englishTitle: string;
  japaneseTitle: string;
  synopsis: string;
  score: number;
  year: number;
  status: string;
  type: string;
  episodes: number;
  duration: string;
  source: string;
  rating: string;
  season: string;
  genres: string[];
  themes: string[];
  demographics: string[];
  studios: string[];
}

export interface AnimeDetailField {
  label: string;
  value: string;
}

export function getPreferredAnimeTitle(entry: Pick<AnimeEntry, 'title' | 'title_english'>): string {
  const titles = [entry.title, entry.title_english?.trim()].filter((title): title is string => Boolean(title));
  return titles.toSorted((a, b) => a.length - b.length)[0] ?? entry.title;
}

export function createAnimePageModel(entry: AnimeEntry): AnimePageModel {
  return {
    title: entry.title,
    englishTitle: entry.title_english ?? entry.title,
    japaneseTitle: entry.title_japanese ?? '',
    synopsis: entry.synopsis ?? 'No synopsis is available for this title yet.',
    score: entry.score ?? 0,
    year: entry.year ?? 0,
    status: entry.status ?? 'Unknown status',
    type: entry.type ?? 'Unknown format',
    episodes: entry.episodes ?? 0,
    duration: entry.duration ?? 'Unknown duration',
    source: entry.source ?? 'Unknown source',
    rating: entry.rating ?? 'Unrated',
    season: formatSeason(entry.season),
    genres: entry.genres.map((item) => item.name),
    themes: entry.themes.map((item) => item.name),
    demographics: entry.demographics.map((item) => item.name),
    studios: entry.studios.map((item) => item.name),
  };
}

export function formatAnimeType(type: string, episodes: number): string {
  return type.toUpperCase() === ANIME_TYPES.MOVIE || episodes <= 0 ? type : `${type} · ${episodes} episodes`;
}

export function formatTaxonomyLabel(value: string): string {
  return value.replaceAll('_', ' ').replace(/\b\w/g, (character) => character.toUpperCase());
}

export function createAnimeDetailFields(anime: AnimePageModel): AnimeDetailField[] {
  return [
    anime.season && { label: 'Season', value: anime.season },
    anime.year > 0 && { label: 'Year', value: String(anime.year) },
    { label: 'Format', value: formatAnimeType(anime.type, anime.episodes) },
    anime.duration && { label: 'Duration', value: anime.duration },
    anime.demographics.length > 0 && {
      label: 'Demographics',
      value: anime.demographics.map(formatTaxonomyLabel).join(', '),
    },
    anime.rating && { label: 'Rating', value: anime.rating },
    anime.source && { label: 'Source', value: anime.source },
    anime.studios.length > 0 && { label: 'Studio', value: anime.studios.join(', ') },
  ].filter((detail): detail is AnimeDetailField => Boolean(detail));
}

function formatSeason(season: string | null): string {
  if (!season) return '';
  return season.charAt(0).toUpperCase() + season.slice(1).toLowerCase();
}
