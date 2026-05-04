import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import type { AntigenStatus } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface AntigenStatusRowProps {
  status: AntigenStatus
}

function usePriorityBadge() {
  const { t } = useTranslations()
  return (s: AntigenStatus) => {
    if (s.is_complete) return { variant: 'ok' as const, label: t('antigenStatus.complete') }
    for (const note of s.notes) {
      if (note.includes('catchup') && note.includes('non più indicato'))
        return { variant: 'muted' as const, label: t('antigenStatus.notIndicated') }
      if (note.includes('catchup') || note.includes('recupero'))
        return { variant: 'warning' as const, label: t('antigenStatus.catchup') }
    }
    if (s.next_dose_due && s.next_dose_due <= new Date().toISOString().split('T')[0])
      return { variant: 'urgent' as const, label: t('antigenStatus.urgent') }
    if (s.next_dose_due) return { variant: 'warning' as const, label: t('antigenStatus.inProgress') }
    return { variant: 'muted' as const, label: '—' }
  }
}

export function AntigenStatusRow({ status }: AntigenStatusRowProps) {
  const priorityBadge = usePriorityBadge()
  const { t } = useTranslations()
  const badge = priorityBadge(status)

  return (
    <div className="flex items-center gap-3 rounded-md border p-3 min-h-[52px]">
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className="font-medium text-sm">{status.antigen}</span>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {t('antigenStatus.doses', { received: status.doses_received, required: status.doses_required })}
            </span>
            <Badge variant={badge.variant}>{badge.label}</Badge>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-0.5 text-xs text-muted-foreground">
          {status.schema_followed && <span>{status.schema_followed}</span>}
          {status.chapter_ref && <span>{t('antigenStatus.chapter', { ref: status.chapter_ref })}</span>}
        </div>
        {status.notes.length > 0 && (
          <div className="mt-1 text-xs text-muted-foreground">
            {status.notes.join(' · ')}
          </div>
        )}
      </div>
    </div>
  )
}
