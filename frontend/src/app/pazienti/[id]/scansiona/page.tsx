'use client'

import { useCallback, useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import useSWR from 'swr'
import { CameraCapture } from '@/components/ocr/CameraCapture'
import { ExtractionReview } from '@/components/ocr/ExtractionReview'
import { ConsentModal } from '@/components/ocr/ConsentModal'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { api } from '@/lib/api'
import type { ExtractionResult, CreateRecordRequest } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

type Step = 'consent' | 'capture' | 'uploading' | 'review' | 'confirming'

export default function ScansionaPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string
  const { t } = useTranslations()

  const { data: patient } = useSWR(['patient', id], () => api.patients.get(id))

  const [step, setStep] = useState<Step>('consent')
  const [results, setResults] = useState<ExtractionResult[]>([])
  const [savedExtractions, setSavedExtractions] = useState<import('@/lib/types').ExtractedVaccination[]>([])
  const [error, setError] = useState<string | null>(null)

  const checkConsent = useCallback(async () => {
    try {
      const r = await api.ocr.consent(id)
      setStep(r.status === 'already_consented' ? 'capture' : 'consent')
    } catch {
      setStep('consent')
    }
  }, [id])

  useEffect(() => {
    if (patient) checkConsent()
  }, [patient, checkConsent])

  const handleConsentAccept = async () => {
    try {
      await api.ocr.consent(id)
      setStep('capture')
    } catch {
      setError(t('scansiona.consentError'))
    }
  }

  const handleConsentManual = () => {
    router.push(`/pazienti/${id}/vaccini/nuovo`)
  }

  const handleCapture = async (file: File) => {
    setStep('uploading')
    setError(null)
    try {
      const r = await api.ocr.extract(file, id)
      if (r.total_found === 0) {
        setError(t('scansiona.noVaccinationsFound'))
        setStep('capture')
        return
      }
      setResults(prev => [...prev, r])
      setStep('review')
    } catch (err) {
      setError(userError(err instanceof Error ? err : new Error(String(err)), t))
      setStep('capture')
    }
  }

  const handleAddPage = (currentExtractions: import('@/lib/types').ExtractedVaccination[]) => {
    setSavedExtractions(currentExtractions)
    setStep('capture')
  }

  const handleConfirm = async (records: CreateRecordRequest[]) => {
    setStep('confirming')
    try {
      await api.ocr.confirm(id, records)
      router.push(`/pazienti/${id}/report`)
    } catch {
      setError(t('scansiona.confirmError'))
      setStep('review')
    }
  }

  return (
    <div className="mx-auto max-w-lg p-4">
      <ConsentModal
        open={step === 'consent'}
        onAccept={handleConsentAccept}
        onManual={handleConsentManual}
      />

      <div className="mb-4 flex items-center gap-3">
        <Link
          href={`/pazienti/${id}`}
          className="flex min-h-[44px] min-w-[44px] items-center justify-center"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-xl font-bold">{t('scansiona.title')}</h1>
      </div>

      {error && (
        <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
          <p>{error}</p>
          <div className="mt-2 flex gap-2">
            <Button variant="outline" size="sm" onClick={() => { setError(null); setStep('capture') }}>
              {t('scansiona.retry')}
            </Button>
            <Link href={`/pazienti/${id}/vaccini/nuovo`}>
              <Button variant="outline" size="sm">{t('scansiona.insertManually')}</Button>
            </Link>
          </div>
        </div>
      )}

      {step === 'uploading' && (
        <div className="flex flex-col items-center gap-4 py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm font-medium">{t('scansiona.uploading')}</p>
          <p className="text-xs text-muted-foreground">
            {t('scansiona.uploadingHint')}
          </p>
        </div>
      )}

      {step === 'confirming' && (
        <div className="flex flex-col items-center gap-4 py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm font-medium">{t('scansiona.saving')}</p>
        </div>
      )}

      {step === 'capture' && !error && (
        <CameraCapture onCapture={handleCapture} onCancel={() => router.back()} />
      )}

      {step === 'review' && results.length > 0 && (
        <ExtractionReview
          result={buildReviewResult(savedExtractions, results[results.length - 1])}
          pageCount={results.length}
          patientId={id}
          onConfirm={handleConfirm}
          onAddPage={handleAddPage}
          onManual={() => router.push(`/pazienti/${id}/vaccini/nuovo`)}
        />
      )}
    </div>
  )
}

function buildReviewResult(
  saved: import('@/lib/types').ExtractedVaccination[],
  latest: ExtractionResult,
): ExtractionResult {
  const all = [...saved, ...latest.extractions]
  return {
    extractions: all,
    total_found: all.length,
    low_confidence_count: all.filter(e => e.confidence < 0.8).length,
    unrecognized_products: [...new Set(all.filter(e => !e.product_name_normalized).map(e => e.product_name_raw))],
    warnings: latest.warnings,
    processing_time_ms: latest.processing_time_ms,
  }
}

function userError(err: Error, t: (key: string, params?: Record<string, string | number>) => string): string {
  if (err.message.includes('ANTHROPIC_API_KEY')) return t('error.ocr.unavailable')
  if (err.message.includes('IMAGE_TOO_LARGE')) return t('error.ocr.imageTooLarge')
  if (err.message.includes('NO_VACCINATIONS')) return t('error.ocr.noVaccinations')
  if (err.message.includes('TIMEOUT')) return t('error.ocr.timeout')
  if (err.message.includes('503')) return t('error.ocr.unavailable')
  if (err.message.includes('403')) return t('error.ocr.consentNotGiven')
  return t('error.ocr.generic')
}
