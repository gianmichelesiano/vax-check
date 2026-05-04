'use client'

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import { translations, defaultLocale, locales, type Locale } from './translations'

function detectBrowserLanguage(): Locale {
  if (typeof window === 'undefined') return defaultLocale
  const saved = localStorage.getItem('vaxcheck-locale') as Locale | null
  if (saved && locales.includes(saved)) return saved
  const browser = navigator.language.slice(0, 2) as Locale
  if (locales.includes(browser)) return browser
  return defaultLocale
}

interface I18nContextValue {
  locale: Locale
  setLocale: (l: Locale) => void
  t: (key: string, params?: Record<string, string | number>) => string
}

const I18nContext = createContext<I18nContextValue | null>(null)

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale)

  useEffect(() => {
    setLocaleState(detectBrowserLanguage())
  }, [])

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l)
    localStorage.setItem('vaxcheck-locale', l)
    document.documentElement.lang = l
  }, [])

  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      let value = translations[locale]?.[key] ?? translations[defaultLocale]?.[key] ?? key
      if (params) {
        for (const [k, v] of Object.entries(params)) {
          value = value.replace(`{${k}}`, String(v))
        }
      }
      return value
    },
    [locale],
  )

  return (
    <I18nContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useTranslations(): I18nContextValue {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useTranslations must be used within I18nProvider')
  return ctx
}
