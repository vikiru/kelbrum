import { Link } from '@tanstack/react-router';
import { ChevronRight, ExternalLink, Star } from 'lucide-react';
import { SiMyanimelist, SiYoutube } from 'react-icons/si';

import type { AnimeImages } from '@/entities/anime/model/anime-schema';

import { formatTaxonomyLabel, type AnimePageModel } from '@/entities/anime/model/anime-details-model';
import { AnimeImage } from '@/entities/anime/ui/anime-image';
import { Badge } from '@/shared/components/ui/badge';

export interface AnimeDetailsHeroProps {
  anime: AnimePageModel;
  images: AnimeImages | null;
  trailerUrl: string | null;
  malUrl: string | null;
  animeId: number;
}

export function AnimeDetailsHero({ anime, images, trailerUrl, malUrl, animeId }: AnimeDetailsHeroProps) {
  const taxonomy = [...new Set([...anime.genres, ...anime.themes].map(formatTaxonomyLabel))];

  return (
    <>
      <nav aria-label="Breadcrumb" className="body-copy mb-8 flex min-w-0 items-center gap-2 text-muted-foreground">
        <Link
          to="/"
          className="shrink-0 transition-colors duration-200 hover:text-foreground motion-reduce:transition-none"
        >
          Home
        </Link>
        <ChevronRight className="size-4" aria-hidden="true" />
        <span className="truncate text-foreground" aria-current="page">
          {anime.englishTitle}
        </span>
      </nav>

      <section
        aria-labelledby="anime-title"
        className="grid gap-8 md:grid-cols-[minmax(0,1.35fr)_320px] md:items-start md:gap-12 xl:grid-cols-[minmax(0,1fr)_400px] xl:gap-8"
      >
        <div className="order-2 min-w-0 md:order-1">
          <div className="body-copy flex flex-wrap items-center gap-x-3 gap-y-2 text-muted-foreground">
            <span className="font-medium text-foreground">{anime.type}</span>
            <span aria-hidden="true">·</span>
            <span>{anime.status}</span>
            <span aria-hidden="true">·</span>
            <span className="flex items-center gap-1.5 font-medium text-foreground">
              <Star className="icon-sm fill-current text-primary" aria-hidden="true" />
              {anime.score}
            </span>
          </div>
          <h1 id="anime-title" className="heading-h2 mt-4 max-w-full">
            {anime.englishTitle}
          </h1>
          <p className="body-copy mt-3 text-muted-foreground">
            {anime.title}
            {anime.japaneseTitle && (
              <>
                <span aria-hidden="true"> · </span>
                {anime.japaneseTitle}
              </>
            )}
          </p>
          <p className="body-copy mt-7 max-w-3xl text-foreground/80">{anime.synopsis}</p>
          {taxonomy.length > 0 && (
            <div className="mt-6 flex max-w-full flex-wrap items-center gap-2" aria-label="Genres and themes">
              {taxonomy.map((value) => (
                <Badge
                  key={value}
                  variant="outline"
                  className="max-w-full rounded-md px-3.5 py-3 text-sm leading-tight font-medium"
                >
                  {value}
                </Badge>
              ))}
            </div>
          )}
          <div className="mt-8 flex flex-wrap gap-3">
            {trailerUrl && (
              <a
                href={trailerUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex h-11 w-36 items-center justify-center gap-2 rounded-md bg-foreground px-4 text-sm font-medium text-background transition-[background-color,color] duration-200 hover:bg-foreground/85 motion-reduce:transition-none"
              >
                <SiYoutube className="icon-sm shrink-0" aria-hidden="true" /> Trailer{' '}
                <ExternalLink className="icon-xs shrink-0" aria-hidden="true" />
              </a>
            )}
            <a
              href={malUrl ?? `https://myanimelist.net/anime/${animeId}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-11 w-44 items-center justify-center gap-2 rounded-md border border-border px-4 text-sm font-medium text-foreground transition-[background-color,border-color,color] duration-200 hover:border-foreground/20 hover:bg-muted/40 motion-reduce:transition-none"
            >
              <SiMyanimelist className="size-5 shrink-0" aria-hidden="true" /> MyAnimeList{' '}
              <ExternalLink className="icon-xs shrink-0" aria-hidden="true" />
            </a>
          </div>
        </div>
        <div className="order-1 -mx-4 aspect-[2/3] w-[calc(100%+2rem)] max-w-none min-[480px]:mx-auto min-[480px]:w-full min-[480px]:max-w-[36rem] md:order-2 md:mx-0 md:max-w-[320px] xl:max-w-[400px]">
          <div className="h-full overflow-hidden rounded-none bg-muted ring-1 ring-foreground/10 md:aspect-[2/3] md:rounded-xl">
            <AnimeImage
              images={images}
              alt={`${anime.englishTitle} poster`}
              sizes="(max-width: 1024px) 100vw, 300px"
              loading="eager"
              fetchPriority="high"
              className="h-full w-full object-cover"
            />
          </div>
        </div>
      </section>
    </>
  );
}
