from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, computed_field


class Sex(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "X"


class ClinicalCondition(BaseModel):
    """A clinical condition or situation that may trigger additional vaccines."""

    code: str
    label: str
    onset_date: date | None = None


class Person(BaseModel):
    """Patient demographics and clinical conditions."""

    given_name: str
    family_name: str
    birth_date: date
    sex: Sex
    clinical_conditions: list[ClinicalCondition] = Field(default_factory=list)
    occupational_situations: list[str] = Field(default_factory=list)
    notes: str | None = None

    @computed_field
    @property
    def age_years(self) -> int:
        """Age in completed years at today's date."""
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @computed_field
    @property
    def age_months(self) -> int:
        """Age in completed months at today's date."""
        today = date.today()
        months = (today.year - self.birth_date.year) * 12 + (today.month - self.birth_date.month)
        if today.day < self.birth_date.day:
            months -= 1
        return months

    @computed_field
    @property
    def birth_year(self) -> int:
        return self.birth_date.year
