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


class PCVChecker(AntigenChecker):
    antigen_code = "PCV_pediatric"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("PCV", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)

        # Pediatric: 2+1 schema (2m, 4m, 12m) = 3 doses
        required = 3
        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        complete = dose_count >= required
        notes: list[str] = []
        if not complete and age_y >= 5:
            notes.append("catchup_closed")

        last_dose_date = relevant[-1].administration_date if relevant else None

        return AntigenStatus(
            antigen=self.antigen_code,
            is_complete=complete,
            doses_received=dose_count,
            doses_required=required,
            schema_followed="2+1",
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
        if age_y >= 5:
            return [
                MissingVaccine(
                    antigen=self.antigen_code,
                    priority=MissingVaccinePriority.CATCHUP_CLOSED,
                    reason="Finestra catchup PCV pediatrico chiusa al 5° compleanno",
                    recommended_schedule="Solo se gruppo a rischio (capitolo 3.1.h)",
                    chapter_ref=rule.chapter_ref,
                )
            ]

        doses_missing = status.doses_required - status.doses_received
        priority = MissingVaccinePriority.DUE_NOW if age_y >= 1 else MissingVaccinePriority.UPCOMING
        return [
            MissingVaccine(
                antigen=self.antigen_code,
                priority=priority,
                reason=f"Schema 2+1 incompleto: {status.doses_received}/{status.doses_required} dosi",
                recommended_schedule="2 mesi, 4 mesi, 12 mesi (schema 2+1)",
                chapter_ref=rule.chapter_ref,
                age_window=(0, 5),
            )
        ]

    def plan_future(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[FuturePlanItem]:
        items: list[FuturePlanItem] = []
        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        # PCV adult at 65
        if age_y < 65:
            target_date = date(
                person.birth_date.year + 65,
                person.birth_date.month,
                person.birth_date.day,
            )
            items.append(
                FuturePlanItem(
                    antigen="PCV_adult",
                    target_age_years=65,
                    target_date_estimate=target_date,
                    plan_type="vaccinazione_base",
                    chapter_ref="1.5.d",
                )
            )

        return items
