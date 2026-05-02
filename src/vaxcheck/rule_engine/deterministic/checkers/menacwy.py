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


class MenACWYChecker(AntigenChecker):
    antigen_code = "MenACWY"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("MenACWY", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)
        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        # Toddler: 1 dose 12-18m. Adolescent: 1 dose 11-15y.
        # Complete if at least 1 dose received (toddler dose)
        # Adolescent booster expected at 11-15
        toddler_done = dose_count >= 1
        has_adolescent = any(
            11 <= age_at_date(person.birth_date, d.administration_date)[0] <= 20
            for d in relevant
        )

        if age_y <= 5:
            complete = toddler_done
        elif 6 <= age_y <= 10:
            complete = True  # Toddler dose done, adolescent window not yet open
        elif 11 <= age_y <= 20:
            complete = toddler_done  # Not complete without adolescent dose
            if has_adolescent:
                complete = True
        else:
            complete = True  # Past catchup, not recommended anymore

        last_dose_date = relevant[-1].administration_date if relevant else None
        notes: list[str] = []
        if toddler_done and not has_adolescent and age_y >= 11:
            notes.append("Richiamo adolescenziale 11-15 anni raccomandato")

        return AntigenStatus(
            antigen=self.antigen_code,
            is_complete=complete,
            doses_received=dose_count,
            doses_required=1 if age_y < 11 else 2,
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
        age_y, _ = age_at_date(person.birth_date, evaluation_date)
        missing: list[MissingVaccine] = []

        if status.is_complete and not (11 <= age_y <= 20 and status.doses_received < 2):
            return missing

        # Toddler dose missing and under 5
        if status.doses_received == 0:
            if age_y <= 5:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                        reason="MenACWY non ricevuto — catchup disponibile fino al 5° compleanno",
                        recommended_schedule="1-2 dosi in base al vaccino (12-18 mesi)",
                        chapter_ref=rule.chapter_ref,
                        age_window=(1, 5),
                    )
                )
            elif 11 <= age_y <= 20:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                        reason="MenACWY non ricevuto — catchup adolescenziale disponibile",
                        recommended_schedule="1 dose tra 11-20 anni",
                        chapter_ref=rule.chapter_ref,
                        age_window=(11, 20),
                    )
                )
            elif 6 <= age_y <= 10:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.UPCOMING,
                        reason="MenACWY non ricevuto — previsto a 11-15 anni",
                        recommended_schedule="1 dose tra 11-15 anni",
                        chapter_ref=rule.chapter_ref,
                        age_window=(11, 15),
                    )
                )
            elif age_y > 20:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.CATCHUP_CLOSED,
                        reason="Finestra catchup MenACWY chiusa (oltre 20 anni)",
                        recommended_schedule="Non più raccomandato dopo i 20 anni",
                        chapter_ref=rule.chapter_ref,
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

        if age_y < 11 and status.doses_received >= 1:
            target_date = date(
                person.birth_date.year + 11,
                person.birth_date.month,
                person.birth_date.day,
            )
            items.append(
                FuturePlanItem(
                    antigen=self.antigen_code,
                    target_age_years=(11, 15),
                    target_date_estimate=target_date,
                    plan_type="richiamo",
                    chapter_ref=rule.chapter_ref,
                )
            )

        return items
