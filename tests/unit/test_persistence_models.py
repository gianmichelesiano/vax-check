from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from vaxcheck.persistence.models import Base, ComplianceReportDB, PatientDB, VaccinationRecordDB


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


class TestPatientDB:
    def test_create_minimal_patient(self, session: Session) -> None:
        patient = PatientDB(
            given_name="Mario",
            family_name="Rossi",
            birth_date=date(2020, 3, 15),
            sex="M",
        )
        session.add(patient)
        session.commit()

        retrieved = session.get(PatientDB, patient.id)
        assert retrieved is not None
        assert retrieved.given_name == "Mario"
        assert retrieved.family_name == "Rossi"
        assert retrieved.birth_date == date(2020, 3, 15)
        assert retrieved.sex == "M"
        assert retrieved.clinical_conditions == []
        assert retrieved.occupational_situations == []
        assert retrieved.notes is None
        assert retrieved.created_at is not None

    def test_clinical_conditions_json(self, session: Session) -> None:
        patient = PatientDB(
            given_name="Anna",
            family_name="Bianchi",
            birth_date=date(1985, 7, 20),
            sex="F",
            clinical_conditions=[
                {"code": "diabetes_with_organ_impact", "label": "Diabete con complicanze", "onset_date": "2015-03-01"}
            ],
            occupational_situations=["healthcare_worker"],
        )
        session.add(patient)
        session.commit()

        retrieved = session.get(PatientDB, patient.id)
        assert retrieved is not None
        assert len(retrieved.clinical_conditions) == 1
        assert retrieved.clinical_conditions[0]["code"] == "diabetes_with_organ_impact"
        assert retrieved.clinical_conditions[0]["onset_date"] == "2015-03-01"
        assert "healthcare_worker" in retrieved.occupational_situations

    def test_id_generated_on_create(self, session: Session) -> None:
        patient = PatientDB(
            given_name="Test",
            family_name="User",
            birth_date=date(2000, 1, 1),
            sex="X",
        )
        session.add(patient)
        session.commit()
        assert patient.id is not None
        assert len(patient.id) == 36  # UUID string


class TestVaccinationRecordDB:
    def test_create_record_with_patient(self, session: Session) -> None:
        patient = PatientDB(
            given_name="Luca",
            family_name="Verdi",
            birth_date=date(2022, 5, 10),
            sex="M",
        )
        session.add(patient)
        session.commit()

        record = VaccinationRecordDB(
            record_id="550e8400-e29b-41d4-a716-446655440000",
            patient_id=patient.id,
            product_name="Infanrix hexa",
            administration_date=date(2022, 7, 10),
            lot_number="ABC-123",
            administered_by="Dr. Bianchi",
        )
        session.add(record)
        session.commit()

        retrieved = session.get(VaccinationRecordDB, record.record_id)
        assert retrieved is not None
        assert retrieved.product_name == "Infanrix hexa"
        assert retrieved.patient_id == patient.id
        assert retrieved.lot_number == "ABC-123"

    def test_cascade_delete(self, session: Session) -> None:
        patient = PatientDB(
            given_name="Test",
            family_name="Cascade",
            birth_date=date(2000, 1, 1),
            sex="F",
        )
        session.add(patient)
        session.commit()

        record = VaccinationRecordDB(
            record_id="660e8400-e29b-41d4-a716-446655440001",
            patient_id=patient.id,
            product_name="Test vaccine",
            administration_date=date(2024, 1, 1),
        )
        session.add(record)
        session.commit()

        session.delete(patient)
        session.commit()

        assert session.get(VaccinationRecordDB, record.record_id) is None


class TestComplianceReportDB:
    def test_create_report(self, session: Session) -> None:
        patient = PatientDB(
            given_name="Clara",
            family_name="Siano",
            birth_date=date(2018, 1, 15),
            sex="F",
        )
        session.add(patient)
        session.commit()

        report = ComplianceReportDB(
            patient_id=patient.id,
            evaluation_date=date(2026, 5, 1),
            report_json={
                "person": {"given_name": "Clara", "family_name": "Siano"},
                "overall_compliance": True,
                "antigen_statuses": {},
                "missing_vaccines": [],
                "future_plan": [],
            },
            engine_used="deterministic",
            engine_version="1.0",
            overall_compliance=True,
        )
        session.add(report)
        session.commit()

        retrieved = session.get(ComplianceReportDB, report.id)
        assert retrieved is not None
        assert retrieved.overall_compliance is True
        assert retrieved.engine_used == "deterministic"
        assert retrieved.report_json["overall_compliance"] is True

    def test_cascade_delete(self, session: Session) -> None:
        patient = PatientDB(
            given_name="Test",
            family_name="ReportCascade",
            birth_date=date(2000, 1, 1),
            sex="F",
        )
        session.add(patient)
        session.commit()

        report = ComplianceReportDB(
            patient_id=patient.id,
            evaluation_date=date(2026, 1, 1),
            report_json={"test": True},
            engine_used="deterministic",
            engine_version="1.0",
            overall_compliance=True,
        )
        session.add(report)
        session.commit()

        session.delete(patient)
        session.commit()

        assert session.get(ComplianceReportDB, report.id) is None
