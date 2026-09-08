import React, { createContext, useContext, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const getInitialTheme = (): Theme => {
  if (typeof window === 'undefined') return 'dark';
  try {
    const saved = localStorage.getItem('theme') as Theme | null;
    if (saved === 'light' || saved === 'dark') return saved;
  } catch (e) {}
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => getInitialTheme());

  const applyTheme = (newTheme: Theme) => {
    const root = document.documentElement;
    const body = document.body;
    if (newTheme === 'dark') {
      root.classList.add('dark');
      body.style.backgroundColor = '#020617';
      body.style.color = '#f1f5f9';
    } else {
      root.classList.remove('dark');
      body.style.backgroundColor = '#f8fafc';
      body.style.color = '#0f172a';
    }
    body.style.transition = 'background-color 200ms ease, color 200ms ease';
  };

  useEffect(() => {
    applyTheme(theme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    try {
      localStorage.setItem('theme', newTheme);
    } catch (e) {}
    applyTheme(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
