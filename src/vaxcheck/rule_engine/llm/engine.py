from __future__ import annotations

import json
import re
from datetime import date

from vaxcheck.domain.compliance import ComplianceReport
from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.rule_engine.llm.prompts import SYSTEM_PROMPT, build_evaluation_prompt
from vaxcheck.rule_engine.llm.providers.base import LLMProvider


def _find_balanced_json(text: str) -> str | None:
    """Extract the first balanced JSON object from text that may have prefixes."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start=start):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def extract_json(text: str) -> object:
    """Robust JSON extraction from LLM output that may include markdown, reasoning, or prefixes."""
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try balanced JSON extraction (handles reasoning text before JSON)
    balanced = _find_balanced_json(text)
    if balanced:
        try:
            return json.loads(balanced)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract valid JSON from LLM response: {text[:500]}...")


class LLMRuleEngine:
    """Engine B: uses an LLM with the KB in context for evaluation."""

    name = "llm"

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.version = f"0.1.0-{provider.__class__.__name__}"

    def evaluate(
        self,
        person: Person,
        records: list[VaccinationRecord],
        kb: KnowledgeBase,
        evaluation_date: date | None = None,
    ) -> ComplianceReport:
        eval_date = evaluation_date or date.today()

        prompt = build_evaluation_prompt(person, records, kb, eval_date)
        response = self.provider.complete(
            prompt, system=SYSTEM_PROMPT, max_tokens=4096, temperature=0.0
        )

        report_json = extract_json(response)
        if not isinstance(report_json, dict):
            raise ValueError(
                f"LLM response is not a JSON object: {type(report_json)}. "
                f"Raw response: {response[:800]}"
            )

        # Sanitize future_plan: drop items with null target_age_years (LLM quirk)
        raw_future = report_json.get("future_plan", [])
        clean_future: list[dict] = []
        if isinstance(raw_future, list):
            for item in raw_future:
                if isinstance(item, dict) and item.get("target_age_years") is not None:
                    clean_future.append(item)
                else:
                    clean_future.append({**item, "target_age_years": 99})  # fallback

        # Build ComplianceReport from LLM response
        return ComplianceReport(
            person=person,
            evaluation_date=eval_date,
            total_records=len(records),
            antigen_statuses=report_json.get("antigen_statuses", {}),
            overall_compliance=report_json.get("overall_compliance", False),
            missing_vaccines=report_json.get("missing_vaccines", []),
            future_plan=clean_future,
            engine_used="llm",
            engine_version=self.version,
            warnings=report_json.get("warnings", []),
        )
