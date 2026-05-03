'use client'

import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { PatientForm } from '@/components/patients/PatientForm'

export default function NewPatientPage() {
  return (
    <div className="max-w-lg mx-auto p-4">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/" className="min-h-[44px] min-w-[44px] flex items-center justify-center">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-xl font-bold">Nuovo paziente</h1>
      </div>
      <PatientForm />
    </div>
  )
}
