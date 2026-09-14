import { LoaderCircle } from 'lucide-react';

export interface LoadingScreenProps {
  label: string;
}

export function LoadingScreen({ label }: LoadingScreenProps) {
  return (
    <main id="main-content" className="flex min-h-screen items-center justify-center" aria-live="polite">
      <output className="flex flex-col items-center gap-3 text-muted-foreground">
        <LoaderCircle className="size-8 animate-spin motion-reduce:animate-none" aria-hidden="true" />
        <span className="body-sm">{label}</span>
      </output>
    </main>
  );
}
