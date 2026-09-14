import { Link } from '@tanstack/react-router';
import { ArrowRight } from 'lucide-react';

import homepage from '@/data/homepage.json';
import { AnimeCardItemsSchema, type AnimeCardItem } from '@/entities/anime/model/anime-schema';
import { AnimeCard } from '@/entities/anime/ui/anime-card';
import { AnimeImage } from '@/entities/anime/ui/anime-image';
import { Navbar } from '@/shared/components/navbar';
import { PageContainer } from '@/shared/components/page-container';
import { Button } from '@/shared/components/ui/button';
import { slugify } from '@/shared/lib/slugify';

const animeEntries = AnimeCardItemsSchema.parse(homepage);
const highRatedAnime = animeEntries.filter((item) => item.score >= 8);

export function HomePage() {
  const featuredRecommendations = highRatedAnime.slice(0, 10);

  return (
    <main id="main-content" className="min-h-screen bg-background text-foreground">
      <Navbar />
      <section className="border-b bg-muted/30" aria-labelledby="home-hero-heading">
        <PageContainer className="grid gap-10 py-16 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:py-28">
          <div>
            <h1 id="home-hero-heading" className="heading-h1 max-w-3xl text-balance">
              Discover your next favourite anime
            </h1>
            <p className="body-copy mt-6 max-w-2xl text-muted-foreground">
              Tired of searching for something that fits? Start with a title you already love, explore a recommendation,
              or shape the catalogue around your taste.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button
                nativeButton={false}
                render={<Link to="/search" />}
                size="lg"
                className="min-h-11 w-full px-5 hover:bg-primary/90 sm:w-auto"
              >
                Search anime <ArrowRight data-icon="inline-end" />
              </Button>
              <Button
                nativeButton={false}
                render={<Link to="/top" />}
                variant="outline"
                size="lg"
                className="min-h-11 w-full border-border px-5 transition-[background-color,border-color,color] duration-200 hover:border-foreground/20 hover:bg-muted/40 motion-reduce:transition-none sm:w-auto"
              >
                View Top 100
              </Button>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="grid grid-cols-3 items-end gap-3 sm:gap-5">
              {animeEntries.slice(0, 3).map((item, index) => (
                <Poster key={item.malId} item={item} featured={index === 1} />
              ))}
            </div>
          </div>
        </PageContainer>
      </section>
      <section className="py-14 lg:py-20" aria-labelledby="home-recommendations-heading">
        <PageContainer>
          <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 id="home-recommendations-heading" className="heading-h4 text-balance">
                Not sure where to start?
              </h2>
              <p className="body-copy mt-2 text-muted-foreground">
                Here are a few highly rated anime worth checking out.
              </p>
            </div>
            <Button
              nativeButton={false}
              render={<Link to="/search" />}
              variant="ghost"
              size="lg"
              className="min-h-11 cursor-pointer px-5"
            >
              Explore more <ArrowRight data-icon="inline-end" />
            </Button>
          </div>
          <ul className="anime-card-grid below-fold-content mt-8 gap-4">
            {featuredRecommendations.map((item) => (
              <li key={item.malId}>
                <AnimeCard item={item} />
              </li>
            ))}
          </ul>
        </PageContainer>
      </section>
    </main>
  );
}

function Poster({ item, featured }: { item: AnimeCardItem; featured: boolean }) {
  const title = item.titleEnglish ?? item.title;
  return (
    <Link
      to="/anime/$id/$slug"
      params={{ id: String(item.malId), slug: slugify(title) }}
      aria-label={`View details for ${title}`}
      className={`group relative block ${featured ? 'mb-8 sm:mb-12' : ''}`}
    >
      <AnimeImage
        images={item.images}
        alt={`${title} poster`}
        sizes="(max-width: 1024px) 50vw, 300px"
        loading="eager"
        fetchPriority="high"
        showSkeleton={false}
        className="aspect-[2/3] w-full rounded-xl object-cover shadow-lg ring-1 ring-foreground/10 transition-transform duration-300 group-hover:-translate-y-1"
      />
    </Link>
  );
}
