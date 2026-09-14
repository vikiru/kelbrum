import { Link } from '@tanstack/react-router';

import { Logo } from '@/shared/components/logo';
import { PageContainer } from '@/shared/components/page-container';

export function Footer() {
  return (
    <footer className="border-t bg-muted/30">
      <PageContainer className="flex flex-col gap-8 py-10 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="flex min-h-11 items-center">
            <Logo />
          </div>
          <p className="body-copy mt-3 max-w-xs text-muted-foreground">
            A focused way to discover your next favourite anime.
          </p>
        </div>
        <nav aria-label="Discover">
          <h2 className="text-base font-semibold tracking-[0.14em] text-foreground uppercase">Discover</h2>
          <div className="mt-3 grid gap-1 text-sm font-medium tracking-[0.08em] text-muted-foreground uppercase">
            <Link
              to="/"
              className="inline-flex min-h-11 w-fit items-center rounded-md px-0 py-2 transition-colors duration-200 hover:bg-accent/60 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring motion-reduce:transition-none"
            >
              Home
            </Link>
            <Link
              to="/search"
              className="inline-flex min-h-11 w-fit items-center rounded-md px-0 py-2 transition-colors duration-200 hover:bg-accent/60 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring motion-reduce:transition-none"
            >
              Search anime
            </Link>
            <Link
              to="/top"
              className="inline-flex min-h-11 w-fit items-center rounded-md px-0 py-2 transition-colors duration-200 hover:bg-accent/60 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring motion-reduce:transition-none"
            >
              Top 100 anime
            </Link>
          </div>
        </nav>
      </PageContainer>
      <div className="border-t">
        <PageContainer className="body-sm py-5 text-muted-foreground">
          © {new Date().getFullYear()} Kelbrum. All images and text belong to their respective owners.
        </PageContainer>
      </div>
    </footer>
  );
}
