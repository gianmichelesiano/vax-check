'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { api } from '@/lib/api'
import type { CreatePatientRequest, Patient, Sex } from '@/lib/types'
import { useTranslations } from '@/i18n/I18nProvider'

interface PatientFormProps {
  initialData?: Patient
  patientId?: string
  onSuccess?: (patientId: string) => void
  onCancel?: () => void
}

export function PatientForm({ initialData, patientId, onSuccess, onCancel }: PatientFormProps) {
  const router = useRouter()
  const { t } = useTranslations()
  const isEdit = Boolean(patientId && initialData)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const [givenName, setGivenName] = useState(initialData?.given_name ?? '')
  const [familyName, setFamilyName] = useState(initialData?.family_name ?? '')
  const [birthDate, setBirthDate] = useState(initialData?.birth_date ?? '')
  const [sex, setSex] = useState<Sex | ''>(initialData?.sex ?? '')
  const [notes, setNotes] = useState(initialData?.notes ?? '')

  function validate(): boolean {
    const e: Record<string, string> = {}
    if (givenName.trim().length < 2) e.given_name = t('patientForm.error.minLength')
    if (familyName.trim().length < 2) e.family_name = t('patientForm.error.minLength')
    if (!birthDate) e.birth_date = t('patientForm.error.required')
    if (!sex) e.sex = t('patientForm.error.required')
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      const data: CreatePatientRequest = {
        given_name: givenName.trim(),
        family_name: familyName.trim(),
        birth_date: birthDate,
        sex: sex as Sex,
        notes: notes.trim() || undefined,
      }
      let id: string
      if (isEdit && patientId) {
        await api.patients.update(patientId, data)
        id = patientId
      } else {
        const patient = await api.patients.create(data)
        id = patient.id
      }
      if (onSuccess) {
        onSuccess(id)
      } else {
        router.push(`/pazienti/${id}`)
      }
    } catch (err) {
      setErrors({ form: err instanceof Error ? err.message : t('patientForm.error.unknown') })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-1.5">
        <Label htmlFor="given_name">{t('patientForm.name')}</Label>
        <Input
          id="given_name"
          value={givenName}
          onChange={(e) => setGivenName(e.target.value)}
          placeholder="Mario"
        />
        {errors.given_name && <p className="text-sm text-destructive">{errors.given_name}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="family_name">{t('patientForm.surname')}</Label>
        <Input
          id="family_name"
          value={familyName}
          onChange={(e) => setFamilyName(e.target.value)}
          placeholder="Rossi"
        />
        {errors.family_name && <p className="text-sm text-destructive">{errors.family_name}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="birth_date">{t('patientForm.birthDate')}</Label>
        <Input
          id="birth_date"
          type="date"
          value={birthDate}
          onChange={(e) => setBirthDate(e.target.value)}
          max={new Date().toISOString().split('T')[0]}
          min="1900-01-01"
        />
        {errors.birth_date && <p className="text-sm text-destructive">{errors.birth_date}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="sex">{t('patientForm.sex')}</Label>
        <Select value={sex} onValueChange={(v) => setSex(v as Sex)}>
          <SelectTrigger id="sex">
            <SelectValue placeholder={t('patientForm.sexPlaceholder')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="M">{t('patientForm.male')}</SelectItem>
            <SelectItem value="F">{t('patientForm.female')}</SelectItem>
            <SelectItem value="X">{t('patientForm.other')}</SelectItem>
          </SelectContent>
        </Select>
        {errors.sex && <p className="text-sm text-destructive">{errors.sex}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="notes">{t('patientForm.notes')}</Label>
        <Input
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder={t('patientForm.notesPlaceholder')}
        />
      </div>

      {errors.form && (
        <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
          {errors.form}
        </div>
      )}

      <div className="flex gap-2">
        {onCancel && (
          <Button type="button" variant="outline" className="flex-1" onClick={onCancel}>
            {t('patient.delete.cancel')}
          </Button>
        )}
        <Button type="submit" className="flex-1" disabled={loading}>
          {loading ? t('patientForm.saving') : isEdit ? t('patientForm.update') : t('patientForm.save')}
        </Button>
      </div>
    </form>
  )
}
