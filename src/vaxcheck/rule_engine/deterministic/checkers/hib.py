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


class HibChecker(AntigenChecker):
    antigen_code = "Hib"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("Hib", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)

        # Primary: 3 doses (2m, 4m, 12m)
        required = 3
        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        # After age 5, Hib no longer indicated (catchup closed)
        # But if already vaccinated, it's complete
        if dose_count >= required:
            complete = True
        elif age_y >= 5:
            # Past catchup window, not needed anymore
            complete = True
            if dose_count == 0:
                return AntigenStatus(
                    antigen=self.antigen_code,
                    is_complete=True,
                    doses_received=0,
                    doses_required=0,
                    schema_followed="natural_immunity",
                    notes=["Dopo i 5 anni Hib non è più indicato"],
                    chapter_ref=rule.chapter_ref,
                )
        else:
            complete = False

        last_dose_date = relevant[-1].administration_date if relevant else None

        return AntigenStatus(
            antigen=self.antigen_code,
            is_complete=complete,
            doses_received=dose_count,
            doses_required=required,
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
        age_y, _ = age_at_date(person.birth_date, evaluation_date)
        if status.is_complete:
            return []

        if age_y >= 5:
            return [
                MissingVaccine(
                    antigen=self.antigen_code,
                    priority=MissingVaccinePriority.CATCHUP_CLOSED,
                    reason="Finestra catchup Hib chiusa al 5° compleanno",
                    recommended_schedule="Non più indicata (immunità naturale)",
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
