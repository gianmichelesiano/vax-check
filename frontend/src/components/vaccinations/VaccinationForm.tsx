'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ProductSelector } from '@/components/vaccinations/ProductSelector'
import { api } from '@/lib/api'
import type { CreateRecordRequest } from '@/lib/types'

interface VaccinationFormProps {
  patientId: string
  onSuccess?: () => void
  onCancel?: () => void
}

export function VaccinationForm({ patientId, onSuccess, onCancel }: VaccinationFormProps) {
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [productName, setProductName] = useState('')
  const [adminDate, setAdminDate] = useState('')
  const [lotNumber, setLotNumber] = useState('')
  const [notes, setNotes] = useState('')

  function validate(): boolean {
    const e: Record<string, string> = {}
    if (!productName) e.product_name = 'Seleziona un prodotto'
    if (!adminDate) e.administration_date = 'Obbligatoria'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      const data: CreateRecordRequest = {
        product_name: productName,
        administration_date: adminDate,
        lot_number: lotNumber.trim() || undefined,
        notes: notes.trim() || undefined,
      }
      await api.records.add(patientId, data)
      onSuccess?.()
    } catch (err) {
      setErrors({ form: err instanceof Error ? err.message : 'Errore sconosciuto' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-1.5">
        <Label>Prodotto</Label>
        <ProductSelector value={productName} onChange={setProductName} />
        {errors.product_name && <p className="text-sm text-destructive">{errors.product_name}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="admin_date">Data somministrazione</Label>
        <Input
          id="admin_date"
          type="date"
          value={adminDate}
          onChange={(e) => setAdminDate(e.target.value)}
          max={new Date().toISOString().split('T')[0]}
        />
        {errors.administration_date && (
          <p className="text-sm text-destructive">{errors.administration_date}</p>
        )}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="lot">Lotto</Label>
        <Input
          id="lot"
          value={lotNumber}
          onChange={(e) => setLotNumber(e.target.value)}
          placeholder="Opzionale"
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="notes">Note</Label>
        <Input
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Note opzionali"
        />
      </div>

      {errors.form && (
        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
          {errors.form}
        </div>
      )}

      <div className="flex gap-2 pt-2">
        {onCancel && (
          <Button type="button" variant="outline" className="flex-1" onClick={onCancel}>
            Annulla
          </Button>
        )}
        <Button type="submit" className="flex-1" disabled={loading}>
          {loading ? 'Salvataggio...' : 'Salva'}
        </Button>
      </div>
    </form>
  )
}
