'use client'

import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { VaccinationForm } from '@/components/vaccinations/VaccinationForm'
import { ArrowLeft } from 'lucide-react'

export default function NewVaccinationPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string

  return (
    <div className="max-w-lg mx-auto p-4">
      <div className="flex items-center gap-3 mb-6">
        <Link
          href={`/pazienti/${id}`}
          className="min-h-[44px] min-w-[44px] flex items-center justify-center"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-xl font-bold">Aggiungi vaccinazione</h1>
      </div>
      <VaccinationForm
        patientId={id}
        onSuccess={() => router.push(`/pazienti/${id}`)}
        onCancel={() => router.back()}
      />
    </div>
  )
}
