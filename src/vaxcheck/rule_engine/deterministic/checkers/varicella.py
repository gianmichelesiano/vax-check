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


class VaricellaChecker(AntigenChecker):
    antigen_code = "V"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("V", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)
        required = 2
        birth_year = person.birth_year

        # From 2023: base recommendation. Before 2023: complementary but
        # Priorix-Tetra (MORV) has been preferred since 2023.
        # If child got Priorix-Tetra (MORV), varicella is covered.
        complete = dose_count >= required

        last_dose_date = relevant[-1].administration_date if relevant else None

        notes: list[str] = []
        if birth_year < 2023 and complete:
            notes.append("Completato via MORV (Priorix-Tetra)")

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
        if age_y < 40:
            return [
                MissingVaccine(
                    antigen=self.antigen_code,
                    priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                    reason="Varicella non completata — catchup disponibile sotto i 40 anni",
                    recommended_schedule="2 dosi a distanza di almeno 4 settimane (o 1 dose se già 1 ricevuta)",
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
