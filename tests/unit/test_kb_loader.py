from __future__ import annotations

import pytest

from vaxcheck.kb.loader import load_knowledge_base


def test_loads_all_files(kb):
    assert kb.version == "2026.1"
    assert len(kb.products) > 0
    assert len(kb.antigens) > 0
    assert len(kb.age_milestones) > 0


def test_products_have_antigens(kb):
    hexa = kb.find_product("Infanrix hexa")
    assert hexa is not None
    assert set(hexa.antigens) == {"D", "T", "Pa", "IPV", "Hib", "HBV"}


def test_antigen_rules_have_schedule(kb):
    dtp = kb.get_antigen_rule("DTP")
    assert dtp is not None
    assert "primary_schedule" in dtp.raw or dtp.primary_schedule


def test_risk_groups_loaded(kb):
    assert "clinical_conditions" in kb.risk_groups


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_knowledge_base(tmp_path)
