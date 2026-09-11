import { Moon, Sun } from 'lucide-react';

import { useMounted } from '@/shared/hooks/use-mounted';
import { useTheme } from '@/shared/hooks/use-theme';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const mounted = useMounted();
  const displayedTheme = mounted ? theme : 'light';
  const nextTheme = displayedTheme === 'dark' ? 'light' : 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${nextTheme} theme`}
      title={`Switch to ${nextTheme} theme`}
      className="inline-flex size-11 items-center justify-center rounded-md text-muted-foreground transition-[background-color,color,box-shadow] hover:bg-muted/60 hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none motion-reduce:transition-none"
    >
      {displayedTheme === 'dark' ? (
        <Sun className="icon-md" aria-hidden="true" />
      ) : (
        <Moon className="icon-md" aria-hidden="true" />
      )}
    </button>
  );
}
