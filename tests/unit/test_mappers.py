from __future__ import annotations

import uuid
from datetime import date

from vaxcheck.domain.compliance import (
    AntigenStatus,
    ComplianceReport,
    FuturePlanItem,
    MissingVaccine,
    MissingVaccinePriority,
)
from vaxcheck.domain.person import ClinicalCondition, Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.persistence.mappers import (
    patient_from_domain,
    person_to_domain,
    record_from_domain,
    record_to_domain,
    report_from_domain,
    report_to_domain,
)


class TestPatientMapper:
    def test_round_trip_minimal(self) -> None:
        person = Person(
            given_name="Mario",
            family_name="Rossi",
            birth_date=date(2020, 3, 15),
            sex=Sex.MALE,
        )
        db_patient = patient_from_domain(person)
        assert db_patient.given_name == "Mario"
        assert db_patient.sex == "M"

        restored = person_to_domain(db_patient)
        assert restored.given_name == person.given_name
        assert restored.family_name == person.family_name
        assert restored.birth_date == person.birth_date
        assert restored.sex == person.sex
        assert restored.clinical_conditions == []
        assert restored.occupational_situations == []
        assert restored.notes is None

    def test_round_trip_with_conditions(self) -> None:
        person = Person(
            given_name="Anna",
            family_name="Bianchi",
            birth_date=date(1985, 7, 20),
            sex=Sex.FEMALE,
            clinical_conditions=[
                ClinicalCondition(code="diabetes", label="Diabete", onset_date=date(2015, 3, 1)),
                ClinicalCondition(code="asplenia", label="Asplenia"),
            ],
            occupational_situations=["healthcare_worker", "veterinarian"],
            notes="Paziente a rischio",
        )
        db_patient = patient_from_domain(person)
        assert len(db_patient.clinical_conditions) == 2
        assert db_patient.clinical_conditions[0]["code"] == "diabetes"
        assert "healthcare_worker" in db_patient.occupational_situations

        restored = person_to_domain(db_patient)
        assert len(restored.clinical_conditions) == 2
        assert restored.clinical_conditions[0].code == "diabetes"
        assert restored.clinical_conditions[0].label == "Diabete"
        assert restored.clinical_conditions[0].onset_date == date(2015, 3, 1)
        assert restored.clinical_conditions[1].onset_date is None
        assert restored.occupational_situations == ["healthcare_worker", "veterinarian"]
        assert restored.notes == "Paziente a rischio"

    def test_patient_id_passed(self) -> None:
        person = Person(
            given_name="Test",
            family_name="ID",
            birth_date=date(2000, 1, 1),
            sex=Sex.OTHER,
        )
        custom_id = str(uuid.uuid4())
        db_patient = patient_from_domain(person, patient_id=custom_id)
        assert db_patient.id == custom_id

    def test_patient_id_none_uses_default(self) -> None:
        person = Person(
            given_name="Test",
            family_name="AutoID",
            birth_date=date(2000, 1, 1),
            sex=Sex.OTHER,
        )
        db_patient = patient_from_domain(person)
        # ID default is a callable that fires on flush, not construction.
        # When patient_id is None, the mapper omits it, letting the DB default handle it.
        assert db_patient.id is None  # not set until flush


class TestRecordMapper:
    def test_round_trip(self) -> None:
        record_id = uuid.uuid4()
        record = VaccinationRecord(
            product_name="Infanrix hexa",
            administration_date=date(2024, 5, 10),
            lot_number="ABC-123",
            administered_by="Dr. Bianchi",
            notes="Prima dose",
            record_id=record_id,
        )
        db_record = record_from_domain(record, patient_id="patient-1")
        assert db_record.record_id == str(record_id)
        assert db_record.patient_id == "patient-1"
        assert db_record.product_name == "Infanrix hexa"

        restored = record_to_domain(db_record)
        assert restored.product_name == record.product_name
        assert restored.administration_date == record.administration_date
        assert restored.lot_number == "ABC-123"
        assert restored.administered_by == "Dr. Bianchi"
        assert restored.notes == "Prima dose"
        assert restored.record_id == record_id

    def test_round_trip_minimal(self) -> None:
        record = VaccinationRecord(
            product_name="Prevenar 13",
            administration_date=date(2024, 6, 15),
        )
        db_record = record_from_domain(record, patient_id="p2")
        restored = record_to_domain(db_record)
        assert restored.product_name == "Prevenar 13"
        assert restored.lot_number is None
        assert restored.administered_by is None
        assert restored.notes is None


class TestReportMapper:
    def _make_person(self) -> Person:
        return Person(
            given_name="Clara",
            family_name="Siano",
            birth_date=date(2018, 1, 15),
            sex=Sex.FEMALE,
        )

    def test_round_trip(self) -> None:
        person = self._make_person()
        report = ComplianceReport(
            person=person,
            evaluation_date=date(2026, 5, 1),
            total_records=14,
            antigen_statuses={
                "D": AntigenStatus(antigen="D", is_complete=True, doses_received=6, doses_required=5)
            },
            overall_compliance=False,
            missing_vaccines=[
                MissingVaccine(
                    antigen="MenB",
                    priority=MissingVaccinePriority.UPCOMING,
                    reason="Mai somministrato",
                    recommended_schedule="2 dosi a 2-6 mesi",
                )
            ],
            future_plan=[
                FuturePlanItem(
                    antigen="dTpa",
                    target_age_years=25,
                    plan_type="booster",
                )
            ],
            engine_used="deterministic",
            engine_version="1.0.0",
            warnings=["Attenzione: MenB mancante"],
        )

        db_report = report_from_domain(report, patient_id="p1")
        assert db_report.patient_id == "p1"
        assert db_report.overall_compliance is False
        assert db_report.engine_used == "deterministic"
        assert db_report.engine_version == "1.0.0"

        restored = report_to_domain(db_report)
        assert restored.person.given_name == "Clara"
        assert restored.person.family_name == "Siano"
        assert restored.evaluation_date == date(2026, 5, 1)
        assert restored.total_records == 14
        assert restored.overall_compliance is False
        assert restored.engine_used == "deterministic"
        assert restored.engine_version == "1.0.0"
        assert len(restored.antigen_statuses) == 1
        assert restored.antigen_statuses["D"].is_complete is True
        assert restored.antigen_statuses["D"].doses_received == 6
        assert len(restored.missing_vaccines) == 1
        assert restored.missing_vaccines[0].antigen == "MenB"
        assert restored.missing_vaccines[0].priority == MissingVaccinePriority.UPCOMING
        assert len(restored.future_plan) == 1
        assert restored.future_plan[0].antigen == "dTpa"
        assert restored.future_plan[0].plan_type == "booster"
        assert len(restored.warnings) == 1
