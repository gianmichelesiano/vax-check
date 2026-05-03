'use client'

import useSWR from 'swr'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/lib/api'
import { FlaskConical, Server } from 'lucide-react'

export default function SettingsPage() {
  const { data: version, isLoading } = useSWR('kb-version', () => api.catalog.kbVersion(), {
    revalidateOnFocus: false,
  })

  return (
    <div className="max-w-lg mx-auto p-4">
      <h1 className="text-xl font-bold mb-6">Impostazioni</h1>

      <div className="space-y-4">
        <div className="rounded-lg border p-4">
          <div className="flex items-center gap-3 mb-2">
            <FlaskConical className="h-5 w-5 text-primary" />
            <h2 className="font-semibold">VaxCheck</h2>
          </div>
          <p className="text-sm text-muted-foreground">
            Sistema on-premise di analisi vaccinale per farmacie svizzere.
          </p>
          {isLoading ? (
            <Skeleton className="h-4 w-32 mt-2" />
          ) : (
            <p className="text-sm mt-2">
              <span className="font-medium">Knowledge Base:</span>{' '}
              {version?.version ?? '—'}
            </p>
          )}
        </div>

        <div className="rounded-lg border p-4">
          <div className="flex items-center gap-3 mb-2">
            <Server className="h-5 w-5 text-primary" />
            <h2 className="font-semibold">Backend</h2>
          </div>
          <p className="text-sm text-muted-foreground">FastAPI · SQLite · Rule engine deterministico</p>
          <p className="text-sm mt-2">
            <span className="font-medium">API:</span> {process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}
          </p>
        </div>

        <div className="rounded-lg border p-4">
          <h2 className="font-semibold mb-2">Disclaimer</h2>
          <p className="text-xs italic text-muted-foreground">
            VaxCheck è un ausilio alla consulenza farmacistica e non sostituisce il parere del
            medico curante.
          </p>
        </div>
      </div>
    </div>
  )
}
