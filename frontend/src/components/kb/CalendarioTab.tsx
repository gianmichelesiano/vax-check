'use client'

import { useMemo, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'
import { AntigenRow } from './AntigenRow'
import type { KBAntigen } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

const levelOrder = ['base', 'complementary', 'risk_group'] as const

interface CalendarioTabProps {
  antigens: KBAntigen[]
}

export function CalendarioTab({ antigens }: CalendarioTabProps) {
  const { t } = useTranslations()
  const [search, setSearch] = useState('')

  const levelLabels: Record<string, string> = {
    base: t('calendario.level.base'),
    complementary: t('calendario.level.complementary'),
    risk_group: t('calendario.level.riskGroup'),
  }

  const grouped = useMemo(() => {
    const filtered = search
      ? antigens.filter((a) =>
          a.full_name.toLowerCase().includes(search.toLowerCase()),
        )
      : antigens

    const groups: Record<string, KBAntigen[]> = { base: [], complementary: [], risk_group: [] }
    for (const a of filtered) {
      const level = levelOrder.includes(a.recommendation_level as typeof levelOrder[number])
        ? a.recommendation_level
        : 'complementary'
      groups[level].push(a)
    }
    return groups
  }, [antigens, search])

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder={t('calendario.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {levelOrder.map((level) => {
        const items = grouped[level]
        if (items.length === 0) return null
        return (
          <div key={level}>
            <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              {levelLabels[level]} ({items.length})
            </h3>
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-left">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="py-2 px-3 text-xs font-medium text-muted-foreground w-[30%]">{t('calendario.table.antigen')}</th>
                    <th className="py-2 px-3 text-xs font-medium text-muted-foreground w-[25%]">{t('calendario.table.primary')}</th>
                    <th className="py-2 px-3 text-xs font-medium text-muted-foreground w-[30%]">{t('calendario.table.boosters')}</th>
                    <th className="py-2 px-3 text-xs font-medium text-muted-foreground w-[15%]">{t('calendario.table.chapter')}</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((a) => (
                    <AntigenRow key={a.code} antigen={a} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      })}

      {antigens.length > 0 && Object.values(grouped).every((g) => g.length === 0) && (
        <p className="text-center text-sm text-muted-foreground py-8">
          {t('calendario.noResults')}
        </p>
      )}
    </div>
  )
}
