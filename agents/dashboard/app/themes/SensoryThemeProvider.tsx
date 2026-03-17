'use client';

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react';

export type SensoryTheme = 'calm' | 'focus' | 'energise';

interface SensoryThemeContextValue {
  theme: SensoryTheme;
  setTheme: (t: SensoryTheme) => void;
}

const SensoryThemeContext = createContext<SensoryThemeContextValue>({
  theme: 'focus',
  setTheme: () => {},
});

const STORAGE_KEY = 'hc-sensory-theme';

export function SensoryThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<SensoryTheme>('focus');

  // Hydrate from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as SensoryTheme | null;
    if (saved && ['calm', 'focus', 'energise'].includes(saved)) {
      setThemeState(saved);
      document.documentElement.setAttribute('data-hc-theme', saved);
    } else {
      // Respect OS preference as default: prefers reduced motion → CALM
      const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (prefersReduced) {
        setThemeState('calm');
        document.documentElement.setAttribute('data-hc-theme', 'calm');
      } else {
        document.documentElement.setAttribute('data-hc-theme', 'focus');
      }
    }
  }, []);

  const setTheme = useCallback((t: SensoryTheme) => {
    setThemeState(t);
    document.documentElement.setAttribute('data-hc-theme', t);
    localStorage.setItem(STORAGE_KEY, t);
  }, []);

  return (
    <SensoryThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </SensoryThemeContext.Provider>
  );
}

export function useSensoryTheme() {
  return useContext(SensoryThemeContext);
}
