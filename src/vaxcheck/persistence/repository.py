"""CRUD repositories for VaxCheck persistence."""

from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from vaxcheck.domain.compliance import ComplianceReport
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.persistence.mappers import (
    patient_from_domain,
    record_from_domain,
    report_from_domain,
)
from vaxcheck.persistence.models import (
    ComplianceReportDB,
    PatientDB,
    VaccinationRecordDB,
)


class PatientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, person: Person) -> PatientDB:
        db_patient = patient_from_domain(person)
        self.session.add(db_patient)
        return db_patient

    def get(self, patient_id: str) -> PatientDB | None:
        return self.session.get(PatientDB, patient_id)

    def get_by_name(self, family_name: str, given_name: str) -> list[PatientDB]:
        return (
            self.session.query(PatientDB)
            .filter(PatientDB.family_name == family_name, PatientDB.given_name == given_name)
            .all()
        )

    def list_all(self) -> list[PatientDB]:
        return self.session.query(PatientDB).order_by(PatientDB.family_name, PatientDB.given_name).all()

    def search(self, query: str) -> list[PatientDB]:
        pattern = f"%{query}%"
        return (
            self.session.query(PatientDB)
            .filter(
                PatientDB.family_name.like(pattern) | PatientDB.given_name.like(pattern)
            )
            .order_by(PatientDB.family_name, PatientDB.given_name)
            .all()
        )

    def update(self, patient_id: str, person: Person) -> PatientDB | None:
        db_patient = self.session.get(PatientDB, patient_id)
        if db_patient is None:
            return None
        db_patient.given_name = person.given_name
        db_patient.family_name = person.family_name
        db_patient.birth_date = person.birth_date
        db_patient.sex = person.sex.value
        db_patient.clinical_conditions = [c.model_dump(mode="json") for c in person.clinical_conditions]
        db_patient.occupational_situations = list(person.occupational_situations)
        db_patient.notes = person.notes
        return db_patient

    def save(self, person: Person, patient_id: str | None = None) -> PatientDB:
        if patient_id:
            updated = self.update(patient_id, person)
            if updated is not None:
                return updated
        return self.create(person)

    def delete(self, patient_id: str) -> bool:
        db_patient = self.session.get(PatientDB, patient_id)
        if db_patient is None:
            return False
        self.session.delete(db_patient)
        return True


class RecordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, record: VaccinationRecord, patient_id: str) -> VaccinationRecordDB:
        db_record = record_from_domain(record, patient_id)
        self.session.add(db_record)
        return db_record

    def get(self, record_id: str) -> VaccinationRecordDB | None:
        return self.session.get(VaccinationRecordDB, record_id)

    def list_for_patient(self, patient_id: str) -> list[VaccinationRecordDB]:
        return (
            self.session.query(VaccinationRecordDB)
            .filter(VaccinationRecordDB.patient_id == patient_id)
            .order_by(VaccinationRecordDB.administration_date)
            .all()
        )

    def delete(self, record_id: str) -> bool:
        db_record = self.session.get(VaccinationRecordDB, record_id)
        if db_record is None:
            return False
        self.session.delete(db_record)
        return True

    def delete_all_for_patient(self, patient_id: str) -> None:
        self.session.execute(
            delete(VaccinationRecordDB).where(VaccinationRecordDB.patient_id == patient_id)
        )

    def replace_all_for_patient(self, patient_id: str, records: list[VaccinationRecord]) -> None:
        self.delete_all_for_patient(patient_id)
        for record in records:
            self.add(record, patient_id)


class ReportRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, report: ComplianceReport, patient_id: str) -> ComplianceReportDB:
        db_report = report_from_domain(report, patient_id)
        self.session.add(db_report)
        return db_report

    def get(self, report_id: str) -> ComplianceReportDB | None:
        return self.session.get(ComplianceReportDB, report_id)

    def list_for_patient(self, patient_id: str) -> list[ComplianceReportDB]:
        return (
            self.session.query(ComplianceReportDB)
            .filter(ComplianceReportDB.patient_id == patient_id)
            .order_by(ComplianceReportDB.evaluation_date.desc())
            .all()
        )

    def get_latest_for_patient(self, patient_id: str) -> ComplianceReportDB | None:
        return (
            self.session.query(ComplianceReportDB)
            .filter(ComplianceReportDB.patient_id == patient_id)
            .order_by(ComplianceReportDB.evaluation_date.desc())
            .first()
        )

    def delete_older_than(self, patient_id: str, keep_count: int = 20) -> int:
        all_reports = (
            self.session.query(ComplianceReportDB)
            .filter(ComplianceReportDB.patient_id == patient_id)
            .order_by(ComplianceReportDB.evaluation_date.desc())
            .all()
        )
        to_delete = all_reports[keep_count:]
        for report in to_delete:
            self.session.delete(report)
        return len(to_delete)
