export type Sex = 'M' | 'F' | 'X'

export interface ClinicalCondition {
  code: string
  label: string
  onset_date?: string
}

export interface Patient {
  id: string
  given_name: string
  family_name: string
  birth_date: string
  sex: Sex
  clinical_conditions: ClinicalCondition[]
  occupational_situations: string[]
  notes?: string
  created_at: string
  updated_at: string
  age_years: number
}

export interface VaccinationRecord {
  record_id: string
  patient_id: string
  product_name: string
  administration_date: string
  lot_number?: string
  administered_by?: string
  notes?: string
  created_at: string
}

export type MissingVaccinePriority =
  | 'urgent'
  | 'due_now'
  | 'upcoming'
  | 'catchup_available'
  | 'catchup_closed'

export interface AntigenStatus {
  antigen: string
  is_complete: boolean
  doses_received: number
  doses_required: number
  schema_followed?: string
  last_dose_date?: string
  next_dose_due?: string
  notes: string[]
  chapter_ref?: string
}

export interface MissingVaccine {
  antigen: string
  priority: MissingVaccinePriority
  reason: string
  recommended_schedule: string
  chapter_ref?: string
  age_window?: [number, number]
}

export interface FuturePlanItem {
  antigen: string
  target_age_years: number | [number, number]
  target_date_estimate?: string
  plan_type: string
  chapter_ref?: string
}

export interface ComplianceReport {
  patient: Patient
  evaluation_date: string
  total_records: number
  antigen_statuses: Record<string, AntigenStatus>
  overall_compliance: boolean
  missing_vaccines: MissingVaccine[]
  future_plan: FuturePlanItem[]
  engine_used: 'deterministic' | 'llm'
  engine_version: string
  warnings: string[]
  disclaimer: string
}

export interface PatientWithRecords extends Patient {
  records: VaccinationRecord[]
  latest_report?: ComplianceReport
}

export interface VaccineProduct {
  name: string
  aliases: string[]
  manufacturer?: string
  antigens: string[]
  notes?: string
}

export interface CreatePatientRequest {
  given_name: string
  family_name: string
  birth_date: string
  sex: Sex
  clinical_conditions?: ClinicalCondition[]
  occupational_situations?: string[]
  notes?: string
}

export interface CreateRecordRequest {
  product_name: string
  administration_date: string
  lot_number?: string
  administered_by?: string
  notes?: string
}
