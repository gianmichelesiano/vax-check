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


class HPVChecker(AntigenChecker):
    antigen_code = "HPV"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("HPV9", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)
        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        # 11-14: 2 doses. 15-26: 3 doses.
        if age_y < 11:
            required = 2
        elif age_y <= 14:
            required = 2
        else:
            required = 3

        complete = dose_count >= required
        if age_y < 11:
            complete = True  # Not yet due

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
        missing: list[MissingVaccine] = []

        if status.is_complete and age_y >= 11:
            return missing

        if 11 <= age_y <= 14:
            if status.doses_received == 0:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.DUE_NOW,
                        reason="HPV raccomandato a 11-14 anni — non ancora iniziato",
                        recommended_schedule="2 dosi a 0-6 mesi (Gardasil 9)",
                        chapter_ref=rule.chapter_ref,
                        age_window=(11, 14),
                    )
                )
        elif 15 <= age_y <= 26:
            if status.doses_received < 3:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                        reason=f"HPV recupero: {status.doses_received}/3 dosi",
                        recommended_schedule="3 dosi a 0-2-6 mesi (Gardasil 9)",
                        chapter_ref=rule.chapter_ref,
                        age_window=(15, 26),
                    )
                )

        return missing

    def plan_future(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[FuturePlanItem]:
        items: list[FuturePlanItem] = []
        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        if age_y < 11:
            target_date = date(
                person.birth_date.year + 11,
                person.birth_date.month,
                person.birth_date.day,
            )
            items.append(
                FuturePlanItem(
                    antigen=self.antigen_code,
                    target_age_years=(11, 14),
                    target_date_estimate=target_date,
                    plan_type="vaccinazione_base",
                    chapter_ref=rule.chapter_ref,
                )
            )

        return items
