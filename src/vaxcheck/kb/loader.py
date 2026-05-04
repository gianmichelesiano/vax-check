from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from vaxcheck.domain.compliance import ComplianceLevel
from vaxcheck.domain.knowledge import AntigenRule, KnowledgeBase, VaccineProduct

# ──────────────────────────────────────────────────────────
# German → English key normalization
# ──────────────────────────────────────────────────────────

_DE_KEY_MAP: dict[str, str] = {
    # Top-level
    "metadaten": "metadata",
    "antigene": "antigens",
    "altersmeilensteine": "age_milestones",
    # Metadata
    "quelle": "source",
    "sprache": "language",
    "datum": "publication_date",
    # Antigen fields
    "vollname": "full_name",
    "empfehlungskategorie": "recommendation_level",
    "kapitel": "chapter_ref",
    "grundimmunisierung": "primary_schedule",
    "auffrischimpfungen": "boosters",
    "auffrisch_intervalle": "booster_intervals",
    "nachholimpfung": "catchup_rules",
    "kontraindikationen": "contraindications",
    "hinweis": "note",
    # Dose-level
    "alter_monate": "age_months",
    "alter_jahre": "age_years",
    "ab_alter_jahre": "age_years_from",
    "alle_jahre": "every_years",
    "min_alter_wochen_erste_dosis": "min_age_weeks_first_dose",
    "gesamtdosen": "doses",
    "dosen": "doses",
    "gilt_als_vollstaendig": "considered_complete",
    "bis_geburtsjahr": "until_birth_year",
    "ab_geburtsjahr": "from_birth_year",
    "erwachsene_25_64_jahre": "adult_25_64_years",
    "erwachsene_ab_65_jahre": "adult_65_plus_years",
    "immundefizient": "immunodeficient",
    "referenz_tabellen": "reference_tables",
    "prinzip": "principle",
    "kombination": "combination",
    "min_abstand_tage": "min_interval_days",
    "antigen_form": "antigen_form",
    "historisches_schema": "historical_schema",
    "schema": "schema",
    "schemata": "schemata",
    # Risk groups
    "chronische_erkrankungen": "clinical_conditions",
    "schwangerschaft_und_neugeborene": "pregnancy",
    "berufe_und_situationen": "occupational",
    "auslandreisende": "travel",
    "sonderregeln": "special_rules",
    "bezeichnung": "label",
    "empfohlen": "recommended",
    "schwelle": "severity_threshold",
    # Catalog
    "produkte": "products",
    "veraltete_produkte": "deprecated_products",
    # URL
    "grund": "reason",
    "url": "reference_url",
    # Catalog product fields
    "aliase": "aliases",
    "hersteller": "manufacturer",
    "altersbereich": "age_range",
    "min_monate": "min_months",
    "max_monate": "max_months",
    "min_jahre": "min_years",
    "max_jahre": "max_years",
    "note": "notes",  # catalog product notes (schedule uses "hinweis" → "note")
}

_DE_VALUE_MAP: dict[str, str] = {
    "basisimpfung": "base",
    "ergaenzend": "complementary",
    "risikogruppe": "risk_group",
}


def _normalize_de(data: Any) -> Any:
    """Recursively translate German YAML keys/values to English equivalents.

    Runs two passes: first pass handles hinweis→note, second pass handles note→notes.
    """
    if isinstance(data, dict):
        result: dict[str, Any] = {}
        for k, v in data.items():
            new_key = _DE_KEY_MAP.get(k, k)
            result[new_key] = _normalize_de(v)
        # Second pass on keys: re-normalize in case of chained mappings (hinweis→note→notes)
        result2: dict[str, Any] = {}
        for k, v in result.items():
            new_key = _DE_KEY_MAP.get(k, k)
            result2[new_key] = v
        return result2
    if isinstance(data, list):
        return [_normalize_de(item) for item in data]
    if isinstance(data, str):
        return _DE_VALUE_MAP.get(data, data)
    return data


# ──────────────────────────────────────────────────────────
# File name maps per language
# ──────────────────────────────────────────────────────────

_LANG_FILES: dict[str, dict[str, str]] = {
    "IT": {
        "catalog": "vaccines_catalog.yaml",
        "schedule": "vaccination_schedule_2026.yaml",
        "risk": "risk_groups.yaml",
    },
    "DE": {
        "catalog": "impfstoff_katalog.yaml",
        "schedule": "impfplan_2026.yaml",
        "risk": "risikogruppen.yaml",
    },
}


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


def load_knowledge_base(kb_dir: Path, language: str | None = None) -> KnowledgeBase:
    """Load and validate KB YAML files for a given language.

    Args:
        kb_dir: Root kb directory (contains IT/, DE/, etc. subdirectories).
        language: Two-letter language code. Defaults to KB_LANGUAGE env var or "IT".

    Returns:
        A validated, immutable KnowledgeBase.
    """
    if language is None:
        language = os.environ.get("KB_LANGUAGE", "IT").upper()

    lang_dir = kb_dir / language
    file_names = _LANG_FILES.get(language)
    if file_names is None:
        raise ValueError(f"Unsupported KB language: {language}")

    catalog_path = lang_dir / file_names["catalog"]
    schedule_path = lang_dir / file_names["schedule"]
    risk_path = lang_dir / file_names["risk"]

    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog file not found: {catalog_path}")
    if not schedule_path.exists():
        raise FileNotFoundError(f"Schedule file not found: {schedule_path}")
    if not risk_path.exists():
        raise FileNotFoundError(f"Risk groups file not found: {risk_path}")

    raw_catalog = _load_yaml(catalog_path)
    raw_schedule = _load_yaml(schedule_path)
    raw_risk = _load_yaml(risk_path)

    if language == "DE":
        raw_catalog = _normalize_de(raw_catalog)
        raw_schedule = _normalize_de(raw_schedule)
        raw_risk = _normalize_de(raw_risk)

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
