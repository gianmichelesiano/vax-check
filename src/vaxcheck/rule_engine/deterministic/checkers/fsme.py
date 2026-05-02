from __future__ import annotations

from datetime import date, timedelta

from vaxcheck.domain.compliance import (
    AntigenStatus,
    FuturePlanItem,
    MissingVaccine,
)
from vaxcheck.domain.knowledge import AntigenRule
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import NormalizedDose
from vaxcheck.rule_engine.deterministic.checkers.base import (
    AntigenChecker,
    age_at_date,
    count_relevant_doses,
)


class FSMEChecker(AntigenChecker):
    antigen_code = "FSME"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("FSME", doses)
        relevant.sort(key=lambda d: d.administration_date)
        dose_count = len(relevant)
        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        # Primary: 3 doses. Booster every 10 years.
        # From age 3 standard, from age 1 pediatric individual.
        complete = dose_count >= 3
        last_dose_date = relevant[-1].administration_date if relevant else None

        notes: list[str] = []
        next_due: date | None = None

        # Check if booster is due (>10 years since last dose)
        if complete and last_dose_date:
            years_since_last = (evaluation_date - last_dose_date).days / 365.25
            if years_since_last > 10:
                complete = False
                next_due = evaluation_date
                notes.append("Richiamo FSME scaduto: sono passati più di 10 anni")

        return AntigenStatus(
            antigen=self.antigen_code,
            is_complete=complete,
            doses_received=dose_count,
            doses_required=3,
            last_dose_date=last_dose_date,
            next_dose_due=next_due,
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
        # FSME is risk-group: only for endemic areas (all CH except Ticino)
        # Don't flag as missing by default — it's optional
        return []

    def plan_future(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[FuturePlanItem]:
        items: list[FuturePlanItem] = []
        if status.last_dose_date and status.is_complete:
            # Next booster in 10 years
            next_booster = status.last_dose_date + timedelta(days=365 * 10)
            items.append(
                FuturePlanItem(
                    antigen=self.antigen_code,
                    target_age_years=age_at_date(person.birth_date, next_booster)[0],
                    target_date_estimate=next_booster,
                    plan_type="richiamo",
                    chapter_ref=rule.chapter_ref,
                )
            )
        return items
