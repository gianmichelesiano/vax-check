from __future__ import annotations

from datetime import date

from vaxcheck.domain.knowledge import AntigenRule
from vaxcheck.domain.person import Person
from vaxcheck.rule_engine.deterministic.checkers.base import age_at_date


def calculate_catchup_doses(
    antigen: str,
    person: Person,
    doses_received: int,
    rule: AntigenRule,
    evaluation_date: date,
) -> int:
    """Return number of catchup doses needed based on UFSP tables.

    Principle: never restart from zero. Calculate missing doses
    based on age and doses already received.
    """
    catchup = rule.catchup_rules
    if catchup is None:
        return 0

    age_y, age_m = age_at_date(person.birth_date, evaluation_date)
    age_total_months = age_y * 12 + age_m

    schedule_by_age = catchup.get("schedule_by_age", [])
    for entry in schedule_by_age:
        age_range = entry.get("age_range_months") or entry.get("age_range_years")
        if age_range is None:
            continue

        is_months = "age_range_months" in entry
        range_min = age_range[0]
        range_max = age_range[1]
        if not is_months:
            range_min *= 12
            range_max *= 12

        if range_min <= age_total_months <= range_max:
            doses = entry.get("doses", 0)
            if isinstance(doses, str):
                # "1 or 2 (vaccine-dependent)" → default to 1
                doses = 1
            needed = max(0, int(doses) - doses_received)
            return needed

    return 0
