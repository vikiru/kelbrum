export const ANIME_TYPES = {
  TV: 'TV',
  MOVIE: 'MOVIE',
  ONA: 'ONA',
} as const;

export type AnimeType = (typeof ANIME_TYPES)[keyof typeof ANIME_TYPES];
