import { useCallback, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark';

function getInitialTheme(): Theme {
  if (typeof window !== 'undefined' && window.localStorage.getItem('kelbrum-theme') === 'dark') return 'dark';
  if (typeof window !== 'undefined' && window.localStorage.getItem('kelbrum-theme') === 'light') return 'light';
  if (typeof document !== 'undefined' && document.documentElement.classList.contains('dark')) return 'dark';
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
  return 'light';
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  useEffect(() => {
    if (window.localStorage.getItem('kelbrum-theme')) return undefined;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handlePreferenceChange = (event: MediaQueryListEvent) => setTheme(event.matches ? 'dark' : 'light');
    mediaQuery.addEventListener('change', handlePreferenceChange);
    return () => mediaQuery.removeEventListener('change', handlePreferenceChange);
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme((current) => {
      const nextTheme = current === 'dark' ? 'light' : 'dark';
      window.localStorage.setItem('kelbrum-theme', nextTheme);
      return nextTheme;
    });
  }, []);
  return { theme, toggleTheme };
}
