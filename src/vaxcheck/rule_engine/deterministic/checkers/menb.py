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


class MenBChecker(AntigenChecker):
    antigen_code = "MenB"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("MenB", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)
        age_y, age_m = age_at_date(person.birth_date, evaluation_date)

        # Infant: 3 doses (3m, 5m, 15m). Adolescent: 2 doses (11-15y).
        # Catchup: infant to 5y, adolescent to 20y.
        if dose_count >= 2:
            complete = True
        elif dose_count >= 1 and age_y < 5:
            complete = False
        elif age_y <= 5:
            complete = dose_count >= 2  # At least catchup dose
        elif 6 <= age_y <= 10:
            complete = True  # Between windows, nothing to do
        elif 11 <= age_y <= 20:
            complete = dose_count >= 2
        else:
            complete = True  # Past all catchup windows

        last_dose_date = relevant[-1].administration_date if relevant else None
        notes: list[str] = []
        if dose_count == 0 and age_y <= 5:
            notes.append("MenB raccomandato come complementare nei lattanti")

        return AntigenStatus(
            antigen=self.antigen_code,
            is_complete=complete,
            doses_received=dose_count,
            doses_required=2 if age_y >= 11 else 3,
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

        if status.is_complete:
            return missing

        if status.doses_received == 0:
            if age_y <= 5:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                        reason="MenB non ricevuto — catchup disponibile fino al 5° compleanno",
                        recommended_schedule="2-3 dosi in base all'età (vedi tabella catchup UFSP)",
                        chapter_ref=rule.chapter_ref,
                        age_window=(0, 5),
                    )
                )
            elif 6 <= age_y <= 10:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.CATCHUP_CLOSED,
                        reason="Finestra catchup MenB infantile chiusa — attendere finestra 11-20 anni",
                        recommended_schedule="2 dosi tra 11-20 anni",
                        chapter_ref=rule.chapter_ref,
                        age_window=(11, 20),
                    )
                )
            elif 11 <= age_y <= 20:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                        reason="MenB non ricevuto — catchup adolescenziale disponibile",
                        recommended_schedule="2 dosi a distanza di almeno 1 mese",
                        chapter_ref=rule.chapter_ref,
                        age_window=(11, 20),
                    )
                )
            else:
                missing.append(
                    MissingVaccine(
                        antigen=self.antigen_code,
                        priority=MissingVaccinePriority.CATCHUP_CLOSED,
                        reason="Finestra catchup MenB chiusa (oltre 20 anni)",
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

        if age_y < 11 and status.doses_received == 0:
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
                    plan_type="vaccinazione_base",
                    chapter_ref=rule.chapter_ref,
                )
            )

        return items
