'use client'

import { useCallback } from 'react'
import { useRouter, useParams } from 'next/navigation'
import useSWR from 'swr'
import { api } from '@/lib/api'
import { PatientCard } from '@/components/patients/PatientCard'
import type { Patient } from '@/lib/types'

export function Sidebar() {
  const router = useRouter()
  const params = useParams()
  const selectedId = (params?.id as string) ?? null

  const { data: patients, isLoading } = useSWR('patients', () => api.patients.list())

  const handleSelect = useCallback(
    (p: Patient) => {
      router.push(`/pazienti/${p.id}/`)
    },
    [router],
  )

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
            onClick={() => handleSelect(p)}
          >
            <PatientCard patient={p} compact selected={p.id === selectedId} />
          </button>
        ))}
      </div>
    </aside>
  )
}
