from __future__ import annotations

from datetime import date
from typing import Protocol

from vaxcheck.domain.compliance import ComplianceReport
from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import VaccinationRecord


class RuleEngine(Protocol):
    """Common interface for both rule engines (deterministic and LLM)."""

    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def evaluate(
        self,
        person: Person,
        records: list[VaccinationRecord],
        kb: KnowledgeBase,
        evaluation_date: date | None = None,
    ) -> ComplianceReport: ...
