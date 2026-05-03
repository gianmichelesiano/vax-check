'use client'

import useSWR from 'swr'
import { api } from '@/lib/api'
import type { Patient } from '@/lib/types'

export function usePatients(search?: string) {
  return useSWR(
    ['patients', search ?? ''],
    () => api.patients.list(search || undefined),
  )
}

export function usePatient(id: string) {
  return useSWR(['patient', id], () => api.patients.get(id))
}

export function useReport(patientId: string) {
  return useSWR(['report', patientId], () => api.analysis.getLatest(patientId))
}

export function useProducts() {
  return useSWR('products', () => api.catalog.products(), {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    dedupingInterval: 600000,
  })
}

export { api }
