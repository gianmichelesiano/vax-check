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

export interface ExtractedVaccination {
  product_name_raw: string
  product_name_normalized: string | null
  administration_date: string | null
  lot_number: string | null
  confidence: number
  needs_review: boolean
  review_reason: string | null
}

export interface ExtractionResult {
  extractions: ExtractedVaccination[]
  total_found: number
  low_confidence_count: number
  unrecognized_products: string[]
  warnings: string[]
  processing_time_ms: number
}

export interface CreateRecordRequest {
  product_name: string
  administration_date: string
  lot_number?: string
  administered_by?: string
  notes?: string
}

export interface KBAntigen {
  code: string
  full_name: string
  recommendation_level: string
  chapter_ref?: string
  primary_schedule_summary?: string
  boosters_summary?: string
}

export interface KBProduct {
  name: string
  aliases: string[]
  manufacturer?: string
  antigens: string[]
  age_range?: Record<string, number>
  notes?: string
}

export interface DeprecatedProduct {
  name: string
  reason: string
}

export interface RiskGroupItem {
  code: string
  label: string
  recommended: string[]
  severity_threshold?: string
  note?: string
}

export interface RiskGroups {
  clinical_conditions: RiskGroupItem[]
  occupational: RiskGroupItem[]
  pregnancy: RiskGroupItem[]
}

export interface KBFullResponse {
  metadata: {
    version: string
    publication_date: string
    source: string
    reference_url?: string
  }
  antigens: KBAntigen[]
  products: KBProduct[]
  deprecated_products: DeprecatedProduct[]
  risk_groups: RiskGroups
  changelog: string
}
