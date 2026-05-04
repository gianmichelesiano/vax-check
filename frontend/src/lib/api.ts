const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const error = await res.text()
    throw new Error(`API ${res.status}: ${error}`)
  }
  if (res.status === 204) {
    return undefined as T
  }
  return res.json()
}

import type {
  Patient,
  PatientWithRecords,
  CreatePatientRequest,
  VaccinationRecord,
  CreateRecordRequest,
  ComplianceReport,
  VaccineProduct,
  ExtractionResult,
  KBFullResponse,
} from './types'

export const api = {
  patients: {
    list: (search?: string) =>
      apiFetch<Patient[]>(`/api/patients${search ? `?search=${encodeURIComponent(search)}` : ''}`),
    get: (id: string) =>
      apiFetch<PatientWithRecords>(`/api/patients/${id}`),
    create: (data: CreatePatientRequest) =>
      apiFetch<Patient>('/api/patients', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: string, data: Partial<CreatePatientRequest>) =>
      apiFetch<Patient>(`/api/patients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id: string) =>
      apiFetch<void>(`/api/patients/${id}`, { method: 'DELETE' }),
  },
  records: {
    add: (patientId: string, data: CreateRecordRequest) =>
      apiFetch<VaccinationRecord>(`/api/patients/${patientId}/records`, {
        method: 'POST', body: JSON.stringify(data),
      }),
    delete: (patientId: string, recordId: string) =>
      apiFetch<void>(`/api/patients/${patientId}/records/${recordId}`, { method: 'DELETE' }),
  },
  analysis: {
    run: (patientId: string) =>
      apiFetch<ComplianceReport>(`/api/patients/${patientId}/analyze`, { method: 'POST' }),
    getLatest: (patientId: string) =>
      apiFetch<ComplianceReport | null>(`/api/patients/${patientId}/reports/latest`),
  },
  catalog: {
    products: () => apiFetch<VaccineProduct[]>('/api/catalog/products'),
    kbVersion: () => apiFetch<{ version: string; date: string }>('/api/kb/version'),
    full: () => apiFetch<KBFullResponse>('/api/kb/full'),
  },
  ocr: {
    extract: async (image: Blob, patientId?: string): Promise<ExtractionResult> => {
      const form = new FormData()
      form.append('image', image, 'booklet.jpg')
      if (patientId) form.append('patient_id', patientId)
      const res = await fetch(`${BASE}/api/ocr/extract`, { method: 'POST', body: form })
      if (!res.ok) {
        const err = await res.text()
        throw new Error(`OCR ${res.status}: ${err}`)
      }
      return res.json()
    },
    consent: (patientId: string) =>
      apiFetch<{ status: string }>(`/api/ocr/consent/${patientId}`, { method: 'POST' }),
    confirm: (patientId: string, records: CreateRecordRequest[]) =>
      apiFetch<{ added: number; report_id: string; overall_compliance: boolean }>(
        '/api/ocr/confirm',
        { method: 'POST', body: JSON.stringify({ patient_id: patientId, confirmed_records: records }) },
      ),
  },
}
