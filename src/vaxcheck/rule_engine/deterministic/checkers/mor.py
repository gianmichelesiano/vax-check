from __future__ import annotations

from datetime import date

from vaxcheck.domain.compliance import (
    AntigenStatus,
    FuturePlanItem,
    MissingVaccine,
    MissingVaccinePriority,
)
from vaxcheck.domain.knowledge import AntigenRule
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import NormalizedDose
from vaxcheck.rule_engine.deterministic.checkers.base import (
    AntigenChecker,
    age_at_date,
)


class MORChecker(AntigenChecker):
    antigen_code = "MOR"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        # MOR can come from Priorix (M,O,R) or Priorix-Tetra (M,O,R,V)
        # Count unique administration dates (one product covers all three)
        seen_dates: set[date] = set()
        for d in sorted(doses, key=lambda x: x.administration_date):
            if d.antigen in ("M", "O", "R"):
                seen_dates.add(d.administration_date)

        dose_count = len(seen_dates)
        required = 2
        birth_year = person.birth_year

        complete = dose_count >= required
        last_dose_date = max(seen_dates) if seen_dates else None

        # Pre-1964: probably immune
        age_y, _ = age_at_date(person.birth_date, evaluation_date)
        notes: list[str] = []
        if birth_year < 1964:
            complete = True
            notes.append("Nato prima del 1964: probabilmente immune")

        return AntigenStatus(
            antigen=self.antigen_code,
            is_complete=complete,
            doses_received=dose_count,
            doses_required=required,
            last_dose_date=last_dose_date,
            notes=notes,
            chapter_ref=rule.chapter_ref,
        )

    def find_missing(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[MissingVaccine]:
        if status.is_complete:
            return []

        age_y, _ = age_at_date(person.birth_date, evaluation_date)
        if age_y >= 9:
            return [
                MissingVaccine(
                    antigen=self.antigen_code,
                    priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                    reason=f"MOR incompleto: {status.doses_received}/2 dosi — catchup disponibile",
                    recommended_schedule="2 dosi a distanza di almeno 4 settimane",
                    chapter_ref=rule.chapter_ref,
                )
            ]

        return []

    def plan_future(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[FuturePlanItem]:
        return []
