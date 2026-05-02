from __future__ import annotations

from datetime import date

from vaxcheck.domain.compliance import (
    ComplianceReport,
)
from vaxcheck.domain.knowledge import ComplianceLevel
from vaxcheck.domain.person import Person, Sex
from vaxcheck.domain.vaccination import NormalizedDose, VaccinationRecord


class TestPerson:
    def test_creation_with_age_calculation(self):
        p = Person(
            given_name="Test",
            family_name="User",
            birth_date=date(2020, 1, 1),
            sex=Sex.FEMALE,
        )
        assert p.given_name == "Test"
        assert p.family_name == "User"
        assert p.birth_year == 2020
        assert p.age_years >= 5  # Born in 2020, now 2026+
        assert p.age_months >= 60

    def test_age_boundary_birthday_today(self, monkeypatch):
        """Person whose birthday is exactly today."""
        today = date(2026, 5, 1)

        class MockDate(date):
            @classmethod
            def today(cls):
                return today

        import vaxcheck.domain.person as pm

        monkeypatch.setattr(pm, "date", MockDate)

        p = Person(
            given_name="Bday",
            family_name="Today",
            birth_date=date(2018, 5, 1),
            sex=Sex.MALE,
        )
        assert p.age_years == 8

    def test_age_boundary_birthday_yesterday(self, monkeypatch):
        today = date(2026, 5, 1)

        class MockDate(date):
            @classmethod
            def today(cls):
                return today

        import vaxcheck.domain.person as pm

        monkeypatch.setattr(pm, "date", MockDate)

        p = Person(
            given_name="Bday",
            family_name="Yesterday",
            birth_date=date(2018, 4, 30),
            sex=Sex.MALE,
        )
        assert p.age_years == 8

    def test_age_boundary_birthday_tomorrow(self, monkeypatch):
        today = date(2026, 5, 1)

        class MockDate(date):
            @classmethod
            def today(cls):
                return today

        import vaxcheck.domain.person as pm

        monkeypatch.setattr(pm, "date", MockDate)

        p = Person(
            given_name="Bday",
            family_name="Tomorrow",
            birth_date=date(2018, 5, 2),
            sex=Sex.MALE,
        )
        assert p.age_years == 7


class TestVaccinationRecord:
    def test_serialization_roundtrip(self):
        record = VaccinationRecord(
            product_name="Infanrix hexa",
            administration_date=date(2018, 3, 21),
            lot_number="ABC123",
        )
        data = record.model_dump(mode="json")
        restored = VaccinationRecord(**data)
        assert restored.product_name == record.product_name
        assert restored.administration_date == record.administration_date
        assert restored.lot_number == "ABC123"

    def test_record_id_is_unique(self):
        r1 = VaccinationRecord(product_name="Test", administration_date=date(2020, 1, 1))
        r2 = VaccinationRecord(product_name="Test", administration_date=date(2020, 1, 1))
        assert r1.record_id != r2.record_id


class TestNormalizedDose:
    def test_creation(self):
        dose = NormalizedDose(
            antigen="D",
            administration_date=date(2018, 3, 21),
            source_record_id=VaccinationRecord(
                product_name="Test", administration_date=date(2018, 3, 21)
            ).record_id,
            source_product="Infanrix hexa",
        )
        assert dose.antigen == "D"
        assert dose.dose_strength == "full"


class TestComplianceReport:
    def test_disclaimer_present(self):
        report = ComplianceReport(
            person=Person(
                given_name="X", family_name="Y", birth_date=date(2000, 1, 1), sex=Sex.OTHER
            ),
            evaluation_date=date.today(),
            total_records=0,
            antigen_statuses={},
            overall_compliance=True,
            missing_vaccines=[],
            future_plan=[],
            engine_used="deterministic",
            engine_version="0.1.0",
        )
        assert "VaxCheck" in report.disclaimer
        assert "ausilio" in report.disclaimer


class TestKnowledgeBase:
    def test_find_product_case_insensitive(self, kb):
        product = kb.find_product("infanrix hexa")
        assert product is not None
        assert product.name == "Infanrix hexa"

    def test_find_product_by_alias(self, kb):
        product = kb.find_product("Hexavac")
        assert product is not None
        assert "Infanrix" in product.name

    def test_find_product_missing(self, kb):
        assert kb.find_product("NonExistentVaccine") is None

    def test_get_antigen_rule(self, kb):
        rule = kb.get_antigen_rule("DTP")
        assert rule is not None
        assert rule.full_name == "Difterite, Tetano, Pertosse"
        assert rule.recommendation_level == ComplianceLevel.BASE

    def test_version(self, kb):
        assert kb.version == "2026.1"
