import type { DocumentOptions, DocumentData } from 'flexsearch';

export interface AnimeSearchHit extends DocumentData {
  id: string;
  text: string;
}

export const SEARCH_INDEX_VERSION = 1;

export function normalizeSearchText(value: string): string {
  return value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}

export const searchIndexOptions = {
  tokenize: 'forward',
  document: {
    id: 'id',
    index: ['text'],
    store: ['id', 'text'],
  },
} satisfies DocumentOptions<AnimeSearchHit>;
