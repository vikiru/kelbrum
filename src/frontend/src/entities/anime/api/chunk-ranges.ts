export interface AnimeChunkRange {
  start: number;
  end: number;
}

export function getAnimeChunkRange(animeId: number, width = 1_000): AnimeChunkRange {
  if (!Number.isInteger(animeId) || animeId < 1 || !Number.isInteger(width) || width < 1) {
    throw new Error('Anime ID and chunk width must be positive integers');
  }
  const start = Math.floor((animeId - 1) / width) * width + 1;
  return { start, end: start + width - 1 };
}

export function getAnimeChunkFilename(kind: 'metadata' | 'full', range: AnimeChunkRange): string {
  return `${kind}-${range.start}-${range.end}.json`;
}

export function parseAnimeChunkFilename(filename: string): AnimeChunkRange | null {
  const match = /^(?:metadata|full)-(\d+)-(\d+)\.json$/.exec(filename);
  if (!match) return null;
  const start = Number(match[1]);
  const end = Number(match[2]);
  return Number.isInteger(start) && Number.isInteger(end) && start > 0 && end >= start ? { start, end } : null;
}
