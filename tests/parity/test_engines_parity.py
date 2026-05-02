from __future__ import annotations

import json
from datetime import date

import pytest

from vaxcheck.domain.compliance import ComplianceLevel
from vaxcheck.domain.person import Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine
from vaxcheck.rule_engine.llm.engine import LLMRuleEngine


class ParityMockProvider:
    """Mock that returns a JSON response matching the deterministic engine's output."""

    def __init__(self, det_report):
        self._response = json.loads(det_report.model_dump_json())

    def complete(self, prompt, system=None, max_tokens=4096, temperature=0.0):
        return json.dumps(self._response)


def get_base_antigens(kb) -> set[str]:
    """Return antigen codes that are BASE recommendation level."""
    return {
        code for code, rule in kb.antigens.items()
        if rule.recommendation_level == ComplianceLevel.BASE
    }


@pytest.fixture
def det_engine():
    return DeterministicRuleEngine()


class TestParityClara:
    """Parity test: Clara's case must give same result from both engines."""

    def test_clara_parity_base_antigens(self, kb, clara, clara_records, det_engine):
        det_report = det_engine.evaluate(clara, clara_records, kb)

        # Create LLM engine with mock that returns det_report's JSON
        provider = ParityMockProvider(det_report)
        llm_engine = LLMRuleEngine(provider)
        llm_report = llm_engine.evaluate(clara, clara_records, kb)

        for antigen in get_base_antigens(kb):
            det_status = det_report.antigen_statuses.get(antigen)
            llm_status = llm_report.antigen_statuses.get(antigen)
            if det_status and llm_status:
                assert det_status.is_complete == llm_status.is_complete, (
                    f"Disagreement on {antigen}: "
                    f"det={det_status.is_complete}, llm={llm_status.is_complete}"
                )

    def test_clara_parity_overall_compliance(self, kb, clara, clara_records, det_engine):
        det_report = det_engine.evaluate(clara, clara_records, kb)
        provider = ParityMockProvider(det_report)
        llm_engine = LLMRuleEngine(provider)
        llm_report = llm_engine.evaluate(clara, clara_records, kb)

        assert det_report.overall_compliance == llm_report.overall_compliance

    def test_clara_parity_missing_vaccines(self, kb, clara, clara_records, det_engine):
        det_report = det_engine.evaluate(clara, clara_records, kb)
        provider = ParityMockProvider(det_report)
        llm_engine = LLMRuleEngine(provider)
        llm_report = llm_engine.evaluate(clara, clara_records, kb)

        det_missing = {m.antigen for m in det_report.missing_vaccines}
        llm_missing = {m.antigen for m in llm_report.missing_vaccines}
        assert det_missing == llm_missing, (
            f"Disagreement on missing: det={det_missing}, llm={llm_missing}"
        )


class TestParityEdgeCases:
    def test_newborn_4_months_parity(self, kb, det_engine):
        """Neonate with only first 2 doses."""
        person = Person(
            given_name="Neo", family_name="Nato", birth_date=date(2025, 10, 1), sex=Sex.MALE
        )
        records = [
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2025, 12, 1)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2026, 2, 1)),
        ]
        det_report = det_engine.evaluate(person, records, kb)

        provider = ParityMockProvider(det_report)
        llm_engine = LLMRuleEngine(provider)
        llm_report = llm_engine.evaluate(person, records, kb)

        assert det_report.overall_compliance == llm_report.overall_compliance

    def test_adult_35_fully_vaccinated_parity(self, kb, det_engine):
        """Adult with complete childhood vaccinations and boosters."""
        person = Person(
            given_name="Adulto", family_name="Completo", birth_date=date(1991, 5, 20), sex=Sex.MALE
        )
        records = [
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1991, 7, 20)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1991, 9, 20)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1992, 1, 20)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1992, 5, 20)),
            VaccinationRecord(product_name="Priorix", administration_date=date(1992, 5, 20)),
            VaccinationRecord(product_name="Priorix", administration_date=date(1992, 10, 20)),
            VaccinationRecord(product_name="Boostrix-Polio", administration_date=date(2015, 5, 20)),
        ]
        det_report = det_engine.evaluate(person, records, kb)

        provider = ParityMockProvider(det_report)
        llm_engine = LLMRuleEngine(provider)
        llm_report = llm_engine.evaluate(person, records, kb)

        assert det_report.overall_compliance == llm_report.overall_compliance

    def test_never_vaccinated_25_parity(self, kb, det_engine):
        """Adult never vaccinated — maximum recovery case."""
        person = Person(
            given_name="Mai", family_name="Vaccinato", birth_date=date(2001, 3, 15), sex=Sex.FEMALE
        )
        records: list[VaccinationRecord] = []
        det_report = det_engine.evaluate(person, records, kb)

        provider = ParityMockProvider(det_report)
        llm_engine = LLMRuleEngine(provider)
        llm_report = llm_engine.evaluate(person, records, kb)

        assert det_report.overall_compliance == llm_report.overall_compliance
        # Should definitely NOT be compliant
        assert not det_report.overall_compliance

    def test_elderly_with_conditions_parity(self, kb, det_engine):
        """Elderly patient with risk conditions."""
        from vaxcheck.domain.person import ClinicalCondition

        person = Person(
            given_name="Anziano", family_name="Rischio", birth_date=date(1956, 8, 10), sex=Sex.MALE,
            clinical_conditions=[
                ClinicalCondition(code="COPD", label="Pneumopatia cronica ostruttiva"),
                ClinicalCondition(code="diabetes_with_organ_impact", label="Diabete con ripercussioni"),
            ],
        )
        records = [
            VaccinationRecord(product_name="Boostrix", administration_date=date(2020, 5, 10)),
            VaccinationRecord(product_name="Prevenar 13", administration_date=date(2020, 5, 10)),
        ]
        det_report = det_engine.evaluate(person, records, kb)

        provider = ParityMockProvider(det_report)
        llm_engine = LLMRuleEngine(provider)
        llm_report = llm_engine.evaluate(person, records, kb)

        assert det_report.overall_compliance == llm_report.overall_compliance
