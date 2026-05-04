'use client'

import { ExternalLink, FileText } from 'lucide-react'
import { useTranslations } from '@/i18n/I18nProvider'

interface VersioneTabProps {
  metadata: {
    version: string
    publication_date: string
    source: string
    reference_url?: string
  }
  changelog: string
}

const PDF_URL = 'https://www.bag.admin.ch/calendariovaccinale'

export function VersioneTab({ metadata, changelog }: VersioneTabProps) {
  const { t } = useTranslations()

  return (
    <div className="space-y-6">
      <div className="rounded-lg border p-4 space-y-3">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          {t('versione.title')}
        </h3>

        <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
          <span className="text-muted-foreground">{t('versione.version')}</span>
          <span className="font-mono font-medium">{metadata.version}</span>

          <span className="text-muted-foreground">{t('versione.publication')}</span>
          <span>{metadata.publication_date}</span>

          <span className="text-muted-foreground">{t('versione.source')}</span>
          <span>{metadata.source}</span>
        </div>

        <a
          href={PDF_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm text-primary hover:underline mt-2"
        >
          <FileText className="h-4 w-4" />
          {t('versione.pdfLink')}
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>

      {changelog && (
        <div className="rounded-lg border p-4 space-y-2">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            {t('versione.changelogTitle')}
          </h3>
          <pre className="text-xs whitespace-pre-wrap font-sans text-muted-foreground">
            {changelog}
          </pre>
        </div>
      )}

      <div className="rounded-lg bg-muted/50 p-4">
        <p className="text-xs text-muted-foreground italic">
          {t('versione.disclaimer')}
        </p>
      </div>
    </div>
  )
}
