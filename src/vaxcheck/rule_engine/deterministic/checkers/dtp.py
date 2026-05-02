from __future__ import annotations

from datetime import date

from vaxcheck.domain.compliance import AntigenStatus, FuturePlanItem, MissingVaccine, MissingVaccinePriority
from vaxcheck.domain.knowledge import AntigenRule
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import NormalizedDose
from vaxcheck.rule_engine.deterministic.checkers.base import (
    AntigenChecker,
    age_at_date,
    count_relevant_doses,
)


class DTPChecker(AntigenChecker):
    antigen_code = "DTP"

    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus:
        relevant = count_relevant_doses("D", doses) + count_relevant_doses("Pa", doses)
        # Deduplicate by source_record_id (a single hexavalent dose covers both D and Pa)
        seen: set[str] = set()
        unique_doses: list[NormalizedDose] = []
        for d in sorted(relevant, key=lambda x: x.administration_date):
            rid = str(d.source_record_id)
            if rid not in seen:
                seen.add(rid)
                unique_doses.append(d)

        dose_count = len(unique_doses)
        birth_year = person.birth_year

        # Determine schema
        if birth_year <= 2018:
            schema = "3+1"
            primary_required = 4
        else:
            schema = "2+1"
            primary_required = 3

        # Check boosters
        age_y, _ = age_at_date(person.birth_date, evaluation_date)
        last_dose_date = unique_doses[-1].administration_date if unique_doses else None

        # Count doses that are primary (before age 2)
        primary_doses = [
            d for d in unique_doses
            if age_at_date(person.birth_date, d.administration_date)[0] < 2
        ]
        _booster_doses = [
            d for d in unique_doses
            if age_at_date(person.birth_date, d.administration_date)[0] >= 2
        ]

        primary_complete = len(primary_doses) >= primary_required

        # Check if booster at 4-7 was done
        prescolar_booster_done = any(
            4 <= age_at_date(person.birth_date, d.administration_date)[0] <= 7
            for d in unique_doses
        )

        # Check if adolescent booster done (11-15)
        adolescent_booster_done = any(
            11 <= age_at_date(person.birth_date, d.administration_date)[0] <= 15
            for d in unique_doses
        )

        # Overall complete = primary + appropriate boosters for age
        complete = primary_complete
        if age_y >= 8:
            complete = complete and prescolar_booster_done
        if age_y >= 16:
            complete = complete and adolescent_booster_done

        notes: list[str] = []
        next_due: date | None = None

        # Determine next dose due
        if not prescolar_booster_done and age_y >= 4:
            next_due = evaluation_date  # due now
        elif not adolescent_booster_done and age_y >= 11:
            next_due = evaluation_date
        elif age_y >= 25:
            adult_booster_done = any(
                age_at_date(person.birth_date, d.administration_date)[0] >= 25
                for d in unique_doses
            )
            if not adult_booster_done:
                next_due = evaluation_date

        return AntigenStatus(
            antigen=self.antigen_code,
            is_complete=complete,
            doses_received=dose_count,
            doses_required=primary_required,
            schema_followed=schema,
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
        missing: list[MissingVaccine] = []
        age_y, _ = age_at_date(person.birth_date, evaluation_date)

        if status.is_complete:
            return missing

        primary_incomplete = status.doses_received < status.doses_required
        if primary_incomplete:
            missing.append(
                MissingVaccine(
                    antigen=self.antigen_code,
                    priority=MissingVaccinePriority.CATCHUP_AVAILABLE,
                    reason=f"Schema primario incompleto: {status.doses_received}/{status.doses_required} dosi",
                    recommended_schedule="Completare schema secondo tabella catchup UFSP",
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

        for booster in rule.boosters:
            target = booster.get("age_years")
            if target is None:
                continue
            if isinstance(target, list):
                target_min, target_max = target
                if age_y < target_min:
                    target_date = date(
                        person.birth_date.year + target_min,
                        person.birth_date.month,
                        person.birth_date.day,
                    )
                    items.append(
                        FuturePlanItem(
                            antigen=self.antigen_code,
                            target_age_years=(target_min, target_max),
                            target_date_estimate=target_date,
                            plan_type="richiamo",
                            chapter_ref=rule.chapter_ref,
                        )
                    )
            elif isinstance(target, int):
                if age_y < target:
                    target_date = date(
                        person.birth_date.year + target,
                        person.birth_date.month,
                        person.birth_date.day,
                    )
                    items.append(
                        FuturePlanItem(
                            antigen=self.antigen_code,
                            target_age_years=target,
                            target_date_estimate=target_date,
                            plan_type="richiamo",
                            chapter_ref=rule.chapter_ref,
                        )
                    )

        return items
