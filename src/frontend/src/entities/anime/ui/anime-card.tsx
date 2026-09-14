import { Link } from '@tanstack/react-router';
import { Star } from 'lucide-react';
import { memo } from 'react';

import type { AnimeCardItem } from '@/entities/anime/model/anime-schema';

import { AnimeImage } from '@/entities/anime/ui/anime-image';
import { Card, CardContent } from '@/shared/components/ui/card';
import { slugify } from '@/shared/lib/slugify';

export interface AnimeCardProps {
  item: AnimeCardItem;
  rank?: number;
}

export const AnimeCard = memo(function AnimeCard({ item, rank }: AnimeCardProps) {
  const title = item.titleEnglish?.trim() || item.title;
  const displayTitle = truncateAnimeTitle(title);
  const slug = slugify(title);

  return (
    <Card className="group h-full overflow-hidden p-0">
      <Link className="flex h-full min-w-0 flex-col" to="/anime/$id/$slug" params={{ id: String(item.malId), slug }}>
        <div className="relative aspect-[2/3] overflow-hidden">
          <AnimeImage
            images={item.images}
            alt={`${title} poster`}
            sizes="(max-width: 640px) 50vw, (max-width: 1280px) 33vw, 300px"
            className="block h-full w-full object-cover"
          />
          {rank !== undefined && (
            <span className="body-sm absolute top-3 left-3 rounded-md bg-background/90 px-2 py-1 font-medium shadow-sm">
              #{rank}
            </span>
          )}
        </div>
        <CardContent className="flex min-w-0 flex-1 flex-col px-3 py-4">
          <h2
            className="min-h-[3rem] min-w-0 font-heading text-sm leading-snug font-semibold wrap-break-word transition-colors group-hover:text-muted-foreground motion-reduce:transition-none"
            title={title}
          >
            {displayTitle}
          </h2>
          <div className="body-sm mt-auto flex items-center justify-between pt-2 text-muted-foreground">
            <span className="flex items-center gap-1 text-foreground">
              <Star className="icon-xs fill-current text-primary" aria-hidden="true" />
              {formatAnimeScore(item.score)}
            </span>
            {item.year !== null && <span>{item.year}</span>}
          </div>
        </CardContent>
      </Link>
    </Card>
  );
});

function truncateAnimeTitle(title: string, maxLength = 56): string {
  if (title.length <= maxLength) return title;

  const truncatedTitle = title.slice(0, maxLength - 1).trimEnd();
  const lastSpace = truncatedTitle.lastIndexOf(' ');
  return `${truncatedTitle.slice(0, lastSpace > 0 ? lastSpace : truncatedTitle.length)}…`;
}

function formatAnimeScore(score: number): string {
  return score.toFixed(2).replace(/\.?(0+)$/, '');
}
