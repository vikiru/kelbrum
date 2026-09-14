import { Link } from '@tanstack/react-router';
import { ArrowLeft, Menu } from 'lucide-react';

import { Logo } from '@/shared/components/logo';
import { PageContainer } from '@/shared/components/page-container';
import { ThemeToggle } from '@/shared/components/theme-toggle';
import { Button } from '@/shared/components/ui/button';
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/shared/components/ui/sheet';

export interface NavbarProps {
  backTo?: '/' | '/top' | '/search';
  backLabel?: string;
}

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Top 100', to: '/top' },
  { label: 'Search', to: '/search' },
] as const;

export function Navbar({ backTo, backLabel = 'Home' }: NavbarProps) {
  return (
    <nav className="border-b bg-background/95">
      <PageContainer className="flex min-h-16 items-center gap-4">
        <div className="flex min-h-11 items-center">
          <Logo />
        </div>
        <div className="body-sm ml-auto hidden items-center gap-1 md:flex">
          {backTo ? (
            <Link
              to={backTo}
              className="inline-flex min-h-11 items-center gap-2 rounded-md px-3 text-muted-foreground transition-[background-color,color] duration-200 hover:bg-muted/60 hover:text-foreground motion-reduce:transition-none"
            >
              <ArrowLeft className="icon-sm" aria-hidden="true" /> {backLabel}
            </Link>
          ) : (
            navItems.slice(1).map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className="inline-flex min-h-11 items-center rounded-md px-3 text-muted-foreground transition-[background-color,color] duration-200 hover:bg-muted/60 hover:text-foreground motion-reduce:transition-none"
              >
                {item.label}
              </Link>
            ))
          )}
          <ThemeToggle />
        </div>
        <Sheet>
          <SheetTrigger
            render={
              <Button
                variant="ghost"
                size="icon"
                className="ml-auto min-h-11 min-w-11 md:hidden"
                aria-label="Open navigation"
              >
                <Menu aria-hidden="true" />
              </Button>
            }
          />
          <SheetContent side="right" className="w-[min(22rem,calc(100vw-2rem))]">
            <SheetHeader className="sr-only">
              <SheetTitle>Navigation</SheetTitle>
              <SheetDescription>Site navigation links</SheetDescription>
            </SheetHeader>
            <div className="h-16 shrink-0" aria-hidden="true" />
            <nav className="flex flex-col gap-1 px-6" aria-label="Mobile navigation">
              {backTo ? (
                <SheetClose
                  nativeButton={false}
                  render={
                    <Link
                      to={backTo}
                      className="flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-medium text-muted-foreground transition-[background-color,color] hover:bg-muted/60 hover:text-foreground motion-reduce:transition-none"
                    />
                  }
                >
                  <ArrowLeft className="icon-sm" aria-hidden="true" />
                  {backLabel}
                </SheetClose>
              ) : (
                navItems.map((item) => (
                  <SheetClose
                    key={item.to}
                    nativeButton={false}
                    render={
                      <Link
                        to={item.to}
                        className="flex min-h-11 items-center rounded-md px-3 text-sm font-medium text-muted-foreground transition-[background-color,color] hover:bg-muted/60 hover:text-foreground motion-reduce:transition-none"
                      />
                    }
                  >
                    {item.label}
                  </SheetClose>
                ))
              )}
              <div className="mt-2 border-t pt-2">
                <ThemeToggle />
              </div>
            </nav>
          </SheetContent>
        </Sheet>
      </PageContainer>
    </nav>
  );
}
