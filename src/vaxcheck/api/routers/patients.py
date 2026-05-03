from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from vaxcheck.api.deps import get_db
from vaxcheck.api.schemas import (
    CreatePatientRequest,
    PatientOut,
    PatientWithRecordsOut,
    UpdatePatientRequest,
)
from vaxcheck.domain.person import ClinicalCondition, Person
from vaxcheck.persistence.mappers import person_to_domain, record_to_domain
from vaxcheck.persistence.repository import PatientRepository, RecordRepository

router = APIRouter(tags=["patients"])


def _patient_out(db_patient, age_years: int) -> PatientOut:
    return PatientOut(
        id=db_patient.id,
        given_name=db_patient.given_name,
        family_name=db_patient.family_name,
        birth_date=db_patient.birth_date,
        sex=db_patient.sex,
        clinical_conditions=db_patient.clinical_conditions,
        occupational_situations=db_patient.occupational_situations,
        notes=db_patient.notes,
        created_at=db_patient.created_at,
        updated_at=db_patient.updated_at,
        age_years=age_years,
    )


@router.get("/patients", response_model=list[PatientOut])
def list_patients(
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    repo = PatientRepository(db)
    if search:
        db_patients = repo.search(search)
    else:
        db_patients = repo.list_all()

    result: list[PatientOut] = []
    for db_p in db_patients:
        person = person_to_domain(db_p)
        result.append(_patient_out(db_p, person.age_years))
    return result


@router.post("/patients", response_model=PatientOut, status_code=201)
def create_patient(
    body: CreatePatientRequest,
    db: Session = Depends(get_db),
):
    person = Person(
        given_name=body.given_name,
        family_name=body.family_name,
        birth_date=body.birth_date,
        sex=body.sex,
        clinical_conditions=[ClinicalCondition(**c.model_dump()) for c in body.clinical_conditions],
        occupational_situations=body.occupational_situations,
        notes=body.notes,
    )
    repo = PatientRepository(db)
    db_patient = repo.create(person)
    db.commit()
    return _patient_out(db_patient, person.age_years)


@router.get("/patients/{patient_id}", response_model=PatientWithRecordsOut)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    repo = PatientRepository(db)
    db_patient = repo.get(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    record_repo = RecordRepository(db)
    db_records = record_repo.list_for_patient(patient_id)
    records_out = []
    for db_r in db_records:
        r = record_to_domain(db_r)
        records_out.append({
            "record_id": str(r.record_id),
            "patient_id": patient_id,
            "product_name": r.product_name,
            "administration_date": r.administration_date,
            "lot_number": r.lot_number,
            "administered_by": r.administered_by,
            "notes": r.notes,
            "created_at": db_r.created_at,
        })

    person = person_to_domain(db_patient)
    return {
        **_patient_out(db_patient, person.age_years).model_dump(),
        "records": records_out,
    }


@router.put("/patients/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: str,
    body: UpdatePatientRequest,
    db: Session = Depends(get_db),
):
    repo = PatientRepository(db)
    db_patient = repo.get(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = body.model_dump(exclude_unset=True)
    current = person_to_domain(db_patient)

    if "clinical_conditions" in update_data and update_data["clinical_conditions"] is not None:
        update_data["clinical_conditions"] = [
            ClinicalCondition(**c) for c in update_data["clinical_conditions"]
        ]

    updated_person = current.model_copy(update=update_data)
    db_patient = repo.update(patient_id, updated_person)
    db.commit()
    updated = person_to_domain(db_patient)
    return _patient_out(db_patient, updated.age_years)


@router.delete("/patients/{patient_id}", status_code=204)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    repo = PatientRepository(db)
    if not repo.delete(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    db.commit()
