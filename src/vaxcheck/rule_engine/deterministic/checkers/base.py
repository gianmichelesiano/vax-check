from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from vaxcheck.domain.compliance import AntigenStatus, FuturePlanItem, MissingVaccine
from vaxcheck.domain.knowledge import AntigenRule
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import NormalizedDose

# Antigen equivalence groups for counting doses across related antigens
ANTIGEN_GROUPS: dict[str, set[str]] = {
    "D": {"D", "d"},
    "T": {"T"},
    "Pa": {"Pa", "pa"},
    "IPV": {"IPV"},
    "Hib": {"Hib"},
    "HBV": {"HBV"},
    "PCV": {"PCV13", "PCV15", "PCV20", "PCV21", "PPV23"},
    "M": {"M"},
    "O": {"O"},
    "R": {"R"},
    "V": {"V"},
    "MenACWY": {"MenACWY"},
    "MenB": {"MenB"},
    "HPV9": {"HPV9"},
    "FSME": {"FSME"},
    "RV": {"RV"},
    "HZ": {"HZ"},
    "Influenza": {"Influenza_std", "Influenza_HD"},
    "COVID": {"COVID"},
}


def count_relevant_doses(antigen: str, doses: list[NormalizedDose]) -> list[NormalizedDose]:
    """Count doses that are relevant for a given antigen, including equivalences."""
    relevant_codes = ANTIGEN_GROUPS.get(antigen, {antigen})
    return [d for d in doses if d.antigen in relevant_codes]


def age_at_date(birth_date: date, at_date: date) -> tuple[int, int]:
    """Return (years, months) age at a given date."""
    years = at_date.year - birth_date.year
    months = at_date.month - birth_date.month
    if at_date.day < birth_date.day:
        months -= 1
    if months < 0:
        years -= 1
        months += 12
    return years, months


def months_between(d1: date, d2: date) -> int:
    """Return months between two dates (d1 earlier than d2)."""
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


class AntigenChecker(ABC):
    """Base class for single-antigen checkers."""

    antigen_code: str

    @abstractmethod
    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus: ...

    @abstractmethod
    def find_missing(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[MissingVaccine]: ...

    @abstractmethod
    def plan_future(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[FuturePlanItem]: ...
