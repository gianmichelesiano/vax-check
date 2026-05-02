from __future__ import annotations

from datetime import date

from vaxcheck.domain.compliance import AntigenStatus, FuturePlanItem, MissingVaccine
from vaxcheck.domain.knowledge import AntigenRule
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import NormalizedDose
from vaxcheck.rule_engine.deterministic.checkers.base import (
    AntigenChecker,
    age_at_date,
    count_relevant_doses,
)


class IPVChecker(AntigenChecker):
    antigen_code = "IPV"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("IPV", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)
        birth_year = person.birth_year

        completion = rule.raw.get("completion_criteria", {})
        if birth_year <= 2018:
            schema = "3+1"
            schema_cfg = completion.get("schema_3plus1", {})
            required = schema_cfg.get("total_doses", 5)
        else:
            schema = "2+1"
            schema_cfg = completion.get("schema_2plus1", {})
            required = schema_cfg.get("total_doses", 4)

        # Count doses after age 1
        doses_after_1 = sum(
            1 for d in relevant
            if age_at_date(person.birth_date, d.administration_date)[0] >= 1
        )

        complete = dose_count >= required and doses_after_1 >= 2
        last_dose_date = relevant[-1].administration_date if relevant else None

        return AntigenStatus(
            antigen=self.antigen_code,
            is_complete=complete,
            doses_received=dose_count,
            doses_required=required,
            schema_followed=schema,
            last_dose_date=last_dose_date,
            chapter_ref=rule.chapter_ref,
        )

    def find_missing(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[MissingVaccine]:
        return []

    def plan_future(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[FuturePlanItem]:
        return []
