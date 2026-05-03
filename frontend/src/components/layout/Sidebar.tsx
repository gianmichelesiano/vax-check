'use client'

import useSWR from 'swr'
import { api } from '@/lib/api'
import { PatientCard } from '@/components/patients/PatientCard'
import type { Patient } from '@/lib/types'

interface SidebarProps {
  onSelect?: (patient: Patient) => void
  selectedId?: string
}

export function Sidebar({ onSelect, selectedId }: SidebarProps) {
  const { data: patients, isLoading } = useSWR('patients', () => api.patients.list())

  if (isLoading) {
    return (
      <aside className="hidden md:block w-72 border-r bg-card overflow-y-auto shrink-0">
        <div className="p-3 space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 animate-pulse rounded-md bg-muted" />
          ))}
        </div>
      </aside>
    )
  }

  return (
    <aside className="hidden md:block w-72 border-r bg-card overflow-y-auto shrink-0">
      <div className="p-3 space-y-1">
        {(patients ?? []).map((p) => (
          <button
            key={p.id}
            className="w-full text-left"
            onClick={() => onSelect?.(p)}
          >
            <PatientCard patient={p} compact selected={p.id === selectedId} />
          </button>
        ))}
      </div>
    </aside>
  )
}
