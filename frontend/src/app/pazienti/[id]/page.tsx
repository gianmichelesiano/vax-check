'use client'

import { useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import useSWR from 'swr'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from '@/components/ui/sheet'
import { VaccinationList } from '@/components/vaccinations/VaccinationList'
import { VaccinationForm } from '@/components/vaccinations/VaccinationForm'
import { api } from '@/lib/api'
import { formatDate, ageLabel, sexLabel } from '@/lib/utils'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  ArrowLeft,
  Plus,
  Activity,
  Shield,
  AlertTriangle,
  Scan,
  Pencil,
  Trash2,
} from 'lucide-react'
import { useState } from 'react'
import type { PatientWithRecords, ComplianceReport } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'
import { PatientForm } from '@/components/patients/PatientForm'

function MetricCard({
  label,
  value,
  icon: Icon,
  variant,
}: {
  label: string
  value: string | number
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  variant: 'default' | 'ok' | 'warning'
}) {
  const colors = {
    default: 'text-muted-foreground',
    ok: 'text-teal-600',
    warning: 'text-amber-600',
  }
  return (
    <div className="rounded-lg border p-3 flex items-center gap-3 min-h-[64px]">
      <Icon className={`h-5 w-5 ${colors[variant]}`} />
      <div>
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-xs text-muted-foreground">{label}</div>
      </div>
    </div>
  )
}

export default function PatientDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string
  const { t, locale } = useTranslations()

  const { data: patient, isLoading, mutate } = useSWR(
    ['patient', id],
    () => api.patients.get(id),
  )

  const [analyzing, setAnalyzing] = useState(false)
  const [report, setReport] = useState<ComplianceReport | null>(null)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [editSheetOpen, setEditSheetOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await api.patients.delete(id)
      router.push('/')
    } finally {
      setDeleting(false)
    }
  }

  const handleAnalyze = useCallback(async () => {
    setAnalyzing(true)
    try {
      const r = await api.analysis.run(id)
      setReport(r)
      mutate()
    } finally {
      setAnalyzing(false)
    }
  }, [id, mutate])

  if (isLoading) {
    return (
      <div className="max-w-lg mx-auto p-4 space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-32" />
        <div className="grid grid-cols-3 gap-2">
          <Skeleton className="h-20" />
          <Skeleton className="h-20" />
          <Skeleton className="h-20" />
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (!patient) {
    return (
      <div className="max-w-lg mx-auto p-4 text-center py-12">
        <p className="text-muted-foreground">{t('patient.detail.notFound')}</p>
        <Link href="/">
          <Button variant="outline" className="mt-4">{t('patient.detail.backToList')}</Button>
        </Link>
      </div>
    )
  }

  const completeCount = report
    ? Object.values(report.antigen_statuses).filter((s) => s.is_complete).length
    : 0
  const totalAntigens = report ? Object.keys(report.antigen_statuses).length : 0
  const missingCount = report ? report.missing_vaccines.length : 0

  return (
    <div className="max-w-lg mx-auto p-4 pb-24">
      <div className="flex items-center gap-3 mb-4">
        <Link href="/" className="min-h-[44px] min-w-[44px] flex items-center justify-center">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-xl font-bold">
            {patient.given_name} {patient.family_name}
          </h1>
          <p className="text-sm text-muted-foreground">
            {sexLabel(patient.sex, t)} {t('common.and')} {ageLabel(patient.age_years, t)} {t('common.and')}{' '}
            {patient.sex === 'F' ? t('patient.detail.femaleBorn') : t('patient.detail.bornOn')} {formatDate(patient.birth_date)}
          </p>
        </div>
        <button
          onClick={() => setEditSheetOpen(true)}
          className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-muted"
        >
          <Pencil className="h-4 w-4" />
        </button>
        <button
          onClick={() => setDeleteOpen(true)}
          className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        <Link href={`/pazienti/${id}/report`} className="flex-1">
          <Button variant="outline" className="w-full border-orange-300 text-orange-600 hover:bg-orange-50 hover:text-orange-700 hover:border-orange-400">
            <Activity className="h-4 w-4 mr-2" />
            {t('patient.detail.analyze')}
          </Button>
        </Link>
        <Link href={`/pazienti/${id}/scansiona`} className="flex-1">
          <Button variant="outline" className="w-full">
            <Scan className="h-4 w-4 mr-2" />
            {t('patient.detail.scan')}
          </Button>
        </Link>
        <Sheet open={sheetOpen} onOpenChange={setSheetOpen}>
          <SheetTrigger asChild>
            <Button className="flex-1">
              <Plus className="h-4 w-4 mr-2" />
              {t('patient.detail.vaccination')}
            </Button>
          </SheetTrigger>
          <SheetContent side="bottom" className="h-[85vh] overflow-y-auto">
            <div className="max-w-md mx-auto">
              <h2 className="text-lg font-bold mb-4">{t('patient.detail.addVaccination')}</h2>
              <VaccinationForm
                patientId={id}
                onSuccess={() => {
                  setSheetOpen(false)
                  mutate()
                }}
                onCancel={() => setSheetOpen(false)}
              />
            </div>
          </SheetContent>
        </Sheet>
      </div>

      {report && (
        <div className="grid grid-cols-3 gap-2 mb-4">
          <MetricCard
            label={t('patient.detail.metrics.vaccinations')}
            value={report.total_records}
            icon={Activity}
            variant="default"
          />
          <MetricCard
            label={t('patient.detail.metrics.antigensOk')}
            value={`${completeCount}/${totalAntigens}`}
            icon={Shield}
            variant="ok"
          />
          <MetricCard
            label={t('patient.detail.metrics.missing')}
            value={missingCount}
            icon={AlertTriangle}
            variant={missingCount > 0 ? 'warning' : 'ok'}
          />
        </div>
      )}

      {patient.notes && (
        <div className="rounded-md bg-muted p-3 mb-4 text-sm">
          <span className="font-medium">{t('patient.detail.notes')} </span>
          {patient.notes}
        </div>
      )}

      <div className="mt-6">
        <h2 className="text-lg font-semibold mb-3">{t('patient.detail.registeredVaccinations')}</h2>
        <VaccinationList
          records={(patient as PatientWithRecords).records ?? []}
          patientId={id}
          onDelete={mutate}
        />
      </div>

      {/* Edit Sheet */}
      <Sheet open={editSheetOpen} onOpenChange={setEditSheetOpen}>
        <SheetContent side="bottom" className="h-[85vh] overflow-y-auto">
          <div className="max-w-md mx-auto">
            <h2 className="text-lg font-bold mb-4">{t('patient.edit.title')}</h2>
            <PatientForm
              initialData={patient}
              patientId={id}
              onSuccess={() => { setEditSheetOpen(false); mutate() }}
              onCancel={() => setEditSheetOpen(false)}
            />
          </div>
        </SheetContent>
      </Sheet>

      {/* Delete Dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('patient.delete.title')}</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">{t('patient.delete.warning')}</p>
          <div className="flex gap-2 pt-2">
            <Button variant="outline" className="flex-1" onClick={() => setDeleteOpen(false)} disabled={deleting}>
              {t('patient.delete.cancel')}
            </Button>
            <Button variant="destructive" className="flex-1" onClick={handleDelete} disabled={deleting}>
              {deleting ? t('patientForm.saving') : t('patient.delete.confirm')}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
