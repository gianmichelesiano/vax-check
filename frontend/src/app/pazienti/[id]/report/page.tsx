'use client'

import { useParams } from 'next/navigation'
import useSWR from 'swr'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ReportTabs } from '@/components/reports/ReportTabs'
import { Loader2, ArrowLeft, AlertCircle } from 'lucide-react'
import { api } from '@/lib/api'
import { useTranslations } from '@/i18n/I18nProvider'

export default function ReportPage() {
  const params = useParams()
  const id = params.id as string
  const { t } = useTranslations()

  const { data: report, isLoading, error } = useSWR(
    ['report', id],
    () => api.analysis.run(id),
    { revalidateOnFocus: false },
  )

  return (
    <div className="max-w-lg mx-auto p-4 pb-24">
      <div className="flex items-center gap-3 mb-6">
        <Link
          href={`/pazienti/${id}`}
          className="min-h-[44px] min-w-[44px] flex items-center justify-center"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-xl font-bold">{t('reportPage.title')}</h1>
      </div>

      {isLoading && (
        <div className="flex flex-col items-center gap-3 py-12 text-muted-foreground">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p>{t('reportPage.loading')}</p>
        </div>
      )}

      {error && (
        <div className="text-center py-12">
          <p className="text-destructive mb-2">{t('reportPage.error')}</p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            {t('reportPage.retry')}
          </Button>
        </div>
      )}

      {!isLoading && !error && !report && (
        <div className="text-center py-12 text-muted-foreground">
          <AlertCircle className="h-12 w-12 mx-auto mb-3 opacity-30" />
          <p className="mb-2">{t('reportPage.noAnalysis')}</p>
          <p className="text-sm mb-4">{t('reportPage.noAnalysisHint')}</p>
          <Link href={`/pazienti/${id}`}>
            <Button variant="outline">{t('reportPage.goToProfile')}</Button>
          </Link>
        </div>
      )}

      {report && (
        <>
          <div className="mb-4 flex items-center gap-2 text-sm text-muted-foreground">
            <span>
              {t('reportPage.analysisOf')}{' '}
              {new Date(report.evaluation_date).toLocaleDateString('de-CH')}
            </span>
            <span>·</span>
            <span>{report.engine_used}</span>
            <span>v{report.engine_version}</span>
          </div>

          <ReportTabs report={report} />

          {report.warnings.length > 0 && (
            <div className="mt-4 rounded-md bg-amber-50 border border-amber-200 p-3">
              <p className="text-sm font-medium text-amber-700 mb-1">{t('reportPage.warnings')}</p>
              {report.warnings.map((w, i) => (
                <p key={i} className="text-xs text-amber-600">{w}</p>
              ))}
            </div>
          )}

          <p className="mt-6 text-xs italic text-muted-foreground text-center">
            {report.disclaimer}
          </p>
        </>
      )}
    </div>
  )
}
