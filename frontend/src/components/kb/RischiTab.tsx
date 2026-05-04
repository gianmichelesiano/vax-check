'use client'

import { useMemo, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'
import { RiskGroupSection } from './RiskGroupSection'
import type { RiskGroups } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface RischiTabProps {
  riskGroups: RiskGroups
}

export function RischiTab({ riskGroups }: RischiTabProps) {
  const { t } = useTranslations()
  const [search, setSearch] = useState('')

  const filterItems = useMemo(() => {
    if (!search) return riskGroups
    const q = search.toLowerCase()
    const filter = (items: typeof riskGroups.clinical_conditions) =>
      items.filter(
        (item) =>
          item.label.toLowerCase().includes(q) ||
          item.recommended.some((v) => v.toLowerCase().includes(q)),
      )
    return {
      clinical_conditions: filter(riskGroups.clinical_conditions),
      occupational: filter(riskGroups.occupational),
      pregnancy: filter(riskGroups.pregnancy),
    }
  }, [riskGroups, search])

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder={t('rischi.searchPlaceholder')}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      <RiskGroupSection
        title={t('rischi.section.clinical')}
        items={filterItems.clinical_conditions}
        defaultOpen={true}
      />
      <RiskGroupSection title={t('rischi.section.occupational')} items={filterItems.occupational} />
      <RiskGroupSection title={t('rischi.section.pregnancy')} items={filterItems.pregnancy} />

      {!search && (
        <p className="text-[10px] text-muted-foreground text-center">
          {t('rischi.total', { count: riskGroups.clinical_conditions.length + riskGroups.occupational.length + riskGroups.pregnancy.length })}
        </p>
      )}
    </div>
  )
}
