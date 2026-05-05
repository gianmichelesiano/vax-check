'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { ExtractionRow } from './ExtractionRow'
import { AlertTriangle, Plus, ScanLine } from 'lucide-react'
import type { ExtractedVaccination, ExtractionResult, CreateRecordRequest } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface ExtractionReviewProps {
  result: ExtractionResult
  patientId: string
  pageCount?: number
  onConfirm: (records: CreateRecordRequest[]) => void
  onAddPage?: (savedExtractions: ExtractedVaccination[]) => void
  onManual: () => void
}

export function ExtractionReview({ result, patientId, pageCount = 1, onConfirm, onAddPage, onManual }: ExtractionReviewProps) {
  const { t } = useTranslations()
  const [extractions, setExtractions] = useState<ExtractedVaccination[]>(result.extractions)
  const [confirming, setConfirming] = useState(false)

  const needsReview = extractions.filter((e) => e.needs_review)
  const allResolved = needsReview.length === 0

  const handleChange = (index: number, updated: Partial<ExtractedVaccination>) => {
    setExtractions((prev) =>
      prev.map((e, i) => {
        if (i !== index) return e
        const merged = { ...e, ...updated }
        const stillNeedsReview = merged.product_name_normalized === null || merged.administration_date === null
        return {
          ...merged,
          needs_review: stillNeedsReview,
          review_reason: stillNeedsReview ? merged.review_reason : null,
        }
      }),
    )
  }

  const handleDelete = (index: number) => {
    setExtractions((prev) => prev.filter((_, i) => i !== index))
  }

  const handleAddRow = () => {
    setExtractions((prev) => [
      ...prev,
      {
        product_name_raw: '',
        product_name_normalized: null,
        administration_date: null,
        lot_number: null,
        confidence: 0,
        needs_review: true,
        review_reason: t('extractionRow.manualEntry'),
      },
    ])
  }

  const handleConfirm = () => {
    setConfirming(true)
    const records: CreateRecordRequest[] = extractions.map((e) => ({
      product_name: e.product_name_normalized ?? e.product_name_raw,
      administration_date: e.administration_date ?? '',
      lot_number: e.lot_number ?? undefined,
    }))
    onConfirm(records)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h2 className="text-lg font-bold">
            {t('extractionReview.found', { count: extractions.length })}
          </h2>
          <p className="text-sm text-muted-foreground">
            {t('extractionReview.verifyHint')}
          </p>
        </div>
        {pageCount > 1 && (
          <span className="shrink-0 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
            {pageCount} pag.
          </span>
        )}
      </div>

      {result.low_confidence_count > 0 && (
        <div className="flex items-start gap-2 rounded-md bg-amber-50 p-3 text-sm text-amber-800">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <p>
            {t('extractionReview.lowConfidence', { count: result.low_confidence_count })}
          </p>
        </div>
      )}

      {result.unrecognized_products.length > 0 && (
        <div className="rounded-md bg-orange-50 p-3 text-sm text-orange-800">
          <p className="font-medium">{t('extractionReview.unrecognized')}</p>
          <ul className="mt-1 list-disc pl-4">
            {result.unrecognized_products.map((p) => (
              <li key={p}>
                {p} — {t('extractionReview.selectProduct')}
              </li>
            ))}
          </ul>
        </div>
      )}

      {result.warnings.length > 0 && (
        <div className="rounded-md bg-blue-50 p-3 text-sm text-blue-800">
          {result.warnings.map((w, i) => (
            <p key={i}>{w}</p>
          ))}
        </div>
      )}

      <div className="space-y-3">
        {extractions.map((extraction, i) => (
          <ExtractionRow
            key={i}
            extraction={extraction}
            index={i}
            onChange={handleChange}
            onDelete={handleDelete}
          />
        ))}
      </div>

      <div className="flex gap-2">
        <Button variant="outline" onClick={handleAddRow} className="flex-1">
          <Plus className="mr-2 h-4 w-4" />
          {t('extractionReview.addRow')}
        </Button>
        {onAddPage && (
          <Button variant="outline" onClick={() => onAddPage(extractions)} className="flex-1">
            <ScanLine className="mr-2 h-4 w-4" />
            {t('scansiona.addPage')}
          </Button>
        )}
      </div>

      <div className="flex flex-col gap-2 pt-2">
        <Button
          onClick={handleConfirm}
          disabled={confirming || !allResolved || extractions.length === 0}
          className="w-full"
        >
          {confirming ? t('extractionReview.saving') : t('extractionReview.confirm')}
        </Button>
        <Link
          href={`/pazienti/${patientId}/vaccini/nuovo`}
          className="text-center text-sm text-muted-foreground underline"
          onClick={onManual}
        >
          {t('extractionReview.insertManually')}
        </Link>
      </div>
    </div>
  )
}
