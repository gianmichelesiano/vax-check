'use client'

import useSWR from 'swr'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/lib/api'
import { FlaskConical } from 'lucide-react'
import { useTranslations } from '@/i18n/I18nProvider'
import { localeLabels, locales } from '@/i18n/translations'
import type { Locale } from '@/i18n/translations'

export default function SettingsPage() {
  const { data: version, isLoading } = useSWR('kb-version', () => api.catalog.kbVersion(), {
    revalidateOnFocus: false,
  })
  const { t, locale, setLocale } = useTranslations()

  return (
    <div className="max-w-lg mx-auto p-4">
      <h1 className="text-xl font-bold mb-6">{t('settings.title')}</h1>

      <div className="space-y-4">
        <div className="rounded-lg border p-4">
          <h2 className="font-semibold mb-2">{t('settings.language')}</h2>
          <select
            value={locale}
            onChange={(e) => setLocale(e.target.value as Locale)}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {locales.map((l) => (
              <option key={l} value={l}>{localeLabels[l]}</option>
            ))}
          </select>
        </div>

        <div className="rounded-lg border p-4">
          <div className="flex items-center gap-3 mb-2">
            <FlaskConical className="h-5 w-5 text-primary" />
            <h2 className="font-semibold">{t('settings.appName')}</h2>
          </div>
          <p className="text-sm text-muted-foreground">
            {t('settings.appDescription')}
          </p>
          {isLoading ? (
            <Skeleton className="h-4 w-32 mt-2" />
          ) : (
            <p className="text-sm mt-2">
              <span className="font-medium">{t('settings.knowledgeBase')}</span>{' '}
              {version?.version ?? '—'}
            </p>
          )}
        </div>

        <div className="rounded-lg border p-4">
          <h2 className="font-semibold mb-2">{t('settings.disclaimer')}</h2>
          <p className="text-xs italic text-muted-foreground">
            {t('settings.disclaimerText')}
          </p>
        </div>
      </div>
    </div>
  )
}
