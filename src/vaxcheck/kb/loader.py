from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from vaxcheck.domain.compliance import ComplianceLevel
from vaxcheck.domain.knowledge import AntigenRule, KnowledgeBase, VaccineProduct


def _load_yaml(path: Path) -> dict[str, Any]:
    with open(path) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping in {path}, got {type(data)}")
    return data


def _parse_products(raw_catalog: dict[str, Any]) -> tuple[list[VaccineProduct], dict[str, VaccineProduct]]:
    products: list[VaccineProduct] = []
    by_name: dict[str, VaccineProduct] = {}
    for entry in raw_catalog.get("products", []):
        product = VaccineProduct(
            name=entry["name"],
            aliases=entry.get("aliases", []),
            manufacturer=entry.get("manufacturer"),
            antigens=entry["antigens"],
            age_range=entry.get("age_range"),
            notes=entry.get("notes"),
        )
        products.append(product)
        by_name[product.name.lower().strip()] = product
        for alias in product.aliases:
            by_name.setdefault(alias.lower().strip(), product)
    return products, by_name


def _parse_antigens(raw_schedule: dict[str, Any]) -> dict[str, AntigenRule]:
    antigens: dict[str, AntigenRule] = {}
    for code, entry in raw_schedule.get("antigens", {}).items():
        rec_level_raw = entry.get("recommendation_level", "complementary")
        try:
            rec_level = ComplianceLevel(rec_level_raw)
        except ValueError:
            rec_level = ComplianceLevel.COMPLEMENTARY

        antigens[code] = AntigenRule(
            antigen_code=code,
            full_name=entry.get("full_name", code),
            recommendation_level=rec_level,
            chapter_ref=entry.get("chapter_ref"),
            primary_schedule=entry.get("primary_schedule", {}),
            boosters=entry.get("boosters", []),
            catchup_rules=entry.get("catchup_rules") or entry.get("catchup"),
            contraindications=entry.get("contraindications", []),
            raw=entry,
        )
    return antigens


def load_knowledge_base(kb_dir: Path) -> KnowledgeBase:
    """Load and validate the three KB YAML files, building a KnowledgeBase.

    Args:
        kb_dir: Directory containing the three YAML files.

    Returns:
        A validated, immutable KnowledgeBase.
    """
    catalog_path = kb_dir / "vaccines_catalog.yaml"
    schedule_path = kb_dir / "vaccination_schedule_2026.yaml"
    risk_path = kb_dir / "risk_groups.yaml"

    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog file not found: {catalog_path}")
    if not schedule_path.exists():
        raise FileNotFoundError(f"Schedule file not found: {schedule_path}")
    if not risk_path.exists():
        raise FileNotFoundError(f"Risk groups file not found: {risk_path}")

    raw_catalog = _load_yaml(catalog_path)
    raw_schedule = _load_yaml(schedule_path)
    raw_risk = _load_yaml(risk_path)

    products, products_by_name = _parse_products(raw_catalog)
    antigens = _parse_antigens(raw_schedule)

    version = raw_schedule.get("metadata", {}).get("version", "unknown")
    age_milestones = raw_schedule.get("age_milestones", [])

    return KnowledgeBase(
        version=version,
        products=products,
        products_by_name=products_by_name,
        antigens=antigens,
        age_milestones=age_milestones,
        risk_groups=raw_risk,
        raw_catalog=raw_catalog,
        raw_schedule=raw_schedule,
        raw_risk_groups=raw_risk,
    )
