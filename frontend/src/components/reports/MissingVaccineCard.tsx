import { Badge } from '@/components/ui/badge'
import type { MissingVaccine } from '@/lib/types'

interface MissingVaccineCardProps {
  missing: MissingVaccine
}

const priorityConfig: Record<string, { variant: 'urgent' | 'warning' | 'muted'; label: string }> = {
  urgent: { variant: 'urgent', label: 'Urgente' },
  due_now: { variant: 'urgent', label: 'Scaduta' },
  upcoming: { variant: 'warning', label: 'Prossima' },
  catchup_available: { variant: 'warning', label: 'Recupero' },
  catchup_closed: { variant: 'muted', label: 'Non più indicata' },
}

export function MissingVaccineCard({ missing }: MissingVaccineCardProps) {
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
        {missing.chapter_ref && <span className="ml-2">Cap. {missing.chapter_ref}</span>}
      </div>
      {missing.age_window && (
        <div className="text-xs text-muted-foreground">
          Finestra: {missing.age_window[0]}–{missing.age_window[1]} anni
        </div>
      )}
    </div>
  )
}
