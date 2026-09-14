import { Link } from '@tanstack/react-router';
import { ArrowLeft, Home } from 'lucide-react';

import { Navbar } from '@/shared/components/navbar';
import { PageContainer } from '@/shared/components/page-container';
import { Button } from '@/shared/components/ui/button';

export function NotFoundScreen() {
  return (
    <main id="main-content" className="min-h-[70vh] bg-background text-foreground">
      <title>Page Not Found | Kelbrum</title>
      <meta name="description" content="The page you requested could not be found on Kelbrum." />
      <meta name="robots" content="noindex, nofollow" />
      <Navbar />
      <PageContainer className="flex min-h-[70vh] items-center justify-center py-20">
        <section className="max-w-xl text-center" aria-labelledby="not-found-title">
          <p className="font-mono text-sm font-semibold tracking-[0.24em] text-muted-foreground uppercase">404</p>
          <h1 id="not-found-title" className="heading-h1 mt-5">
            Page Not Found
          </h1>
          <p className="body-copy mt-5 text-muted-foreground">
            We couldn’t find the page you’re looking for. Head back home and continue exploring the catalogue.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Button nativeButton={false} render={<Link to="/" />} size="lg" className="min-h-11 cursor-pointer px-5">
              <Home data-icon="inline-start" /> Back home
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="min-h-11 cursor-pointer px-5"
              onClick={() => window.history.back()}
            >
              <ArrowLeft data-icon="inline-start" /> Go back
            </Button>
          </div>
        </section>
      </PageContainer>
    </main>
  );
}
