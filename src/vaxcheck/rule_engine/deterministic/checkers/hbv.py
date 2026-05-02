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
    count_relevant_doses,
)


class HBVChecker(AntigenChecker):
    antigen_code = "HBV"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("HBV", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)

        # Primary: 3 doses (2m, 4m, 12m) via hexavalent
        required = 3
        complete = dose_count >= required
        last_dose_date = relevant[-1].administration_date if relevant else None

        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        notes: list[str] = []
        # Adolescent catchup: if 11-15 and not vaccinated, recommend
        if not complete and 11 <= age_y <= 15:
            notes.append("Catchup adolescenziale disponibile: schema 2 o 3 dosi")

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
        if 11 <= age_y <= 15:
            return [
                MissingVaccine(
                    antigen=self.antigen_code,
                    priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                    reason="HBV non completato nell'infanzia — catchup adolescenziale disponibile",
                    recommended_schedule="Schema pediatrico 3 dosi (0-1-5 mesi) o adulto 2 dosi (0-4 mesi)",
                    chapter_ref=rule.chapter_ref,
                    age_window=(11, 15),
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
