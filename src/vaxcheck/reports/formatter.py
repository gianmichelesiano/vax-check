from __future__ import annotations

from vaxcheck.domain.compliance import ComplianceReport, MissingVaccinePriority

PRIORITY_LABELS: dict[MissingVaccinePriority, str] = {
    MissingVaccinePriority.URGENT: "URGENTE",
    MissingVaccinePriority.DUE_NOW: "DA FARE ORA",
    MissingVaccinePriority.UPCOMING: "IN ARRIVO",
    MissingVaccinePriority.CATCHUP_AVAILABLE: "RECUPERO DISPONIBILE",
    MissingVaccinePriority.CATCHUP_CLOSED: "RECUPERO CHIUSO",
}


def format_report_italian(report: ComplianceReport) -> str:
    """Format a ComplianceReport as human-readable Italian text."""
    person = report.person
    lines: list[str] = []

    lines.append("=" * 70)
    lines.append("  VAXCHECK — REPORT DI CONFORMITÀ VACCINALE")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Paziente: {person.given_name} {person.family_name}")
    lines.append(f"Nato/a il: {person.birth_date.strftime('%d.%m.%Y')} ({person.age_years} anni)")
    lines.append(f"Data valutazione: {report.evaluation_date.strftime('%d.%m.%Y')}")
    lines.append(f"Engine: {report.engine_used} v{report.engine_version}")
    lines.append(f"Somministrazioni analizzate: {report.total_records}")
    lines.append("")

    # Overall status
    if report.overall_compliance:
        lines.append("✓ STATO GENERALE: IN REGOLA")
        lines.append("  Tutte le vaccinazioni di base sono complete.")
    else:
        lines.append("✗ STATO GENERALE: VACCINAZIONI MANCANTI")
    lines.append("")

    # Per-antigen status
    lines.append("-" * 70)
    lines.append("STATO PER ANTIGENE")
    lines.append("-" * 70)
    for code, status in sorted(report.antigen_statuses.items()):
        check = "✓" if status.is_complete else "✗"
        dose_info = f"{status.doses_received}/{status.doses_required} dosi"
        schema = f" ({status.schema_followed})" if status.schema_followed else ""
        lines.append(f"  {check} {code}: {dose_info}{schema}")
        if status.notes:
            for note in status.notes:
                lines.append(f"     ⚠ {note}")
    lines.append("")

    # Missing vaccines
    if report.missing_vaccines:
        lines.append("-" * 70)
        lines.append("VACCINAZIONI MANCANTI O IN RITARDO")
        lines.append("-" * 70)
        for mv in report.missing_vaccines:
            priority_label = PRIORITY_LABELS.get(mv.priority, mv.priority.value)
            lines.append(f"  [{priority_label}] {mv.antigen}")
            lines.append(f"  Motivo: {mv.reason}")
            lines.append(f"  Schema raccomandato: {mv.recommended_schedule}")
            if mv.age_window:
                lines.append(f"  Finestra: {mv.age_window[0]}-{mv.age_window[1]} anni")
            if mv.chapter_ref:
                lines.append(f"  Riferimento: capitolo {mv.chapter_ref}")
            lines.append("")
    else:
        lines.append("Nessuna vaccinazione mancante rilevata.")
        lines.append("")

    # Future plan
    if report.future_plan:
        lines.append("-" * 70)
        lines.append("CALENDARIO FUTURO PREVISTO")
        lines.append("-" * 70)
        for item in report.future_plan:
            date_str = item.target_date_estimate.strftime("%d.%m.%Y") if item.target_date_estimate else "da definire"
            age_str = (
                str(item.target_age_years)
                if isinstance(item.target_age_years, int)
                else f"{item.target_age_years[0]}-{item.target_age_years[1]}"
            )
            lines.append(f"  {item.antigen}: {item.plan_type} a {age_str} anni ({date_str})")
        lines.append("")

    # Warnings
    if report.warnings:
        lines.append("-" * 70)
        lines.append("AVVISI")
        lines.append("-" * 70)
        for w in report.warnings:
            lines.append(f"  ⚠ {w}")
        lines.append("")

    # Disclaimer
    lines.append("-" * 70)
    lines.append(report.disclaimer)
    lines.append("-" * 70)

    return "\n".join(lines)
