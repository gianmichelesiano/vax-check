import { cn } from '@/lib/utils'
import type { FuturePlanItem } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface FutureTimelineProps {
  items: FuturePlanItem[]
}

function formatTarget(age: number | [number, number], t: (key: string, params?: Record<string, string | number>) => string): string {
  if (typeof age === 'number') return t('futureTimeline.years', { age })
  return `${t('futureTimeline.years', { age: age[0] })}–${t('futureTimeline.years', { age: age[1] })}`
}

export function FutureTimeline({ items }: FutureTimelineProps) {
  const { t } = useTranslations()

  if (items.length === 0) {
    return (
      <p className="text-center py-8 text-muted-foreground">
        {t('futureTimeline.empty')}
      </p>
    )
  }

  const sorted = [...items].sort((a, b) => {
    const aAge = typeof a.target_age_years === 'number' ? a.target_age_years : a.target_age_years[0]
    const bAge = typeof b.target_age_years === 'number' ? b.target_age_years : b.target_age_years[0]
    return aAge - bAge
  })

  const dotColor = (planType: string) => {
    if (planType.includes('richiamo')) return 'bg-primary'
    if (planType.includes('base') || planType.includes('primario')) return 'bg-accent'
    if (planType.includes('stagionale')) return 'bg-teal-500'
    return 'bg-muted-foreground'
  }

  return (
    <div className="relative pl-6 space-y-0">
      <div className="absolute left-[7px] top-1 bottom-1 w-0.5 bg-muted" />
      {sorted.map((item, i) => (
        <div key={`${item.antigen}-${i}`} className="relative pb-4 last:pb-0">
          <div
            className={cn(
              'absolute left-[-17px] top-1.5 h-3 w-3 rounded-full border-2 border-background',
              dotColor(item.plan_type),
            )}
          />
          <div className="text-sm">
            <span className="font-medium">{item.antigen}</span>
            <span className="text-muted-foreground"> — {item.plan_type}</span>
          </div>
          <div className="text-xs text-muted-foreground mt-0.5">
            {formatTarget(item.target_age_years, t)}
            {item.target_date_estimate && ` · ${t('futureTimeline.estimated', { date: item.target_date_estimate })}`}
            {item.chapter_ref && ` · ${t('futureTimeline.chapter', { ref: item.chapter_ref })}`}
          </div>
        </div>
      ))}
    </div>
  )
}
