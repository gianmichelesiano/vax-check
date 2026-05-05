from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from vaxcheck.api.deps import get_db, get_engine, get_kb
from vaxcheck.api.schemas import (
    AntigenStatusOut,
    ComplianceReportOut,
    FuturePlanItemOut,
    MissingVaccineOut,
    PatientOut,
)
from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.persistence.mappers import person_to_domain, record_to_domain
from vaxcheck.persistence.repository import PatientRepository, RecordRepository, ReportRepository
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine

router = APIRouter(tags=["analysis"])


def _report_to_out(report, db_patient, kb: KnowledgeBase | None = None) -> ComplianceReportOut:
    person = report.person
    return ComplianceReportOut(
        patient=PatientOut(
            id=db_patient.id,
            given_name=person.given_name,
            family_name=person.family_name,
            birth_date=person.birth_date,
            sex=person.sex,
            clinical_conditions=[{"code": c.code, "label": c.label, "onset_date": c.onset_date} for c in person.clinical_conditions],
            occupational_situations=list(person.occupational_situations),
            notes=person.notes,
            created_at=db_patient.created_at,
            updated_at=db_patient.updated_at,
            age_years=person.age_years,
        ),
        evaluation_date=report.evaluation_date,
        total_records=report.total_records,
        antigen_statuses={
            k: AntigenStatusOut(
                antigen=v.antigen,
                full_name=kb.antigens[k].full_name if kb and k in kb.antigens else None,
                is_complete=v.is_complete,
                doses_received=v.doses_received,
                doses_required=v.doses_required,
                schema_followed=v.schema_followed,
                last_dose_date=v.last_dose_date,
                next_dose_due=v.next_dose_due,
                notes=v.notes,
                chapter_ref=v.chapter_ref,
            )
            for k, v in report.antigen_statuses.items()
        },
        overall_compliance=report.overall_compliance,
        missing_vaccines=[
            MissingVaccineOut(
                antigen=m.antigen,
                priority=m.priority.value,
                reason=m.reason,
                recommended_schedule=m.recommended_schedule,
                chapter_ref=m.chapter_ref,
                age_window=m.age_window,
            )
            for m in report.missing_vaccines
        ],
        future_plan=[
            FuturePlanItemOut(
                antigen=f.antigen,
                target_age_years=f.target_age_years,
                target_date_estimate=f.target_date_estimate,
                plan_type=f.plan_type,
                chapter_ref=f.chapter_ref,
            )
            for f in report.future_plan
        ],
        engine_used=report.engine_used,
        engine_version=report.engine_version,
        warnings=report.warnings,
        disclaimer=report.disclaimer,
    )


@router.post("/patients/{patient_id}/analyze", response_model=ComplianceReportOut)
def analyze_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    kb: KnowledgeBase = Depends(get_kb),
    engine: DeterministicRuleEngine = Depends(get_engine),
):
    patient_repo = PatientRepository(db)
    db_patient = patient_repo.get(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    person = person_to_domain(db_patient)

    record_repo = RecordRepository(db)
    db_records = record_repo.list_for_patient(patient_id)
    records = [record_to_domain(r) for r in db_records]

    report = engine.evaluate(person, records, kb)
    report_repo = ReportRepository(db)
    report_repo.save(report, patient_id)
    db.commit()

    return _report_to_out(report, db_patient, kb)


@router.get("/patients/{patient_id}/reports/latest", response_model=ComplianceReportOut | None)
def get_latest_report(
    patient_id: str,
    db: Session = Depends(get_db),
):
    patient_repo = PatientRepository(db)
    db_patient = patient_repo.get(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    report_repo = ReportRepository(db)
    db_report = report_repo.get_latest_for_patient(patient_id)
    if db_report is None:
        return None

    from vaxcheck.persistence.mappers import report_to_domain
    report = report_to_domain(db_report)
    return _report_to_out(report, db_patient)
