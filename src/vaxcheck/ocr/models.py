from datetime import date

from pydantic import BaseModel, Field


class ExtractedVaccination(BaseModel):
    product_name_raw: str
    product_name_normalized: str | None = None
    administration_date: date | None = None
    lot_number: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    needs_review: bool = False
    review_reason: str | None = None


class ExtractionResult(BaseModel):
    extractions: list[ExtractedVaccination]
    total_found: int
    low_confidence_count: int
    unrecognized_products: list[str]
    warnings: list[str]
    processing_time_ms: int
