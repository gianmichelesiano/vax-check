import { Badge } from '@/components/ui/badge'
import type { MissingVaccine } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface MissingVaccineCardProps {
  missing: MissingVaccine
}

function buildPriorityConfig(t: (key: string, params?: Record<string, string | number>) => string) {
  return {
    urgent: { variant: 'urgent' as const, label: t('missingVaccine.urgent') },
    due_now: { variant: 'urgent' as const, label: t('missingVaccine.dueNow') },
    upcoming: { variant: 'warning' as const, label: t('missingVaccine.upcoming') },
    catchup_available: { variant: 'warning' as const, label: t('missingVaccine.catchupAvailable') },
    catchup_closed: { variant: 'muted' as const, label: t('missingVaccine.catchupClosed') },
  }
}

export function MissingVaccineCard({ missing }: MissingVaccineCardProps) {
  const { t } = useTranslations()
  const priorityConfig = buildPriorityConfig(t)
  const config = priorityConfig[missing.priority] ?? { variant: 'muted' as const, label: missing.priority }

  return (
    <div className="rounded-md border p-3 space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-medium text-sm">{missing.antigen}</span>
        <Badge variant={config.variant}>{config.label}</Badge>
      </div>
      <p className="text-sm text-muted-foreground">{missing.reason}</p>
      <div className="text-xs text-muted-foreground">
        <span>{missing.recommended_schedule}</span>
        {missing.chapter_ref && <span className="ml-2">{t('missingVaccine.chapter', { ref: missing.chapter_ref })}</span>}
      </div>
      {missing.age_window && (
        <div className="text-xs text-muted-foreground">
          {missing.age_window[1] === 1
            ? t('missingVaccine.ageWindowYear', { min: missing.age_window[0], max: missing.age_window[1] })
            : t('missingVaccine.ageWindow', { min: missing.age_window[0], max: missing.age_window[1] })}
        </div>
      )}
    </div>
  )
}
