'use client'

import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'

interface PatientSearchProps {
  value: string
  onChange: (value: string) => void
}

export function PatientSearch({ value, onChange }: PatientSearchProps) {
  return (
    <div className="relative">
      <Search className="absolute left-3 top-3.5 h-5 w-5 text-muted-foreground" />
      <Input
        type="search"
        placeholder="Cerca paziente per nome..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="pl-10"
      />
    </div>
  )
}
