from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from vaxcheck.api.deps import get_db
from vaxcheck.api.schemas import CreateRecordRequest, VaccinationRecordOut
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.persistence.repository import PatientRepository, RecordRepository

router = APIRouter(tags=["records"])


@router.post("/patients/{patient_id}/records", response_model=VaccinationRecordOut, status_code=201)
def add_record(
    patient_id: str,
    body: CreateRecordRequest,
    db: Session = Depends(get_db),
):
    patient_repo = PatientRepository(db)
    if patient_repo.get(patient_id) is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    record = VaccinationRecord(
        product_name=body.product_name,
        administration_date=body.administration_date,
        lot_number=body.lot_number,
        administered_by=body.administered_by,
        notes=body.notes,
        record_id=uuid4(),
    )
    repo = RecordRepository(db)
    db_record = repo.add(record, patient_id)
    db.commit()

    return VaccinationRecordOut(
        record_id=db_record.record_id,
        patient_id=db_record.patient_id,
        product_name=db_record.product_name,
        administration_date=db_record.administration_date,
        lot_number=db_record.lot_number,
        administered_by=db_record.administered_by,
        notes=db_record.notes,
        created_at=db_record.created_at,
    )


@router.delete("/patients/{patient_id}/records/{record_id}", status_code=204)
def delete_record(
    patient_id: str,
    record_id: str,
    db: Session = Depends(get_db),
):
    patient_repo = PatientRepository(db)
    if patient_repo.get(patient_id) is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    repo = RecordRepository(db)
    if not repo.delete(record_id):
        raise HTTPException(status_code=404, detail="Record not found")
    db.commit()
