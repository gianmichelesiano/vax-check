"""Pydantic schemas for the API layer — separate from domain models."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from vaxcheck.domain.person import Sex


class ClinicalConditionOut(BaseModel):
    code: str
    label: str
    onset_date: date | None = None


class PatientOut(BaseModel):
    id: str
    given_name: str
    family_name: str
    birth_date: date
    sex: Sex
    clinical_conditions: list[ClinicalConditionOut] = Field(default_factory=list)
    occupational_situations: list[str] = Field(default_factory=list)
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    age_years: int


class VaccinationRecordOut(BaseModel):
    record_id: str
    patient_id: str
    product_name: str
    administration_date: date
    lot_number: str | None = None
    administered_by: str | None = None
    notes: str | None = None
    created_at: datetime


class AntigenStatusOut(BaseModel):
    antigen: str
    full_name: str | None = None
    is_complete: bool
    doses_received: int
    doses_required: int
    schema_followed: str | None = None
    last_dose_date: date | None = None
    next_dose_due: date | None = None
    notes: list[str] = Field(default_factory=list)
    chapter_ref: str | None = None


class MissingVaccineOut(BaseModel):
    antigen: str
    priority: str
    reason: str
    recommended_schedule: str
    chapter_ref: str | None = None
    age_window: tuple[int, int] | None = None


class FuturePlanItemOut(BaseModel):
    antigen: str
    target_age_years: int | tuple[int, int]
    target_date_estimate: date | None = None
    plan_type: str
    chapter_ref: str | None = None


class ComplianceReportOut(BaseModel):
    patient: PatientOut
    evaluation_date: date
    total_records: int
    antigen_statuses: dict[str, AntigenStatusOut]
    overall_compliance: bool
    missing_vaccines: list[MissingVaccineOut]
    future_plan: list[FuturePlanItemOut]
    engine_used: str
    engine_version: str
    warnings: list[str] = Field(default_factory=list)
    disclaimer: str


class PatientWithRecordsOut(PatientOut):
    records: list[VaccinationRecordOut]


class VaccineProductOut(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    manufacturer: str | None = None
    antigens: list[str]
    age_range: dict[str, Any] | None = None
    notes: str | None = None


class KBAntigenOut(BaseModel):
    code: str
    full_name: str
    recommendation_level: str
    chapter_ref: str | None = None
    primary_schedule_summary: str | None = None
    boosters_summary: str | None = None
    raw: dict[str, Any]


class KBProductOut(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    manufacturer: str | None = None
    antigens: list[str]
    age_range: dict[str, Any] | None = None
    notes: str | None = None


class DeprecatedProductOut(BaseModel):
    name: str
    reason: str


class RiskGroupItemOut(BaseModel):
    code: str
    label: str
    recommended: list[str]
    severity_threshold: str | None = None
    note: str | None = None


class RiskGroupsOut(BaseModel):
    clinical_conditions: list[RiskGroupItemOut] = Field(default_factory=list)
    occupational: list[RiskGroupItemOut] = Field(default_factory=list)
    pregnancy: list[RiskGroupItemOut] = Field(default_factory=list)


class KBFullOut(BaseModel):
    metadata: dict[str, Any]
    antigens: list[KBAntigenOut]
    products: list[KBProductOut]
    deprecated_products: list[DeprecatedProductOut]
    risk_groups: RiskGroupsOut
    changelog: str


class CreatePatientRequest(BaseModel):
    given_name: str = Field(..., min_length=2)
    family_name: str = Field(..., min_length=2)
    birth_date: date
    sex: Sex
    clinical_conditions: list[ClinicalConditionOut] = Field(default_factory=list)
    occupational_situations: list[str] = Field(default_factory=list)
    notes: str | None = None


class UpdatePatientRequest(BaseModel):
    given_name: str | None = Field(None, min_length=2)
    family_name: str | None = Field(None, min_length=2)
    birth_date: date | None = None
    sex: Sex | None = None
    clinical_conditions: list[ClinicalConditionOut] | None = None
    occupational_situations: list[str] | None = None
    notes: str | None = None


class CreateRecordRequest(BaseModel):
    product_name: str
    administration_date: date
    lot_number: str | None = None
    administered_by: str | None = None
    notes: str | None = None
