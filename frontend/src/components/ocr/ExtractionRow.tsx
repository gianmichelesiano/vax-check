'use client'

import { ProductSelector } from '@/components/vaccinations/ProductSelector'
import { Input } from '@/components/ui/input'
import { X } from 'lucide-react'
import type { ExtractedVaccination } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface ExtractionRowProps {
  extraction: ExtractedVaccination
  index: number
  onChange: (index: number, updated: Partial<ExtractedVaccination>) => void
  onDelete: (index: number) => void
}

export function ExtractionRow({ extraction, index, onChange, onDelete }: ExtractionRowProps) {
  const { t } = useTranslations()

  const badge = (() => {
    if (extraction.confidence >= 0.9) return { color: 'bg-green-500', label: '' }
    if (extraction.confidence >= 0.7) return { color: 'bg-amber-500', label: t('extractionRow.confidence.check') }
    return { color: 'bg-red-500', label: t('extractionRow.confidence.fix') }
  })()

  return (
    <div
      className={`space-y-3 rounded-lg border p-3 ${
        extraction.needs_review ? 'border-l-4 border-l-amber-400' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`inline-block h-2.5 w-2.5 rounded-full ${badge.color}`} />
          <span className="text-xs font-medium text-muted-foreground">
            {(extraction.confidence >= 0.9
              ? t('extractionRow.confidence.high')
              : extraction.confidence >= 0.7
                ? t('extractionRow.confidence.medium')
                : t('extractionRow.confidence.low')
            )}{' '}
            {badge.label && <span className="text-amber-600">({badge.label})</span>}
          </span>
        </div>
        <button
          onClick={() => onDelete(index)}
          className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {extraction.review_reason && (
        <p className="text-xs text-amber-600">{extraction.review_reason}</p>
      )}

      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        <ProductSelector
          value={extraction.product_name_normalized ?? extraction.product_name_raw}
          onChange={(val) => onChange(index, { product_name_normalized: val })}
        />
        <Input
          type="date"
          value={extraction.administration_date ?? ''}
          onChange={(e) => onChange(index, { administration_date: e.target.value || null })}
          max={new Date().toISOString().split('T')[0]}
        />
      </div>

      <Input
        value={extraction.lot_number ?? ''}
        onChange={(e) => onChange(index, { lot_number: e.target.value || null })}
        placeholder={t('extractionRow.lotPlaceholder')}
        className="text-sm"
      />
    </div>
  )
}
