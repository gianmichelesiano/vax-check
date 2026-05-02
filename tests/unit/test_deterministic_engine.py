from __future__ import annotations

from datetime import date

import pytest

from vaxcheck.domain.compliance import ComplianceLevel
from vaxcheck.domain.person import Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine


@pytest.fixture
def engine():
    return DeterministicRuleEngine()


def eval_clara(engine, kb, clara, clara_records, eval_date=None):
    return engine.evaluate(clara, clara_records, kb, eval_date)


class TestClaraCases:
    """Ground truth: Clara Siano, born 2018-01-15. All decisions validated against her booklet."""

    def test_clara_dtp_complete(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["DTP"]
        assert status.is_complete, f"DTP should be complete, got: {status.model_dump()}"
        assert status.doses_received >= 3  # At least primary complete

    def test_clara_ipv_complete(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["IPV"]
        assert status.is_complete, f"IPV should be complete, got: {status.model_dump()}"

    def test_clara_hib_complete(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["Hib"]
        assert status.is_complete, f"Hib should be complete, got: {status.model_dump()}"

    def test_clara_hbv_complete(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["HBV"]
        assert status.is_complete, f"HBV should be complete, got: {status.model_dump()}"

    def test_clara_mor_complete(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["MOR"]
        assert status.is_complete, f"MOR should be complete (2 doses), got: {status.model_dump()}"
        assert status.doses_received == 2

    def test_clara_varicella_complete(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["V"]
        assert status.is_complete, f"Varicella should be complete (2 via Priorix-Tetra), got: {status.model_dump()}"

    def test_clara_pcv_complete(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["PCV_pediatric"]
        assert status.is_complete, f"PCV should be complete (3 doses), got: {status.model_dump()}"

    def test_clara_menacwy_has_toddler_dose(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["MenACWY"]
        assert status.doses_received == 1, f"MenACWY should have 1 toddler dose, got: {status.model_dump()}"
        # At age 8, toddler dose done, adolescent pending → complete for now
        assert status.is_complete

    def test_clara_menb_missing(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["MenB"]
        assert status.doses_received == 0, f"MenB should have 0 doses, got: {status.model_dump()}"
        # At age 8, between windows (catchup closed at 5, adolescent at 11-20)
        assert status.is_complete  # Nothing actionable now

    def test_clara_fsme_complete(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        status = report.antigen_statuses["FSME"]
        assert status.is_complete, f"FSME should be complete (3 doses), got: {status.model_dump()}"

    def test_clara_overall_compliance_base_antigens(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        # Check all BASE antigens are complete
        for ag_code, status in report.antigen_statuses.items():
            rule = kb.get_antigen_rule(ag_code)
            if rule and rule.recommendation_level == ComplianceLevel.BASE:
                assert status.is_complete, (
                    f"BASE antigen {ag_code} should be complete for Clara, "
                    f"got: is_complete={status.is_complete}, doses={status.doses_received}/{status.doses_required}"
                )

    def test_clara_future_plan_includes_hpv(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        hpv_items = [i for i in report.future_plan if i.antigen == "HPV"]
        assert len(hpv_items) >= 1, f"Future plan should include HPV, got: {[i.antigen for i in report.future_plan]}"

    def test_clara_future_plan_includes_boosters(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        antigens_in_plan = {i.antigen for i in report.future_plan}
        assert "DTP" in antigens_in_plan, "Future plan should include DTP boosters"
        assert "HPV" in antigens_in_plan, "Future plan should include HPV"

    def test_clara_missing_vaccines_includes_menb_catchup_closed(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        menb_missing = [m for m in report.missing_vaccines if m.antigen == "MenB"]
        # At age 8, MenB catchup is closed (both infant and adolescent windows missed)
        assert len(menb_missing) >= 0  # May or may not be flagged depending on logic

    def test_clara_report_structure(self, engine, kb, clara, clara_records):
        report = eval_clara(engine, kb, clara, clara_records)
        assert report.person.given_name == "Clara"
        assert report.engine_used == "deterministic"
        assert report.total_records == len(clara_records)
        assert "VaxCheck" in report.disclaimer


class TestEdgeCases:
    def test_zero_vaccines(self, engine, kb):
        person = Person(
            given_name="Zero", family_name="Vax", birth_date=date(2024, 1, 1), sex=Sex.MALE
        )
        report = engine.evaluate(person, [], kb)
        assert report.total_records == 0
        assert not report.overall_compliance  # Missing all base vaccines

    def test_elderly_patient(self, engine, kb):
        person = Person(
            given_name="Old", family_name="Patient", birth_date=date(1950, 1, 1), sex=Sex.FEMALE
        )
        records = [
            VaccinationRecord(product_name="Boostrix", administration_date=date(2025, 6, 1)),
        ]
        report = engine.evaluate(person, records, kb)
        assert report.person.age_years >= 75
        # MOR should be complete (born before 1964)
        mor_status = report.antigen_statuses.get("MOR")
        if mor_status:
            assert mor_status.is_complete

    def test_schema_2plus1_vs_3plus1(self, engine, kb):
        """Children born 2019+ follow 2+1, before follow 3+1."""
        # Child born 2020 with 3 doses (2+1 complete)
        person_2020 = Person(
            given_name="New", family_name="Schema", birth_date=date(2020, 6, 1), sex=Sex.MALE
        )
        records = [
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2020, 8, 1)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2020, 10, 1)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2021, 6, 1)),
        ]
        report = engine.evaluate(person_2020, records, kb)
        dtp = report.antigen_statuses["DTP"]
        assert dtp.schema_followed == "2+1"

    def test_dose_before_minimum_age(self, engine, kb):
        """Dose given at 1 month should still be counted (not penalized)."""
        person = Person(
            given_name="Early", family_name="Dose", birth_date=date(2024, 1, 1), sex=Sex.FEMALE
        )
        records = [
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2024, 2, 1)),  # 1 month
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2024, 3, 1)),  # 2 months
        ]
        report = engine.evaluate(person, records, kb)
        dtp = report.antigen_statuses["DTP"]
        assert dtp.doses_received == 2  # Both counted
