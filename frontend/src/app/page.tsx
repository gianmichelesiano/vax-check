'use client'

import { useState, useMemo } from 'react'
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
import { useTranslations } from '@/i18n/I18nProvider'

export default function DashboardPage() {
  const { t } = useTranslations()
  const [search, setSearch] = useState('')
  const [selectedLetter, setSelectedLetter] = useState<string | null>(null)
  const [showAll, setShowAll] = useState(true)

  const { data: allPatients, isLoading } = useSWR('patients', () => api.patients.list())

  const filtered = useMemo(() => {
    const patients = allPatients ?? []
    if (search.trim().length >= 1) {
      const q = search.trim().toLowerCase()
      return patients.filter(
        (p) =>
          p.family_name.toLowerCase().includes(q) ||
          p.given_name.toLowerCase().includes(q),
      )
    }
    if (selectedLetter) {
      return patients.filter(
        (p) => p.family_name[0]?.toUpperCase() === selectedLetter,
      )
    }
    if (showAll) return [...patients]
    return []
  }, [allPatients, search, selectedLetter, showAll])

  const handleSearch = (val: string) => {
    setSearch(val)
    if (val.trim()) { setSelectedLetter(null); setShowAll(false) }
  }

  const handleLetterSelect = (letter: string | null) => {
    setSelectedLetter(letter)
    setShowAll(letter === null)
    setSearch('')
  }

  const showEmpty = !search.trim() && !selectedLetter && !showAll
  const showNoResults =
    !isLoading &&
    filtered.length === 0 &&
    (search.trim().length >= 1 || selectedLetter !== null || showAll)

  return (
    <div className="flex min-h-[calc(100vh-3.5rem)]">
      <Sidebar
        patients={allPatients ?? []}
        selectedLetter={selectedLetter}
        onLetterSelect={handleLetterSelect}
      />

      <div className="flex-1 p-4 max-w-2xl mx-auto w-full">
        {/* Header desktop */}
        <div className="hidden md:flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">{t('dashboard.title')}</h1>
            <p className="text-muted-foreground text-sm">{t('dashboard.subtitle')}</p>
          </div>
          <Link href="/pazienti/nuovo">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              {t('dashboard.newPatient')}
            </Button>
          </Link>
        </div>

        {/* Search */}
        <div className="mb-4">
          <PatientSearch value={search} onChange={handleSearch} />
        </div>

        {/* Letter header */}
        {selectedLetter && !search.trim() && (
          <div className="mb-3 flex items-center gap-2">
            <span className="text-2xl font-black text-primary">{selectedLetter}</span>
            <span className="text-sm text-muted-foreground">
              — {filtered.length} {filtered.length === 1 ? 'paziente' : 'pazienti'}
            </span>
          </div>
        )}

        {/* Content */}
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3 rounded-lg border p-3">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-1.5">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-20" />
                </div>
              </div>
            ))}
          </div>
        ) : showEmpty ? (
          <div className="text-center py-16 text-muted-foreground">
            <Users className="h-12 w-12 mx-auto mb-3 opacity-20" />
            <p className="text-sm">{t('dashboard.startSearch')}</p>
          </div>
        ) : showNoResults ? (
          <div className="text-center py-12 text-muted-foreground">
            <Users className="h-10 w-10 mx-auto mb-3 opacity-20" />
            <p className="text-sm">
              {search.trim()
                ? t('dashboard.noResults', { search: search.trim() })
                : t('dashboard.letterEmpty', { letter: selectedLetter ?? '' })}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered
              .sort((a, b) => a.family_name.localeCompare(b.family_name))
              .map((p) => (
                <Link key={p.id} href={`/pazienti/${p.id}`}>
                  <PatientCard patient={p} />
                </Link>
              ))}
          </div>
        )}

        {/* FAB mobile */}
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
