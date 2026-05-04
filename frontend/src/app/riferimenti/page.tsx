'use client'

import { Suspense, useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { BookText } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { CalendarioTab } from '@/components/kb/CalendarioTab'
import { CatalogoTab } from '@/components/kb/CatalogoTab'
import { RischiTab } from '@/components/kb/RischiTab'
import { VersioneTab } from '@/components/kb/VersioneTab'
import { api } from '@/lib/api'
import type { KBFullResponse } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

const TAB_KEYS = ['calendario', 'catalogo', 'rischi', 'versione'] as const

function LoadingSkeleton() {
  return (
    <div className="space-y-4 p-4">
      <Skeleton className="h-10 w-full max-w-md" />
      <Skeleton className="h-64 w-full rounded-lg" />
    </div>
  )
}

function RiferimentiContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const { t } = useTranslations()
  const tabParam = searchParams.get('tab')
  const initialTab = TAB_KEYS.includes(tabParam as typeof TAB_KEYS[number])
    ? tabParam!
    : 'calendario'

  const TAB_LABELS: Record<string, string> = {
    calendario: t('riferimenti.tab.calendario'),
    catalogo: t('riferimenti.tab.catalogo'),
    rischi: t('riferimenti.tab.rischi'),
    versione: t('riferimenti.tab.versione'),
  }

  const [data, setData] = useState<KBFullResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState(initialTab)

  useEffect(() => {
    api.catalog.full()
      .then((res) => {
        setData(res)
        setLoading(false)
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Errore caricamento dati')
        setLoading(false)
      })
  }, [])

  const handleTabChange = (tab: string) => {
    setActiveTab(tab)
    const params = new URLSearchParams(searchParams.toString())
    if (tab === 'calendario') params.delete('tab')
    else params.set('tab', tab)
    const qs = params.toString()
    router.replace(`/riferimenti${qs ? `?${qs}` : ''}`, { scroll: false })
  }

  if (loading) return <LoadingSkeleton />
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-4">
        <p className="text-destructive text-sm">{error}</p>
      </div>
    )
  }
  if (!data) return null

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-4">
      <div className="flex items-center gap-2">
        <BookText className="h-5 w-5 text-primary" />
        <h1 className="text-lg font-semibold">{t('riferimenti.title')}</h1>
      </div>

      <div className="hidden md:block">
        <Tabs value={activeTab} onValueChange={handleTabChange}>
          <TabsList>
            {TAB_KEYS.map((key) => (
              <TabsTrigger key={key} value={key}>
                {TAB_LABELS[key]}
              </TabsTrigger>
            ))}
          </TabsList>
          <TabsContent value="calendario">
            <CalendarioTab antigens={data.antigens} />
          </TabsContent>
          <TabsContent value="catalogo">
            <CatalogoTab products={data.products} deprecatedProducts={data.deprecated_products} />
          </TabsContent>
          <TabsContent value="rischi">
            <RischiTab riskGroups={data.risk_groups} />
          </TabsContent>
          <TabsContent value="versione">
            <VersioneTab metadata={data.metadata} changelog={data.changelog} />
          </TabsContent>
        </Tabs>
      </div>

      <div className="md:hidden space-y-4">
        <select
          value={activeTab}
          onChange={(e) => handleTabChange(e.target.value)}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {TAB_KEYS.map((key) => (
            <option key={key} value={key}>
              {TAB_LABELS[key]}
            </option>
          ))}
        </select>

        {activeTab === 'calendario' && <CalendarioTab antigens={data.antigens} />}
        {activeTab === 'catalogo' && <CatalogoTab products={data.products} deprecatedProducts={data.deprecated_products} />}
        {activeTab === 'rischi' && <RischiTab riskGroups={data.risk_groups} />}
        {activeTab === 'versione' && <VersioneTab metadata={data.metadata} changelog={data.changelog} />}
      </div>
    </div>
  )
}

export default function RiferimentiPage() {
  return (
    <Suspense fallback={<LoadingSkeleton />}>
      <RiferimentiContent />
    </Suspense>
  )
}
