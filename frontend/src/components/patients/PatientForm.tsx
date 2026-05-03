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
import type { CreatePatientRequest, Sex } from '@/lib/types'

interface PatientFormProps {
  onSuccess?: (patientId: string) => void
}

export function PatientForm({ onSuccess }: PatientFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const [givenName, setGivenName] = useState('')
  const [familyName, setFamilyName] = useState('')
  const [birthDate, setBirthDate] = useState('')
  const [sex, setSex] = useState<Sex | ''>('')
  const [notes, setNotes] = useState('')

  function validate(): boolean {
    const e: Record<string, string> = {}
    if (givenName.trim().length < 2) e.given_name = 'Minimo 2 caratteri'
    if (familyName.trim().length < 2) e.family_name = 'Minimo 2 caratteri'
    if (!birthDate) e.birth_date = 'Obbligatoria'
    if (!sex) e.sex = 'Obbligatorio'
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
      const patient = await api.patients.create(data)
      if (onSuccess) {
        onSuccess(patient.id)
      } else {
        router.push(`/pazienti/${patient.id}`)
      }
    } catch (err) {
      setErrors({ form: err instanceof Error ? err.message : 'Errore sconosciuto' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-1.5">
        <Label htmlFor="given_name">Nome</Label>
        <Input
          id="given_name"
          value={givenName}
          onChange={(e) => setGivenName(e.target.value)}
          placeholder="Mario"
        />
        {errors.given_name && <p className="text-sm text-destructive">{errors.given_name}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="family_name">Cognome</Label>
        <Input
          id="family_name"
          value={familyName}
          onChange={(e) => setFamilyName(e.target.value)}
          placeholder="Rossi"
        />
        {errors.family_name && <p className="text-sm text-destructive">{errors.family_name}</p>}
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="birth_date">Data di nascita</Label>
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
        <Label htmlFor="sex">Sesso</Label>
        <Select value={sex} onValueChange={(v) => setSex(v as Sex)}>
          <SelectTrigger id="sex">
            <SelectValue placeholder="Seleziona sesso" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="M">Maschio</SelectItem>
            <SelectItem value="F">Femmina</SelectItem>
            <SelectItem value="X">Altro</SelectItem>
          </SelectContent>
        </Select>
        {errors.sex && <p className="text-sm text-destructive">{errors.sex}</p>}
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

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? 'Salvataggio...' : 'Salva paziente'}
      </Button>
    </form>
  )
}
