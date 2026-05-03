import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import type { AntigenStatus } from '@/lib/types'

interface AntigenStatusRowProps {
  status: AntigenStatus
}

const priorityBadge = (s: AntigenStatus) => {
  if (s.is_complete) return { variant: 'ok' as const, label: 'ok' }
  for (const note of s.notes) {
    if (note.includes('catchup') && note.includes('non più indicato'))
      return { variant: 'muted' as const, label: 'non indicato' }
    if (note.includes('catchup') || note.includes('recupero'))
      return { variant: 'warning' as const, label: 'recupero' }
  }
  if (s.next_dose_due && s.next_dose_due <= new Date().toISOString().split('T')[0])
    return { variant: 'urgent' as const, label: 'urgente' }
  if (s.next_dose_due) return { variant: 'warning' as const, label: 'in corso' }
  return { variant: 'muted' as const, label: '—' }
}

export function AntigenStatusRow({ status }: AntigenStatusRowProps) {
  const badge = priorityBadge(status)

  return (
    <div className="flex items-center gap-3 rounded-md border p-3 min-h-[52px]">
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <span className="font-medium text-sm">{status.antigen}</span>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {status.doses_received}/{status.doses_required} dosi
            </span>
            <Badge variant={badge.variant}>{badge.label}</Badge>
          </div>
        </div>
        <div className="flex items-center gap-2 mt-0.5 text-xs text-muted-foreground">
          {status.schema_followed && <span>{status.schema_followed}</span>}
          {status.chapter_ref && <span>Cap. {status.chapter_ref}</span>}
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
