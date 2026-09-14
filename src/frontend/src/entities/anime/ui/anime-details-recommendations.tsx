import { Link } from '@tanstack/react-router';
import { ArrowUpRight, LoaderCircle } from 'lucide-react';

import type { AnimeCardItem } from '@/entities/anime/model/anime-schema';

import { AnimeCard } from '@/entities/anime/ui/anime-card';
import { Button } from '@/shared/components/ui/button';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/shared/components/ui/carousel';

interface AnimeDetailsRecommendationsProps {
  animeId: string;
  slug: string;
  items: AnimeCardItem[];
  totalCount: number;
  isLoading: boolean;
  isError: boolean;
}

export function AnimeDetailsRecommendations({
  animeId,
  slug,
  items,
  totalCount,
  isLoading,
  isError,
}: AnimeDetailsRecommendationsProps) {
  return (
    <section aria-labelledby="anime-recommendations-heading">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h2 id="anime-recommendations-heading" className="heading-h4">
            Recommendations
          </h2>
          <p className="body-copy mt-2 max-w-2xl text-muted-foreground">
            If this one worked for you, these are worth putting next on your list.
          </p>
        </div>
        {totalCount > 10 && (
          <Button
            nativeButton={false}
            render={<Link to="/anime/$id/$slug/recommendations" params={{ id: animeId, slug }} />}
            variant="secondary"
            size="lg"
            className="min-h-11 cursor-pointer px-5"
          >
            Browse all recommendations
            <ArrowUpRight
              className="icon-sm transition-transform duration-200 group-hover/button:translate-x-0.5 group-hover/button:-translate-y-0.5 motion-reduce:transition-none"
              aria-hidden="true"
            />
          </Button>
        )}
      </div>
      <Carousel className="mt-6 px-12" opts={{ align: 'start', loop: false }}>
        <CarouselContent className="-ml-3" aria-label="Recommended anime">
          {isLoading ? (
            <CarouselItem className="basis-full pl-3">
              <div className="flex min-h-48 items-center justify-center rounded-xl border border-dashed">
                <LoaderCircle
                  className="size-5 animate-spin text-muted-foreground"
                  aria-label="Loading recommendations"
                />
              </div>
            </CarouselItem>
          ) : isError ? (
            <CarouselItem className="basis-full pl-3">
              <div className="body-copy flex min-h-48 items-center justify-center rounded-xl border border-dashed p-6 text-center text-muted-foreground">
                Recommendations could not be loaded.
              </div>
            </CarouselItem>
          ) : (
            items.map((item) => (
              <CarouselItem key={item.malId} className="basis-full pl-3 min-[480px]:basis-1/2 md:basis-1/3">
                <AnimeCard item={item} />
              </CarouselItem>
            ))
          )}
        </CarouselContent>
        <CarouselPrevious className="left-0 hidden min-h-11 min-w-11 sm:flex" aria-label="Previous recommendations" />
        <CarouselNext className="right-0 hidden min-h-11 min-w-11 sm:flex" aria-label="Next recommendations" />
      </Carousel>
    </section>
  );
}
