#!/usr/bin/env python3
"""Demo script: evaluate Clara Siano's vaccination booklet with both engines."""
# ruff: noqa: E402 (imports after .env loading)
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

# Allow running from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Load .env before imports (intentional — must run first)
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and line.startswith("export "):
                line = line.removeprefix("export ")
                if "=" in line:
                    key, _, val = line.partition("=")
                    val = val.strip().strip('"').strip("'")
                    os.environ.setdefault(key.strip(), val)

from vaxcheck.domain.person import Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.kb.loader import load_knowledge_base
from vaxcheck.reports.formatter import format_report_italian
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine


def main():
    kb_dir = Path(__file__).resolve().parent.parent / "kb"
    kb = load_knowledge_base(kb_dir)
    print(f"Knowledge base loaded: v{kb.version} ({len(kb.products)} products, {len(kb.antigens)} antigens)")

    clara = Person(
        given_name="Clara",
        family_name="Siano",
        birth_date=date(2018, 1, 15),
        sex=Sex.FEMALE,
    )
    print(f"Patient: {clara.given_name} {clara.family_name}, {clara.age_years} anni")

    clara_records = [
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 3, 21)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2018, 3, 21)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 5, 24)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2018, 5, 24)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 7, 12)),
        VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(2018, 11, 5)),
        VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(2019, 2, 4)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2019, 2, 4)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2019, 10, 15)),
        VaccinationRecord(product_name="Menveo", administration_date=date(2020, 2, 11)),
        VaccinationRecord(product_name="Adacel-Polio", administration_date=date(2024, 4, 23)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 4, 23)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 5, 10)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 11, 11)),
    ]

    # Engine A: Deterministic
    print("\n" + "=" * 70)
    print("ENGINE A — Deterministico")
    print("=" * 70)
    det_engine = DeterministicRuleEngine()
    det_report = det_engine.evaluate(clara, clara_records, kb)
    print(format_report_italian(det_report))

    # Engine B: LLM (any Anthropic-compatible provider)
    print("\n" + "=" * 70)
    print("ENGINE B — LLM (DeepSeek/Claude)")
    print("=" * 70)
    has_key = (
        os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    )
    if has_key:
        try:
            from vaxcheck.rule_engine.llm.engine import LLMRuleEngine

            # Prefer DeepSeek if DEEPSEEK_API_KEY is set, else try Claude
            if os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
                from vaxcheck.rule_engine.llm.providers.deepseek import DeepSeekProvider
                provider = DeepSeekProvider()
            else:
                from vaxcheck.rule_engine.llm.providers.claude import ClaudeProvider
                provider = ClaudeProvider()

            llm_engine = LLMRuleEngine(provider)
            llm_report = llm_engine.evaluate(clara, clara_records, kb)
            print(format_report_italian(llm_report))

            # Show divergences
            print("\n" + "=" * 70)
            print("CONFRONTO ENGINE A vs B")
            print("=" * 70)
            det_missing = {m.antigen for m in det_report.missing_vaccines}
            llm_missing = {m.antigen for m in llm_report.missing_vaccines}
            if det_missing == llm_missing:
                print("✓ Set antigeni mancanti: IDENTICI")
            else:
                print(f"✗ DIVERGENZA mancanti: A={det_missing}, B={llm_missing}")

            if det_report.overall_compliance == llm_report.overall_compliance:
                print("✓ Conformità complessiva: IDENTICA")
            else:
                print(f"✗ DIVERGENZA conformità: A={det_report.overall_compliance}, B={llm_report.overall_compliance}")
        except Exception as e:
            import traceback
            print(f"Engine B error: {e}")
            print(traceback.format_exc())
    else:
        print("No API key found — skipping LLM engine demo.")
        print("Source .env or set ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY.")

    print(f"\nDone. Evaluation date: {date.today()}")


if __name__ == "__main__":
    main()
