import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { translations, Language, TranslationKeys } from '../locales';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  t: (key: string, params?: Record<string, string | number>) => string;
  ta: (key: string) => string[];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const getInitialLanguage = (): Language => {
  if (typeof window === 'undefined') return 'es';
  try {
    const saved = localStorage.getItem('language') as Language | null;
    if (saved === 'es' || saved === 'en') return saved;
  } catch (e) {}
  const browserLang = navigator.language.toLowerCase();
  return browserLang.startsWith('es') ? 'es' : 'en';
};

const getNestedValue = (obj: any, path: string): string | undefined => {
  return path.split('.').reduce((acc, part) => acc?.[part], obj);
};

const interpolate = (template: string, params?: Record<string, string | number>): string => {
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (match, key) => {
    return params[key] !== undefined ? String(params[key]) : match;
  });
};

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => getInitialLanguage());

  useEffect(() => {
    try {
      localStorage.setItem('language', language);
    } catch (e) {}
    document.documentElement.setAttribute('lang', language);
  }, [language]);

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
  }, []);

  const toggleLanguage = useCallback(() => {
    setLanguageState((prev) => (prev === 'es' ? 'en' : 'es'));
  }, []);

  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      const currentTranslations: TranslationKeys = translations[language];
      const value = getNestedValue(currentTranslations, key);
      if (typeof value !== 'string') {
        return key;
      }
      return interpolate(value, params);
    },
    [language]
  );

  const ta = useCallback(
    (key: string): string[] => {
      const currentTranslations: TranslationKeys = translations[language];
      const value = getNestedValue(currentTranslations, key);
      if (Array.isArray(value)) {
        return value as string[];
      }
      return [];
    },
    [language]
  );

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t, ta }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
