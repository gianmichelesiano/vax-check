from __future__ import annotations

from datetime import date

from vaxcheck.domain.compliance import AntigenStatus, ComplianceLevel, ComplianceReport, FuturePlanItem, MissingVaccine
from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.normalization.normalizer import group_by_antigen, normalize_records
from vaxcheck.rule_engine.deterministic.checkers.base import AntigenChecker
from vaxcheck.rule_engine.deterministic.checkers.dtp import DTPChecker
from vaxcheck.rule_engine.deterministic.checkers.fsme import FSMEChecker
from vaxcheck.rule_engine.deterministic.checkers.hbv import HBVChecker
from vaxcheck.rule_engine.deterministic.checkers.hib import HibChecker
from vaxcheck.rule_engine.deterministic.checkers.hpv import HPVChecker
from vaxcheck.rule_engine.deterministic.checkers.ipv import IPVChecker
from vaxcheck.rule_engine.deterministic.checkers.menacwy import MenACWYChecker
from vaxcheck.rule_engine.deterministic.checkers.menb import MenBChecker
from vaxcheck.rule_engine.deterministic.checkers.mor import MORChecker
from vaxcheck.rule_engine.deterministic.checkers.pcv import PCVChecker
from vaxcheck.rule_engine.deterministic.checkers.varicella import VaricellaChecker
from vaxcheck.rule_engine.deterministic.future_plan import generate_future_plan


class DeterministicRuleEngine:
    """Engine A: Python-coded rules, 100% reproducible. No network, no LLM."""

    name = "deterministic"
    version = "0.1.0"

    def __init__(self) -> None:
        self.checkers: dict[str, AntigenChecker] = {
            "DTP": DTPChecker(),
            "IPV": IPVChecker(),
            "Hib": HibChecker(),
            "HBV": HBVChecker(),
            "PCV_pediatric": PCVChecker(),
            "MOR": MORChecker(),
            "V": VaricellaChecker(),
            "MenACWY": MenACWYChecker(),
            "MenB": MenBChecker(),
            "HPV": HPVChecker(),
            "FSME": FSMEChecker(),
        }

    def evaluate(
        self,
        person: Person,
        records: list[VaccinationRecord],
        kb: KnowledgeBase,
        evaluation_date: date | None = None,
    ) -> ComplianceReport:
        eval_date = evaluation_date or date.today()

        # Step 1: Normalize records → normalized doses
        doses = normalize_records(records, kb)
        doses_by_antigen = group_by_antigen(doses)

        # Step 2: Run each checker
        statuses: dict[str, AntigenStatus] = {}
        all_missing: list[MissingVaccine] = []
        warnings: list[str] = []

        for antigen_code, checker in self.checkers.items():
            rule = kb.get_antigen_rule(antigen_code)
            if rule is None:
                # Try without _pediatric suffix
                rule = kb.get_antigen_rule(antigen_code.replace("_pediatric", ""))
            if rule is None:
                warnings.append(f"No KB rule for antigen {antigen_code}")
                continue

            relevant_doses = []
            for ag in _get_equivalent_antigens(antigen_code):
                relevant_doses.extend(doses_by_antigen.get(ag, []))

            status = checker.check(person, relevant_doses, rule, eval_date)
            statuses[antigen_code] = status
            all_missing.extend(checker.find_missing(person, status, rule, eval_date))

        # Step 3: Add risk-group antigens from KB schedule not in our checkers
        for ag_code, rule in kb.antigens.items():
            if ag_code not in statuses and ag_code not in ("PCV_adult",):
                statuses[ag_code] = AntigenStatus(
                    antigen=ag_code,
                    is_complete=True,  # Not evaluated by default checkers
                    doses_received=0,
                    doses_required=0,
                    notes=["Non valutato — fuori scope MVP"],
                    chapter_ref=rule.chapter_ref,
                )

        # Step 4: Future plan
        future = generate_future_plan(person, statuses, kb, eval_date)

        # Also collect future items from individual checkers
        for checker in self.checkers.values():
            ag = checker.antigen_code
            if ag in statuses:
                rule = kb.get_antigen_rule(ag)
                if rule:
                    future.extend(
                        checker.plan_future(person, statuses[ag], rule, eval_date)
                    )

        # Deduplicate future plan
        seen_future: set[tuple[str, int]] = set()
        unique_future: list[FuturePlanItem] = []
        for item in future:
            age_target = item.target_age_years
            tag = (item.antigen, age_target if isinstance(age_target, int) else age_target[0])
            if tag not in seen_future:
                seen_future.add(tag)
                unique_future.append(item)
        unique_future.sort(key=lambda x: x.target_date_estimate or date.max)

        # Step 5: Overall compliance — all BASE antigens must be complete
        overall = True
        for ag_code, status in statuses.items():
            rule = kb.get_antigen_rule(ag_code)
            if rule and rule.recommendation_level == ComplianceLevel.BASE:
                if not status.is_complete:
                    overall = False
                    break

        return ComplianceReport(
            person=person,
            evaluation_date=eval_date,
            total_records=len(records),
            antigen_statuses=statuses,
            overall_compliance=overall,
            missing_vaccines=all_missing,
            future_plan=unique_future,
            engine_used="deterministic",
            engine_version=self.version,
            warnings=warnings,
        )


def _get_equivalent_antigens(antigen_code: str) -> list[str]:
    """Return list of antigen codes to search for a given checker antigen code."""
    mapping: dict[str, list[str]] = {
        "DTP": ["D", "d", "T", "Pa", "pa"],
        "IPV": ["IPV"],
        "Hib": ["Hib"],
        "HBV": ["HBV"],
        "PCV_pediatric": ["PCV13", "PCV15", "PCV20", "PCV21", "PPV23"],
        "MOR": ["M", "O", "R"],
        "V": ["V"],
        "MenACWY": ["MenACWY"],
        "MenB": ["MenB"],
        "HPV": ["HPV9"],
        "FSME": ["FSME"],
    }
    return mapping.get(antigen_code, [antigen_code])
