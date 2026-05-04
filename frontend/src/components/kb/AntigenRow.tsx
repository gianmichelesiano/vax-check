'use client'

import type { KBAntigen } from '@/lib/types'
import { Badge } from '@/components/ui/badge'
import { useTranslations } from '@/i18n/I18nProvider'

const levelColors: Record<string, string> = {
  base: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  complementary: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  risk_group: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
}

const PDF_URL = 'https://www.bag.admin.ch/calendariovaccinale'

interface AntigenRowProps {
  antigen: KBAntigen
}

export function AntigenRow({ antigen }: AntigenRowProps) {
  const { t } = useTranslations()

  const levelLabels: Record<string, string> = {
    base: t('antigenRow.level.base'),
    complementary: t('antigenRow.level.complementary'),
    risk_group: t('antigenRow.level.riskGroup'),
  }

  return (
    <tr className="border-b last:border-0 hover:bg-muted/50">
      <td className="py-3 pr-2">
        <div className="font-medium text-sm">{antigen.full_name}</div>
        <Badge
          variant="outline"
          className={`mt-1 text-[10px] px-1.5 py-0 font-medium ${levelColors[antigen.recommendation_level] || ''}`}
        >
          {levelLabels[antigen.recommendation_level] || antigen.recommendation_level}
        </Badge>
      </td>
      <td className="py-3 px-2 text-sm text-muted-foreground">
        {antigen.primary_schedule_summary || '-'}
      </td>
      <td className="py-3 px-2 text-sm text-muted-foreground">
        {antigen.boosters_summary || '-'}
      </td>
      <td className="py-3 pl-2">
        {antigen.chapter_ref ? (
          <div className="flex flex-wrap gap-1">
            {antigen.chapter_ref.split(',').map((ref: string) => (
              <a
                key={ref.trim()}
                href={PDF_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary hover:bg-primary/20 transition-colors"
              >
                {ref.trim()}
              </a>
            ))}
          </div>
        ) : (
          <span className="text-xs text-muted-foreground">-</span>
        )}
      </td>
    </tr>
  )
}
