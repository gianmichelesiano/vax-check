from pathlib import Path

from fastapi import APIRouter, Depends

from vaxcheck.api.deps import get_kb
from vaxcheck.api.schemas import (
    DeprecatedProductOut,
    KBAntigenOut,
    KBFullOut,
    KBProductOut,
    RiskGroupItemOut,
    RiskGroupsOut,
    VaccineProductOut,
)
from vaxcheck.domain.knowledge import KnowledgeBase

router = APIRouter(tags=["catalog"])


@router.get("/catalog/products", response_model=list[VaccineProductOut])
def list_products(kb: KnowledgeBase = Depends(get_kb)):
    return [
        VaccineProductOut(
            name=p.name,
            aliases=p.aliases,
            manufacturer=p.manufacturer,
            antigens=p.antigens,
            age_range=p.age_range,
            notes=p.notes,
        )
        for p in kb.products
    ]


@router.get("/kb/version")
def kb_version(kb: KnowledgeBase = Depends(get_kb)):
    return {"version": kb.version, "date": kb.version}


def _summarize_primary_schedule(antigen_code: str, raw: dict) -> str | None:
    """Build readable Italian summary from primary_schedule YAML structure."""
    ps = raw.get("primary_schedule") or raw.get("schedule")
    if not ps:
        # Check for alternative schedule structures
        if raw.get("schedule_alternatives"):
            return None
        if raw.get("primary_schedule_infant"):
            ps = raw["primary_schedule_infant"]
        elif raw.get("adolescent_schedule"):
            return None
        elif raw.get("adult_schedule"):
            ps = raw["adult_schedule"]
        elif "age_min_years" in raw and raw.get("schedule"):
            ps = raw["schedule"]
        else:
            return None

    doses = ps.get("doses") or ps.get("doses_detail")
    schema_name = ps.get("schema_name") or ps.get("schema")
    total_doses = ps.get("doses")

    if doses and isinstance(doses, list):
        ages = []
        for d in doses:
            am = d.get("age_months")
            ay = d.get("age_years")
            ar = d.get("age_range")
            if am is not None:
                ages.append(f"{int(am)} mesi")
            elif ay is not None:
                if isinstance(ay, list):
                    ages.append(f"{ay[0]}-{ay[1]} anni")
                else:
                    ages.append(f"{int(ay)} anni")
            elif ar and isinstance(ar, list):
                ages.append(f"{ar[0]}-{ar[1]} mesi")
        n_doses = len(ages)
        base = f"{n_doses} dosi: {', '.join(ages)}"
        if schema_name:
            base += f" (schema {schema_name})"
        return base

    if total_doses and isinstance(total_doses, int):
        target = ps.get("target_age_years")
        interval = ps.get("interval_months")
        if target and interval:
            if isinstance(target, list):
                return f"{total_doses} dosi a {target[0]}-{target[1]} anni, intervallo {interval} mesi"
            return f"{total_doses} dosi a {int(target)} anni, intervallo {interval} mesi"

    return None


def _summarize_boosters(antigen_code: str, raw: dict) -> str | None:
    """Build readable Italian booster summary from boosters YAML."""
    boosters = raw.get("boosters")
    if not boosters or not isinstance(boosters, list) or len(boosters) == 0:
        return None

    parts: list[str] = []
    for b in boosters:
        ay = b.get("age_years")
        ayf = b.get("age_years_from")
        ey = b.get("every_years")
        note = b.get("notes") or b.get("note", "")

        if ay and isinstance(ay, list):
            parts.append(f"{ay[0]}-{ay[1]} anni")
        elif ay and isinstance(ay, (int, float)):
            parts.append(f"{int(ay)} anni")
        elif ayf is not None and ey is not None:
            parts.append(f"da {int(ayf)} anni ogni {int(ey)} anni")
        elif ayf is not None:
            parts.append(f"da {int(ayf)} anni")

        if note:
            parts[-1] += f" ({note})"

    # Read booster_intervals for recurring adult boosters
    bi = raw.get("booster_intervals", {})
    adult_25 = bi.get("adult_25_64_years")
    adult_65 = bi.get("adult_65_plus_years")
    if adult_25 and not any("ogni" in p for p in parts):
        parts.append(f"poi ogni {int(adult_25)} anni")
    if adult_65 and adult_65 != adult_25:
        parts.append(f"da 65 anni ogni {int(adult_65)} anni")

    return ", ".join(parts) if parts else None


def _build_risk_groups(raw_risk: dict) -> RiskGroupsOut:
    """Parse risk_groups YAML into typed structure."""
    out = RiskGroupsOut()

    for item_list, field in [
        (raw_risk.get("clinical_conditions", {}), "clinical_conditions"),
        (raw_risk.get("occupational", {}), "occupational"),
        (raw_risk.get("pregnancy", {}), "pregnancy"),
    ]:
        items = []
        for code, data in item_list.items():
            items.append(
                RiskGroupItemOut(
                    code=code,
                    label=data.get("label", code),
                    recommended=data.get("recommended", []),
                    severity_threshold=data.get("severity_threshold"),
                    note=data.get("notes") or data.get("note"),
                )
            )
        setattr(out, field, items)

    return out


@router.get("/kb/full", response_model=KBFullOut)
def kb_full(kb: KnowledgeBase = Depends(get_kb)):
    metadata = kb.raw_schedule.get("metadata", {})
    raw_catalog = kb.raw_catalog

    antigens = []
    for code, rule in sorted(kb.antigens.items(), key=lambda x: (
        {"base": 0, "complementary": 1, "risk_group": 2}.get(
            x[1].recommendation_level.value, 9
        ),
        x[0],
    )):
        antigens.append(
            KBAntigenOut(
                code=code,
                full_name=rule.full_name,
                recommendation_level=rule.recommendation_level.value,
                chapter_ref=rule.chapter_ref,
                primary_schedule_summary=_summarize_primary_schedule(code, rule.raw),
                boosters_summary=_summarize_boosters(code, rule.raw),
                raw=rule.raw,
            )
        )

    products = [
        KBProductOut(
            name=p.name,
            aliases=p.aliases,
            manufacturer=p.manufacturer,
            antigens=p.antigens,
            age_range=p.age_range,
            notes=p.notes,
        )
        for p in kb.products
    ]

    deprecated = [
        DeprecatedProductOut(name=d["name"], reason=d["reason"])
        for d in raw_catalog.get("deprecated_products", [])
    ]

    risk_groups = _build_risk_groups(kb.raw_risk_groups)

    # Try to read CHANGELOG
    changelog = ""
    changelog_path = Path("kb/CHANGELOG.md")
    if changelog_path.exists():
        changelog = changelog_path.read_text()

    return KBFullOut(
        metadata={
            "version": metadata.get("version", "unknown"),
            "publication_date": metadata.get("publication_date", ""),
            "source": metadata.get("source", ""),
            "reference_url": metadata.get("reference_url", ""),
        },
        antigens=antigens,
        products=products,
        deprecated_products=deprecated,
        risk_groups=risk_groups,
        changelog=changelog,
    )
