'use client'

import { cn, initials, avatarColor, ageLabel } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import type { Patient } from '@/lib/types'

interface PatientCardProps {
  patient: Patient
  compact?: boolean
  selected?: boolean
}

export function PatientCard({ patient, compact, selected }: PatientCardProps) {
  const badge = { label: 'Analisi richiesta', variant: 'muted' as const }

  if (compact) {
    return (
      <div
        className={cn(
          'flex items-center gap-2 rounded-md p-2 min-h-[48px] transition-colors hover:bg-accent',
          selected && 'bg-accent',
        )}
      >
        <div
          className={cn(
            'flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold',
            avatarColor(patient.given_name + patient.family_name),
          )}
        >
          {initials(patient.given_name, patient.family_name)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">
            {patient.given_name} {patient.family_name}
          </div>
          <div className="text-xs text-muted-foreground">{ageLabel(patient.age_years)}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-3 rounded-lg border p-3 min-h-[64px] cursor-pointer hover:bg-accent/50 transition-colors">
      <div
        className={cn(
          'flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold',
          avatarColor(patient.given_name + patient.family_name),
        )}
      >
        {initials(patient.given_name, patient.family_name)}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <div className="font-medium truncate">
            {patient.given_name} {patient.family_name}
          </div>
          <Badge variant={badge.variant}>{badge.label}</Badge>
        </div>
        <div className="text-sm text-muted-foreground">{ageLabel(patient.age_years)}</div>
      </div>
    </div>
  )
}
