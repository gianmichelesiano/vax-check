'use client'

'use client'

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatDate } from '@/lib/utils'
import { Trash2 } from 'lucide-react'
import { useState } from 'react'
import type { VaccinationRecord } from '@/lib/types'
import { api } from '@/lib/api'
import { useTranslations } from '@/i18n/I18nProvider'

interface VaccinationListProps {
  records: VaccinationRecord[]
  patientId: string
  onDelete?: () => void
}

export function VaccinationList({ records, patientId, onDelete }: VaccinationListProps) {
  const { t } = useTranslations()
  const [deleting, setDeleting] = useState<string | null>(null)
  const [confirmId, setConfirmId] = useState<string | null>(null)

  async function handleDelete(recordId: string) {
    setDeleting(recordId)
    try {
      await api.records.delete(patientId, recordId)
      onDelete?.()
    } catch {
      setDeleting(null)
    } finally {
      setConfirmId(null)
    }
  }

  if (records.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p>{t('vaccinationList.empty')}</p>
      </div>
    )
  }

  const sorted = [...records].sort(
    (a, b) => new Date(b.administration_date).getTime() - new Date(a.administration_date).getTime(),
  )

  return (
    <>
      <div className="space-y-1">
        {sorted.map((r) => (
          <div
            key={r.record_id}
            className="flex items-center gap-3 rounded-md border p-3 min-h-[52px] bg-card relative overflow-hidden"
          >
            <div className="flex-1 min-w-0">
              <div className="font-medium text-sm">{r.product_name}</div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{formatDate(r.administration_date)}</span>
                {r.lot_number && <Badge variant="outline" className="text-xs">{r.lot_number}</Badge>}
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="text-muted-foreground hover:text-destructive shrink-0"
              onClick={() => setConfirmId(r.record_id)}
              disabled={deleting === r.record_id}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>

      <Dialog open={!!confirmId} onOpenChange={() => setConfirmId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('vaccinationList.deleteTitle')}</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            {t('vaccinationList.deleteWarning')}
          </p>
          <div className="flex gap-2 justify-end mt-4">
            <Button variant="outline" onClick={() => setConfirmId(null)}>
              {t('vaccinationList.cancel')}
            </Button>
            <Button
              variant="destructive"
              onClick={() => confirmId && handleDelete(confirmId)}
              disabled={deleting === confirmId}
            >
              {t('vaccinationList.delete')}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
