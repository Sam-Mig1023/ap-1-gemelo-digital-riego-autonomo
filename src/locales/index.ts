import { es } from './es';
import { en } from './en';

export type Language = 'es' | 'en';

export type TranslationKeys = typeof es;

export const translations: Record<Language, TranslationKeys> = {
  es,
  en,
};
