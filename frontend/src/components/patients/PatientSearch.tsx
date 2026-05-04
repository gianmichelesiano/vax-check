'use client'

import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'
import { useTranslations } from '@/i18n/I18nProvider'

interface PatientSearchProps {
  value: string
  onChange: (value: string) => void
}

export function PatientSearch({ value, onChange }: PatientSearchProps) {
  const { t } = useTranslations()

  return (
    <div className="relative">
      <Search className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
      <Input
        type="search"
        placeholder={t('patientSearch.placeholder')}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pl-10"
      />
    </div>
  )
}
