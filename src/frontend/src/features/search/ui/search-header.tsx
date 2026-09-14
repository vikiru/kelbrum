import type { ReactNode } from 'react';

import { Link } from '@tanstack/react-router';
import { Search as SearchIcon, X } from 'lucide-react';

import type { AnimeCardItem } from '@/entities/anime/model/anime-schema';

import { InputGroup, InputGroupAddon, InputGroupInput } from '@/shared/components/ui/input-group';
import { ScrollArea } from '@/shared/components/ui/scroll-area';
import { deduplicateAnimeTitles } from '@/shared/lib/anime-title-deduplication';
import { slugify } from '@/shared/lib/slugify';

interface SearchHeaderProps {
  query: string;
  suggestions: readonly AnimeCardItem[];
  activeSuggestionIndex: number;
  onQueryChange: (query: string) => void;
  onActiveSuggestionChange: (index: number) => void;
  onMoveSuggestion: (direction: 1 | -1) => void;
  onSelectSuggestion: (index: number) => void;
  onResetActiveSuggestion: () => void;
  actions?: ReactNode;
}

export function SearchHeader({
  query,
  suggestions,
  activeSuggestionIndex,
  onQueryChange,
  onActiveSuggestionChange,
  onMoveSuggestion,
  onSelectSuggestion,
  onResetActiveSuggestion,
  actions,
}: SearchHeaderProps) {
  return (
    <header className="mx-auto max-w-3xl text-center">
      <h1 className="heading-h3">Find your next anime</h1>
      <p className="body-copy mt-4 text-muted-foreground">
        Search by title or browse the catalogue using filters to find something you want to watch.
      </p>
      <div className="relative mt-8">
        <div className="flex items-start gap-3">
          <div className="relative min-w-0 flex-1">
            <SearchIcon
              className="icon-md absolute top-1/2 left-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden="true"
            />
            <InputGroup className="h-14 rounded-xl border-0 shadow-sm">
              <InputGroupInput
                value={query}
                role="combobox"
                aria-autocomplete="list"
                aria-controls="search-suggestions"
                aria-expanded={suggestions.length > 0}
                aria-activedescendant={
                  suggestions[activeSuggestionIndex]
                    ? `search-suggestion-${suggestions[activeSuggestionIndex].malId}`
                    : undefined
                }
                onChange={(event) => {
                  onQueryChange(event.target.value);
                  onResetActiveSuggestion();
                }}
                onKeyDown={(event) => {
                  if (!suggestions.length) return;
                  if (event.key === 'ArrowDown') {
                    event.preventDefault();
                    onMoveSuggestion(1);
                  } else if (event.key === 'ArrowUp') {
                    event.preventDefault();
                    onMoveSuggestion(-1);
                  } else if (event.key === 'Enter') {
                    event.preventDefault();
                    onSelectSuggestion(activeSuggestionIndex);
                  } else if (event.key === 'Escape') {
                    onQueryChange('');
                  }
                }}
                placeholder="Search titles and alternative titles"
                aria-label="Search anime titles"
                className="h-14 pl-11 text-base"
              />
              {query && (
                <InputGroupAddon
                  align="inline-end"
                  onClick={() => {
                    onQueryChange('');
                    onResetActiveSuggestion();
                  }}
                  aria-label="Clear search"
                  className="h-14 cursor-pointer bg-transparent px-3 transition-[background-color,color] hover:bg-muted/60 hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none motion-reduce:transition-none"
                >
                  <X className="icon-sm" aria-hidden="true" />
                  <span className="sr-only">Clear search</span>
                </InputGroupAddon>
              )}
            </InputGroup>
            {suggestions.length > 0 && (
              <SearchSuggestions
                items={suggestions}
                activeIndex={activeSuggestionIndex}
                onActiveChange={onActiveSuggestionChange}
              />
            )}
          </div>
          {actions && <div className="self-start lg:hidden">{actions}</div>}
        </div>
      </div>
    </header>
  );
}

interface SearchSuggestionsProps {
  items: readonly AnimeCardItem[];
  activeIndex: number;
  onActiveChange: (index: number) => void;
}

function SearchSuggestions({ items, activeIndex, onActiveChange }: SearchSuggestionsProps) {
  return (
    <ScrollArea
      id="search-suggestions"
      role="listbox"
      aria-label="Search suggestions"
      className="absolute top-full right-0 left-0 z-50 mt-2 h-80 overflow-hidden rounded-xl border bg-popover p-1 text-popover-foreground shadow-lg"
    >
      {items.map((item, index) => {
        const title = item.titleEnglish?.trim() || item.title;
        const alternateTitles = deduplicateAnimeTitles([item.title, item.titleEnglish, item.titleJapanese]).filter(
          (value) => value !== title,
        );
        return (
          <Link
            key={item.malId}
            id={`search-suggestion-${item.malId}`}
            role="option"
            aria-selected={index === activeIndex}
            to="/anime/$id/$slug"
            params={{ id: String(item.malId), slug: slugify(title) }}
            onMouseEnter={() => onActiveChange(index)}
            className={`flex min-h-10 items-center justify-between gap-4 rounded-lg px-3 py-1.5 text-left text-sm transition-none hover:bg-muted focus-visible:bg-muted focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none ${index === activeIndex ? 'bg-muted' : ''}`}
          >
            <span className="min-w-0 truncate text-sm font-medium">
              {title}
              {alternateTitles.length > 0 && (
                <span className="ml-2 font-normal text-muted-foreground">{alternateTitles.join(' · ')}</span>
              )}
            </span>
            <span className="shrink-0 text-xs text-muted-foreground">{item.year ?? '—'}</span>
          </Link>
        );
      })}
    </ScrollArea>
  );
}
