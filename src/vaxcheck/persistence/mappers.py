"""Mappers between Pydantic domain models and SQLAlchemy ORM models."""

from __future__ import annotations

from uuid import UUID

from vaxcheck.domain.compliance import ComplianceReport
from vaxcheck.domain.person import ClinicalCondition, Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.persistence.models import (
    ComplianceReportDB,
    PatientDB,
    VaccinationRecordDB,
)


def patient_from_domain(person: Person, patient_id: str | None = None) -> PatientDB:
    kwargs = {}
    if patient_id is not None:
        kwargs["id"] = patient_id
    return PatientDB(
        given_name=person.given_name,
        family_name=person.family_name,
        birth_date=person.birth_date,
        sex=person.sex.value,
        clinical_conditions=[c.model_dump(mode="json") for c in person.clinical_conditions],
        occupational_situations=list(person.occupational_situations),
        notes=person.notes,
        **kwargs,
    )


def person_to_domain(db_patient: PatientDB) -> Person:
    return Person(
        given_name=db_patient.given_name,
        family_name=db_patient.family_name,
        birth_date=db_patient.birth_date,
        sex=Sex(db_patient.sex),
        clinical_conditions=[ClinicalCondition(**cc) for cc in db_patient.clinical_conditions],
        occupational_situations=list(db_patient.occupational_situations),
        notes=db_patient.notes,
    )


def record_from_domain(record: VaccinationRecord, patient_id: str) -> VaccinationRecordDB:
    return VaccinationRecordDB(
        record_id=str(record.record_id),
        patient_id=patient_id,
        product_name=record.product_name,
        administration_date=record.administration_date,
        lot_number=record.lot_number,
        administered_by=record.administered_by,
        notes=record.notes,
    )


def record_to_domain(db_record: VaccinationRecordDB) -> VaccinationRecord:
    return VaccinationRecord(
        product_name=db_record.product_name,
        administration_date=db_record.administration_date,
        lot_number=db_record.lot_number,
        administered_by=db_record.administered_by,
        notes=db_record.notes,
        record_id=UUID(db_record.record_id),
    )


def report_from_domain(report: ComplianceReport, patient_id: str) -> ComplianceReportDB:
    return ComplianceReportDB(
        patient_id=patient_id,
        evaluation_date=report.evaluation_date,
        report_json=report.model_dump(mode="json"),
        engine_used=report.engine_used,
        engine_version=report.engine_version,
        overall_compliance=report.overall_compliance,
    )


def report_to_domain(db_report: ComplianceReportDB) -> ComplianceReport:
    return ComplianceReport.model_validate(db_report.report_json)
