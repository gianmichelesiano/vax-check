from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from vaxcheck.domain.compliance import ComplianceLevel


class VaccineProduct(BaseModel):
    """A single vaccine product from the catalog."""

    name: str
    aliases: list[str] = Field(default_factory=list)
    manufacturer: str | None = None
    antigens: list[str]
    age_range: dict[str, Any] | None = None
    notes: str | None = None


class AntigenRule(BaseModel):
    """Rules for a single antigen from the 2026 schedule."""

    antigen_code: str
    full_name: str
    recommendation_level: ComplianceLevel
    chapter_ref: str | None = None
    primary_schedule: dict[str, Any]
    boosters: list[dict[str, Any]] = Field(default_factory=list)
    catchup_rules: dict[str, Any] | None = None
    contraindications: list[str] = Field(default_factory=list)
    raw: dict[str, Any]


class KnowledgeBase(BaseModel):
    """Complete loaded knowledge base (immutable)."""

    version: str
    products: list[VaccineProduct]
    products_by_name: dict[str, VaccineProduct]
    antigens: dict[str, AntigenRule]
    age_milestones: list[dict[str, Any]]
    risk_groups: dict[str, Any]
    raw_catalog: dict[str, Any]
    raw_schedule: dict[str, Any]
    raw_risk_groups: dict[str, Any]

    model_config = {"arbitrary_types_allowed": True}

    def find_product(self, name: str) -> VaccineProduct | None:
        """Case-insensitive lookup with alias fallback."""
        key = name.lower().strip()
        if key in self.products_by_name:
            return self.products_by_name[key]
        for product in self.products:
            for alias in product.aliases:
                if alias.lower().strip() == key:
                    return product
        return None

    def get_antigen_rule(self, antigen: str) -> AntigenRule | None:
        return self.antigens.get(antigen)
