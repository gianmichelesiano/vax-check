'use client'

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AntigenStatusRow } from '@/components/reports/AntigenStatusRow'
import { MissingVaccineCard } from '@/components/reports/MissingVaccineCard'
import { FutureTimeline } from '@/components/reports/FutureTimeline'
import { CheckCircle2 } from 'lucide-react'
import type { ComplianceReport } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface ReportTabsProps {
  report: ComplianceReport
}

export function ReportTabs({ report }: ReportTabsProps) {
  const { t } = useTranslations()
  const baseAntigens = ['DTP', 'IPV', 'Hib', 'HBV', 'PCV_pediatric', 'MOR', 'V']
  const statusEntries = Object.entries(report.antigen_statuses)

  const sortedStatuses = [
    ...statusEntries.filter(([k]) => baseAntigens.includes(k)),
    ...statusEntries.filter(([k]) => !baseAntigens.includes(k)),
  ]

  const sortedMissing = [...report.missing_vaccines].sort((a, b) => {
    const order: Record<string, number> = {
      urgent: 0,
      due_now: 1,
      upcoming: 2,
      catchup_available: 3,
      catchup_closed: 4,
    }
    return (order[a.priority] ?? 5) - (order[b.priority] ?? 5)
  })

  return (
    <Tabs defaultValue="status" className="w-full">
      <TabsList>
        <TabsTrigger value="status">{t('reportTabs.status')}</TabsTrigger>
        <TabsTrigger value="missing">{t('reportTabs.missing')}</TabsTrigger>
        <TabsTrigger value="future">{t('reportTabs.future')}</TabsTrigger>
      </TabsList>

      <TabsContent value="status">
        <div className="space-y-1">
          {sortedStatuses.map(([key, status]) => (
            <AntigenStatusRow key={key} status={status} />
          ))}
        </div>
      </TabsContent>

      <TabsContent value="missing">
        {sortedMissing.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-8 text-teal-600">
            <CheckCircle2 className="h-8 w-8" />
            <p className="text-sm">{t('reportTabs.allComplete')}</p>
          </div>
        ) : (
          <div className="space-y-2">
            {sortedMissing.map((m, i) => (
              <MissingVaccineCard key={`${m.antigen}-${i}`} missing={m} />
            ))}
          </div>
        )}
      </TabsContent>

      <TabsContent value="future">
        <FutureTimeline items={report.future_plan} />
      </TabsContent>
    </Tabs>
  )
}
