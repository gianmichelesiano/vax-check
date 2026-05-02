from __future__ import annotations

from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.domain.vaccination import NormalizedDose, VaccinationRecord


def normalize_records(
    records: list[VaccinationRecord],
    kb: KnowledgeBase,
) -> list[NormalizedDose]:
    """Expand each VaccinationRecord into N NormalizedDose, one per antigen.

    Example: Infanrix hexa → 6 NormalizedDose (D, T, Pa, IPV, Hib, HBV).
    Unknown products produce a warning but do not halt processing.
    """
    doses: list[NormalizedDose] = []
    for record in records:
        product = kb.find_product(record.product_name)
        if product is None:
            # Unknown product — skip with warning handled by caller
            continue
        for antigen in product.antigens:
            doses.append(
                NormalizedDose(
                    antigen=antigen,
                    administration_date=record.administration_date,
                    source_record_id=record.record_id,
                    source_product=product.name,
                )
            )
    return doses


def group_by_antigen(doses: list[NormalizedDose]) -> dict[str, list[NormalizedDose]]:
    """Group normalized doses by antigen code."""
    groups: dict[str, list[NormalizedDose]] = {}
    for dose in doses:
        groups.setdefault(dose.antigen, []).append(dose)
    for antigen_doses in groups.values():
        antigen_doses.sort(key=lambda d: d.administration_date)
    return groups
