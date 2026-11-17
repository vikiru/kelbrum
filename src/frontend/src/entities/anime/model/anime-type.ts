export const ANIME_TYPES = ['TV', 'MOVIE', 'ONA'] as const;

export type AnimeType = (typeof ANIME_TYPES)[number];

export const ANIME_TYPE_LABELS: Record<AnimeType, string> = {
  TV: 'TV',
  MOVIE: 'Movie',
  ONA: 'ONA',
};

const ANIME_TYPE_BY_UPPER: Record<string, AnimeType> = {
  TV: 'TV',
  MOVIE: 'MOVIE',
  ONA: 'ONA',
};

export function normalizeAnimeType(value: string): AnimeType | null {
  return ANIME_TYPE_BY_UPPER[value.trim().toUpperCase()] ?? null;
}
