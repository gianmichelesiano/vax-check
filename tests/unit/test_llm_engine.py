from __future__ import annotations

import json
from datetime import date

import pytest

from vaxcheck.domain.compliance import (
    ComplianceReport,
)
from vaxcheck.rule_engine.llm.engine import LLMRuleEngine, extract_json
from vaxcheck.rule_engine.llm.prompts import build_evaluation_prompt


class MockProvider:
    """Mock LLM provider returning a predefined valid JSON response."""

    def __init__(self, response_json: dict | None = None):
        self._response = response_json or _build_mock_clara_response()
        self.last_prompt: str = ""
        self.last_system: str | None = None

    def complete(self, prompt: str, system: str | None = None, max_tokens: int = 4096, temperature: float = 0.0) -> str:
        self.last_prompt = prompt
        self.last_system = system
        return json.dumps(self._response)


def _build_mock_clara_response() -> dict:
    return {
        "overall_compliance": True,
        "antigen_statuses": {
            "DTP": {
                "antigen": "DTP",
                "is_complete": True,
                "doses_received": 5,
                "doses_required": 4,
                "schema_followed": "3+1",
                "notes": [],
                "chapter_ref": "1.1.b/c, 1.2.a",
            },
            "IPV": {
                "antigen": "IPV",
                "is_complete": True,
                "doses_received": 5,
                "doses_required": 5,
                "schema_followed": "3+1",
                "notes": [],
                "chapter_ref": "1.1.d",
            },
            "Hib": {
                "antigen": "Hib",
                "is_complete": True,
                "doses_received": 4,
                "doses_required": 3,
                "notes": [],
                "chapter_ref": "1.1.e",
            },
            "HBV": {
                "antigen": "HBV",
                "is_complete": True,
                "doses_received": 4,
                "doses_required": 3,
                "notes": [],
                "chapter_ref": "1.1.f",
            },
            "MOR": {
                "antigen": "MOR",
                "is_complete": True,
                "doses_received": 2,
                "doses_required": 2,
                "notes": [],
                "chapter_ref": "1.1.k",
            },
            "V": {
                "antigen": "V",
                "is_complete": True,
                "doses_received": 2,
                "doses_required": 2,
                "notes": [],
                "chapter_ref": "1.1.l",
            },
            "MenB": {
                "antigen": "MenB",
                "is_complete": True,
                "doses_received": 0,
                "doses_required": 0,
                "notes": ["Tra le finestre catchup — atteso a 11-15 anni"],
                "chapter_ref": "1.1.i",
            },
        },
        "missing_vaccines": [
            {
                "antigen": "MenB",
                "priority": "catchup_closed",
                "reason": "Finestra catchup MenB infantile chiusa (oltre 5 anni)",
                "recommended_schedule": "2 dosi tra 11-20 anni",
                "chapter_ref": "1.1.i",
                "age_window": [11, 20],
            }
        ],
        "future_plan": [
            {
                "antigen": "DTP",
                "target_age_years": [11, 15],
                "target_date_estimate": "2029-01-15",
                "plan_type": "richiamo",
                "chapter_ref": "1.3.a",
            },
            {
                "antigen": "HPV",
                "target_age_years": [11, 14],
                "target_date_estimate": "2029-01-15",
                "plan_type": "vaccinazione_base",
                "chapter_ref": "1.3.c",
            },
        ],
        "warnings": [],
    }


class TestExtractJSON:
    def test_plain_json(self):
        data = {"key": "value"}
        assert extract_json(json.dumps(data)) == data

    def test_markdown_code_block(self):
        data = {"key": "value"}
        text = f"Here's the result:\n```json\n{json.dumps(data)}\n```\nHope this helps!"
        assert extract_json(text) == data

    def test_json_with_prefix(self):
        data = {"key": "value"}
        text = f"Sure, here you go: {json.dumps(data)}"
        assert extract_json(text) == data

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError):
            extract_json("Not JSON at all")


class TestLLMRuleEngine:
    def test_engine_returns_valid_report(self, kb, clara, clara_records):
        provider = MockProvider()
        engine = LLMRuleEngine(provider)
        report = engine.evaluate(clara, clara_records, kb)

        assert isinstance(report, ComplianceReport)
        assert report.engine_used == "llm"
        assert report.person.given_name == "Clara"
        assert report.total_records == len(clara_records)
        assert "VaxCheck" in report.disclaimer

    def test_engine_uses_system_prompt(self, kb, clara, clara_records):
        provider = MockProvider()
        engine = LLMRuleEngine(provider)
        engine.evaluate(clara, clara_records, kb)
        assert provider.last_system is not None
        assert "UFSP" in provider.last_system

    def test_engine_builds_prompt_with_kb_context(self, kb, clara, clara_records):
        provider = MockProvider()
        engine = LLMRuleEngine(provider)
        engine.evaluate(clara, clara_records, kb)
        assert "Clara" in provider.last_prompt
        assert "Infanrix hexa" in provider.last_prompt
        assert "DTP" in provider.last_prompt

    def test_mock_provider_response_passes_parity_checks(self, kb, clara, clara_records):
        """Verify the mock response is internally consistent."""
        provider = MockProvider()
        engine = LLMRuleEngine(provider)
        report = engine.evaluate(clara, clara_records, kb)

        assert report.overall_compliance is True
        assert report.antigen_statuses["DTP"].is_complete is True
        assert report.antigen_statuses["MOR"].is_complete is True
        assert len(report.future_plan) >= 2

    def test_build_evaluation_prompt_includes_all_sections(self, kb, clara, clara_records):
        prompt = build_evaluation_prompt(clara, clara_records, kb, date.today())
        assert "PAZIENTE" in prompt
        assert "VACCINI RICEVUTI" in prompt
        assert "KNOWLEDGE BASE" in prompt
        assert "CATALOGO PRODOTTI" in prompt
        assert "DATA VALUTAZIONE" in prompt

    def test_skip_if_no_api_key(self, kb, clara, clara_records):
        """Real Claude test — skipped if no API key."""
        import os

        if "ANTHROPIC_API_KEY" not in os.environ:
            pytest.skip("ANTHROPIC_API_KEY not set — skipping real LLM test")
