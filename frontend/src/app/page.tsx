'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import useSWR from 'swr'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { PatientCard } from '@/components/patients/PatientCard'
import { PatientSearch } from '@/components/patients/PatientSearch'
import { Sidebar } from '@/components/layout/Sidebar'
import { Plus, Users } from 'lucide-react'
import type { Patient } from '@/lib/types'
import { api } from '@/lib/api'

export default function DashboardPage() {
  const [search, setSearch] = useState('')
  const [debounced, setDebounced] = useState('')

  useEffect(() => {
    const t = setTimeout(() => setDebounced(search), 300)
    return () => clearTimeout(t)
  }, [search])

  const { data: patients, isLoading } = useSWR(
    ['patients', debounced],
    () => api.patients.list(debounced || undefined),
  )

  return (
    <div className="flex min-h-[calc(100vh-3.5rem)]">
      <Sidebar />

      <div className="flex-1 p-4 max-w-2xl mx-auto w-full">
        <div className="hidden md:flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Pazienti</h1>
            <p className="text-muted-foreground text-sm">Gestisci la tua anagrafica vaccinale</p>
          </div>
          <Link href="/pazienti/nuovo">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nuovo paziente
            </Button>
          </Link>
        </div>

        <div className="mb-4">
          <PatientSearch value={search} onChange={setSearch} />
        </div>

        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3 rounded-lg border p-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-1.5">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-20" />
                </div>
              </div>
            ))}
          </div>
        ) : patients && patients.length > 0 ? (
          <div className="space-y-2">
            {patients.map((p) => (
              <Link key={p.id} href={`/pazienti/${p.id}`}>
                <PatientCard patient={p} />
              </Link>
            ))}
          </div>
        ) : debounced ? (
          <div className="text-center py-12 text-muted-foreground">
            <Users className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p>Nessun paziente trovato per &quot;{debounced}&quot;</p>
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground">
            <Users className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p>Nessun paziente. Crea il primo paziente.</p>
          </div>
        )}

        <div className="md:hidden fixed bottom-16 right-4 z-30">
          <Link href="/pazienti/nuovo">
            <Button size="lg" className="rounded-full h-14 w-14 shadow-lg">
              <Plus className="h-6 w-6" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
