from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from vaxcheck.domain.person import Person


class ComplianceLevel(str, Enum):
    BASE = "base"
    COMPLEMENTARY = "complementary"
    RISK_GROUP = "risk_group"


class AntigenStatus(BaseModel):
    """Status of a single antigen for a patient."""

    antigen: str
    is_complete: bool
    doses_received: int
    doses_required: int
    schema_followed: str | None = None
    last_dose_date: date | None = None
    next_dose_due: date | None = None
    notes: list[str] = Field(default_factory=list)
    chapter_ref: str | None = None


class MissingVaccinePriority(str, Enum):
    URGENT = "urgent"
    DUE_NOW = "due_now"
    UPCOMING = "upcoming"
    CATCHUP_AVAILABLE = "catchup_available"
    CATCHUP_CLOSED = "catchup_closed"


class MissingVaccine(BaseModel):
    antigen: str
    priority: MissingVaccinePriority
    reason: str
    recommended_schedule: str
    chapter_ref: str | None = None
    age_window: tuple[int, int] | None = None


class FuturePlanItem(BaseModel):
    antigen: str
    target_age_years: int | tuple[int, int]
    target_date_estimate: date | None = None
    plan_type: str
    chapter_ref: str | None = None


DISCLAIMER = (
    "VaxCheck è un ausilio alla consulenza farmacistica e non sostituisce "
    "il parere del medico curante. Le decisioni cliniche restano di "
    "competenza del medico."
)


class ComplianceReport(BaseModel):
    """Final output of the rule engine. Same shape for engines A and B."""

    person: Person
    evaluation_date: date
    total_records: int

    antigen_statuses: dict[str, AntigenStatus]

    overall_compliance: bool
    missing_vaccines: list[MissingVaccine]
    future_plan: list[FuturePlanItem]

    engine_used: Literal["deterministic", "llm"]
    engine_version: str
    warnings: list[str] = Field(default_factory=list)

    disclaimer: str = DISCLAIMER
