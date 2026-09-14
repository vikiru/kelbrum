import { Link } from '@tanstack/react-router';

import { cn } from '@/shared/lib/merge-class-names';

export interface LogoProps {
  className?: string;
}

export function Logo({ className }: LogoProps) {
  return (
    <Link
      to="/"
      aria-label="Kelbrum home"
      className={cn(
        'inline-flex min-h-11 w-fit items-center gap-0 font-heading text-[1.15rem] font-semibold tracking-[0.08em] uppercase [--logo-kel-color:var(--foreground)] focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ring',
        className,
      )}
    >
      <span className="text-foreground">Kel</span>
      <svg className="-mx-0.5 size-2.5 shrink-0 skew-x-12 text-primary" viewBox="0 0 10 10" aria-hidden="true">
        <defs>
          <linearGradient id="kelbrum-connector" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0.5" stopColor="var(--logo-kel-color)" />
            <stop offset="0.5" stopColor="currentColor" />
          </linearGradient>
        </defs>
        <path fill="url(#kelbrum-connector)" d="m5 0 1.2 3.8L10 5 6.2 6.2 5 10 3.8 6.2 0 5l3.8-1.2L5 0Z" />
      </svg>
      <span className="ml-0.5 text-primary">brum</span>
    </Link>
  );
}
