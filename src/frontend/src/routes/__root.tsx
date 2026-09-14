import { TanStackDevtools } from '@tanstack/react-devtools';
import { QueryClientProvider, type QueryClient } from '@tanstack/react-query';
import { HeadContent, Scripts, createRootRouteWithContext } from '@tanstack/react-router';
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools';

import { Footer } from '@/shared/components/footer';
import { NotFoundScreen } from '@/shared/components/not-found-screen';
import appCss from '@/styles.css?url';

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  notFoundComponent: NotFoundScreen,
  head: () => ({
    meta: [
      {
        charSet: 'utf-8',
      },
      {
        name: 'viewport',
        content: 'width=device-width, initial-scale=1',
      },
      {
        title: 'Kelbrum | Discover your next favourite anime',
      },
      {
        name: 'description',
        content:
          'Discover your next favourite anime through thoughtful recommendations, search, filters, and catalogue exploration.',
      },
    ],
    links: [
      {
        rel: 'stylesheet',
        href: appCss,
      },
      {
        rel: 'icon',
        type: 'image/x-icon',
        href: '/favicon-light.ico',
        media: '(prefers-color-scheme: light)',
      },
      {
        rel: 'icon',
        type: 'image/x-icon',
        href: '/favicon-dark.ico',
        media: '(prefers-color-scheme: dark)',
      },
      {
        rel: 'icon',
        type: 'image/png',
        sizes: '32x32',
        href: '/favicon-32x32-light.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        rel: 'icon',
        type: 'image/png',
        sizes: '32x32',
        href: '/favicon-32x32-dark.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        rel: 'apple-touch-icon',
        href: '/apple-touch-icon-light.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        rel: 'apple-touch-icon',
        href: '/apple-touch-icon-dark.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        rel: 'manifest',
        href: '/manifest.json',
      },
    ],
  }),
  shellComponent: RootDocument,
});

function RootDocument({ children }: { children: React.ReactNode }) {
  const { queryClient } = Route.useRouteContext();

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(() => {
              const storedTheme = localStorage.getItem('kelbrum-theme');
              const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
              if (storedTheme === 'dark' || (!storedTheme && prefersDark)) {
                document.documentElement.classList.add('dark');
              }
            })();`,
          }}
        />
        <HeadContent />
      </head>
      <body className="antialiased">
        <a
          href="#main-content"
          className="fixed top-2 left-2 z-50 -translate-y-20 rounded-md bg-background px-4 py-3 text-sm font-medium text-foreground shadow-md transition-transform focus:translate-y-0 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none"
        >
          Skip to main content
        </a>
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
        <Footer />
        {import.meta.env.DEV && (
          <TanStackDevtools
            config={{
              position: 'bottom-right',
            }}
            plugins={[
              {
                name: 'Tanstack Router',
                render: <TanStackRouterDevtoolsPanel />,
              },
            ]}
          />
        )}
        <Scripts />
      </body>
    </html>
  );
}
