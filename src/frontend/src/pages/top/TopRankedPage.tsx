import topRankedAnimeData from '@/data/top-100.json';
import { AnimeCardItemsSchema } from '@/entities/anime/model/anime-schema';
import { AnimeCard } from '@/entities/anime/ui/anime-card';
import { Navbar } from '@/shared/components/navbar';
import { PageContainer } from '@/shared/components/page-container';

const topAnime = AnimeCardItemsSchema.parse(topRankedAnimeData).slice(0, 100);

export function TopRankedPage() {
  return (
    <main id="main-content" className="min-h-screen bg-background text-foreground">
      <Navbar />
      <PageContainer className="py-12 lg:py-20">
        <header className="w-full">
          <h1 className="heading-h1 text-balance">Top 100 Anime</h1>
          <p className="body-copy mt-5 text-pretty text-muted-foreground">
            The highest-rated anime in the catalogue, ranked by score. See what made the Top 100 and find something
            worth watching.
          </p>
        </header>
        <ol className="anime-card-grid anime-card-grid--five-column below-fold-content mt-10 gap-5">
          {topAnime.map((item, index) => (
            <li key={item.malId}>
              <AnimeCard item={item} rank={index + 1} />
            </li>
          ))}
        </ol>
      </PageContainer>
    </main>
  );
}
