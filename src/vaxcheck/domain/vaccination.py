from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class VaccinationRecord(BaseModel):
    """Raw administration record — one product on one date.

    Option 1 granularity: stored as-is, denormalized at runtime
    into N NormalizedDose (one per antigen) via the normalizer.
    """

    product_name: str
    administration_date: date
    lot_number: str | None = None
    administered_by: str | None = None
    notes: str | None = None
    record_id: UUID = Field(default_factory=uuid4)


class NormalizedDose(BaseModel):
    """Single dose of a single antigen, derived from a VaccinationRecord.

    Generated at runtime by the normalizer. NOT persisted.
    """

    antigen: str
    administration_date: date
    source_record_id: UUID
    source_product: str
    dose_strength: Literal["full", "reduced"] = "full"
