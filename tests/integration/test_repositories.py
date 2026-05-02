from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from vaxcheck.domain.compliance import (
    ComplianceReport,
    MissingVaccine,
    MissingVaccinePriority,
)
from vaxcheck.domain.person import ClinicalCondition, Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.persistence.models import Base
from vaxcheck.persistence.repository import (
    PatientRepository,
    RecordRepository,
    ReportRepository,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def _make_person(given_name: str = "Mario", family_name: str = "Rossi") -> Person:
    return Person(
        given_name=given_name,
        family_name=family_name,
        birth_date=date(2020, 3, 15),
        sex=Sex.MALE,
        clinical_conditions=[ClinicalCondition(code="asplenia", label="Asplenia")],
        notes="Test patient",
    )


def _make_record(product_name: str = "Infanrix hexa", admin_date: date | None = None) -> VaccinationRecord:
    return VaccinationRecord(
        product_name=product_name,
        administration_date=admin_date or date(2020, 5, 15),
    )


class TestPatientRepository:
    def test_create_and_get(self, session: Session) -> None:
        repo = PatientRepository(session)
        person = _make_person()
        db_patient = repo.create(person)
        session.commit()

        retrieved = repo.get(db_patient.id)
        assert retrieved is not None
        assert retrieved.given_name == "Mario"
        assert retrieved.family_name == "Rossi"

    def test_list_all(self, session: Session) -> None:
        repo = PatientRepository(session)
        repo.create(_make_person("Mario", "Rossi"))
        repo.create(_make_person("Anna", "Bianchi"))
        session.commit()

        patients = repo.list_all()
        assert len(patients) == 2
        assert patients[0].family_name <= patients[1].family_name  # alphabetical order

    def test_search(self, session: Session) -> None:
        repo = PatientRepository(session)
        repo.create(_make_person("Mario", "Rossi"))
        repo.create(_make_person("Anna", "Bianchi"))
        session.commit()

        results = repo.search("Ross")
        assert len(results) == 1
        assert results[0].family_name == "Rossi"

    def test_search_case_sensitive_like(self, session: Session) -> None:
        repo = PatientRepository(session)
        repo.create(_make_person("Mario", "Rossi"))
        session.commit()

        # SQLite LIKE is case-insensitive for ASCII
        results = repo.search("mario")
        assert len(results) >= 1

    def test_update(self, session: Session) -> None:
        repo = PatientRepository(session)
        db_patient = repo.create(_make_person())
        session.commit()

        updated_person = _make_person(given_name="Marco", family_name="Neri")
        result = repo.update(db_patient.id, updated_person)
        assert result is not None
        assert result.given_name == "Marco"
        assert result.family_name == "Neri"
        session.commit()

        retrieved = repo.get(db_patient.id)
        assert retrieved is not None
        assert retrieved.given_name == "Marco"

    def test_save_create_new(self, session: Session) -> None:
        repo = PatientRepository(session)
        person = _make_person()
        db_patient = repo.save(person)
        session.commit()
        assert db_patient.id is not None
        assert repo.get(db_patient.id) is not None

    def test_save_update_existing(self, session: Session) -> None:
        repo = PatientRepository(session)
        db_patient = repo.create(_make_person())
        session.commit()

        updated = _make_person(given_name="Giulia")
        result = repo.save(updated, patient_id=db_patient.id)
        session.commit()
        assert result.given_name == "Giulia"
        # Should not create a new patient
        assert len(repo.list_all()) == 1

    def test_delete(self, session: Session) -> None:
        repo = PatientRepository(session)
        db_patient = repo.create(_make_person())
        session.commit()

        assert repo.delete(db_patient.id) is True
        session.commit()
        assert repo.get(db_patient.id) is None


class TestRecordRepository:
    def test_add_and_list(self, session: Session) -> None:
        patient_repo = PatientRepository(session)
        db_patient = patient_repo.create(_make_person())
        session.commit()

        record_repo = RecordRepository(session)
        r1 = _make_record("Infanrix hexa", date(2020, 5, 15))
        r2 = _make_record("Prevenar 13", date(2020, 7, 15))
        record_repo.add(r1, db_patient.id)
        record_repo.add(r2, db_patient.id)
        session.commit()

        records = record_repo.list_for_patient(db_patient.id)
        assert len(records) == 2
        assert records[0].administration_date <= records[1].administration_date

    def test_delete(self, session: Session) -> None:
        patient_repo = PatientRepository(session)
        db_patient = patient_repo.create(_make_person())
        session.commit()

        record_repo = RecordRepository(session)
        r = _make_record()
        db_record = record_repo.add(r, db_patient.id)
        session.commit()

        assert record_repo.delete(db_record.record_id) is True
        session.commit()
        assert record_repo.get(db_record.record_id) is None

    def test_replace_all_for_patient(self, session: Session) -> None:
        patient_repo = PatientRepository(session)
        db_patient = patient_repo.create(_make_person())
        session.commit()

        record_repo = RecordRepository(session)
        r1 = _make_record("Vaccine A", date(2020, 1, 1))
        r2 = _make_record("Vaccine B", date(2020, 2, 1))
        record_repo.add(r1, db_patient.id)
        record_repo.add(r2, db_patient.id)
        session.commit()

        new_records = [
            _make_record("Vaccine C", date(2020, 3, 1)),
            _make_record("Vaccine D", date(2020, 4, 1)),
            _make_record("Vaccine E", date(2020, 5, 1)),
        ]
        record_repo.replace_all_for_patient(db_patient.id, new_records)
        session.commit()

        records = record_repo.list_for_patient(db_patient.id)
        assert len(records) == 3
        product_names = {r.product_name for r in records}
        assert product_names == {"Vaccine C", "Vaccine D", "Vaccine E"}


class TestReportRepository:
    def test_save_and_get_latest(self, session: Session) -> None:
        patient_repo = PatientRepository(session)
        db_patient = patient_repo.create(_make_person())
        session.commit()

        report_repo = ReportRepository(session)
        person = _make_person()
        report1 = ComplianceReport(
            person=person,
            evaluation_date=date(2026, 1, 1),
            total_records=3,
            antigen_statuses={},
            overall_compliance=True,
            missing_vaccines=[],
            future_plan=[],
            engine_used="deterministic",
            engine_version="1.0",
        )
        report2 = ComplianceReport(
            person=person,
            evaluation_date=date(2026, 3, 1),
            total_records=5,
            antigen_statuses={},
            overall_compliance=False,
            missing_vaccines=[
                MissingVaccine(
                    antigen="MenB",
                    priority=MissingVaccinePriority.DUE_NOW,
                    reason="Mai fatto",
                    recommended_schedule="2 dosi",
                )
            ],
            future_plan=[],
            engine_used="deterministic",
            engine_version="1.0",
        )

        report_repo.save(report1, db_patient.id)
        report_repo.save(report2, db_patient.id)
        session.commit()

        latest = report_repo.get_latest_for_patient(db_patient.id)
        assert latest is not None
        assert latest.evaluation_date == date(2026, 3, 1)
        assert latest.overall_compliance is False

    def test_delete_older_than(self, session: Session) -> None:
        patient_repo = PatientRepository(session)
        db_patient = patient_repo.create(_make_person())
        session.commit()

        report_repo = ReportRepository(session)
        person = _make_person()
        for i in range(5):
            report = ComplianceReport(
                person=person,
                evaluation_date=date(2026, i + 1, 1),
                total_records=i,
                antigen_statuses={},
                overall_compliance=True,
                missing_vaccines=[],
                future_plan=[],
                engine_used="deterministic",
                engine_version="1.0",
            )
            report_repo.save(report, db_patient.id)
        session.commit()

        deleted = report_repo.delete_older_than(db_patient.id, keep_count=2)
        session.commit()
        assert deleted == 3

        all_reports = report_repo.list_for_patient(db_patient.id)
        assert len(all_reports) == 2

    def test_cascade_delete_with_patient(self, session: Session) -> None:
        patient_repo = PatientRepository(session)
        db_patient = patient_repo.create(_make_person())
        session.commit()

        report_repo = ReportRepository(session)
        person = _make_person()
        report = ComplianceReport(
            person=person,
            evaluation_date=date(2026, 1, 1),
            total_records=0,
            antigen_statuses={},
            overall_compliance=True,
            missing_vaccines=[],
            future_plan=[],
            engine_used="deterministic",
            engine_version="1.0",
        )
        db_report = report_repo.save(report, db_patient.id)
        session.commit()

        patient_repo.delete(db_patient.id)
        session.commit()

        assert report_repo.get(db_report.id) is None
