from __future__ import annotations

from datetime import date

from vaxcheck.domain.compliance import AntigenStatus, FuturePlanItem
from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.domain.person import Person


def generate_future_plan(
    person: Person,
    antigen_statuses: dict[str, AntigenStatus],
    kb: KnowledgeBase,
    evaluation_date: date,
    horizon_years: int = 80,
) -> list[FuturePlanItem]:
    """Generate a personalized future vaccination calendar based on age milestones."""
    items: list[FuturePlanItem] = []
    age_y = person.age_years

    for milestone in kb.age_milestones:
        target_age = milestone.get("age_years") or milestone.get("age_months")
        if target_age is None:
            # Handle "age_years_from" with "every_years" (recurring)
            age_from = milestone.get("age_years_from")
            every = milestone.get("every_years")
            if age_from is not None and every is not None:
                # Generate recurring items
                next_age = age_from
                if age_y >= age_from:
                    # Find next occurrence
                    years_since = age_y - age_from
                    next_age = age_from + ((years_since // every) + 1) * every
                if next_age - age_y <= horizon_years:
                    target_date = date(
                        person.birth_date.year + next_age,
                        person.birth_date.month,
                        person.birth_date.day,
                    )
                    for antigen in milestone.get("expected", []):
                        # Skip if already complete
                        status = antigen_statuses.get(antigen)
                        if status and status.is_complete:
                            continue
                        items.append(
                            FuturePlanItem(
                                antigen=antigen,
                                target_age_years=next_age,
                                target_date_estimate=target_date,
                                plan_type=milestone.get("type", "richiamo"),
                                chapter_ref=None,
                            )
                        )
            continue

        # Single milestone
        if isinstance(target_age, list):
            target_min, target_max = target_age
            effective_target = target_min
        else:
            effective_target = target_age

        if age_y < effective_target:
            target_date = date(
                person.birth_date.year + effective_target,
                person.birth_date.month,
                person.birth_date.day,
            )
            for antigen in milestone.get("expected", []):
                # Skip if already complete
                status = antigen_statuses.get(antigen)
                if status and status.is_complete:
                    continue
                items.append(
                    FuturePlanItem(
                        antigen=antigen,
                        target_age_years=target_age if isinstance(target_age, int) else (target_min, target_max),
                        target_date_estimate=target_date,
                        plan_type=milestone.get("type", "vaccinazione_base"),
                        chapter_ref=None,
                    )
                )

    # Sort by target date
    items.sort(key=lambda x: x.target_date_estimate or date.max)
    return items
