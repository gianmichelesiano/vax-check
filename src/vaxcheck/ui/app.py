"""VaxCheck Streamlit UI — Pharmacy-facing web application.

Run with:
    streamlit run src/vaxcheck/ui/app.py
"""
# ruff: noqa: E402 (imports after sys.path setup)

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

# Ensure vaxcheck is importable when run as `streamlit run`
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st

from vaxcheck.domain.compliance import ComplianceReport, MissingVaccinePriority
from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.domain.person import ClinicalCondition, Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.kb.loader import load_knowledge_base
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine

# ──────────────────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────────────────

st.set_page_config(
    page_title="VaxCheck — Analisi Vaccinale",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────

KB_DIR = _project_root.parent / "kb"
PRIORITY_ICONS: dict[MissingVaccinePriority, str] = {
    MissingVaccinePriority.URGENT: "🔴",
    MissingVaccinePriority.DUE_NOW: "🟠",
    MissingVaccinePriority.UPCOMING: "🔵",
    MissingVaccinePriority.CATCHUP_AVAILABLE: "🟢",
    MissingVaccinePriority.CATCHUP_CLOSED: "⚫",
}
PRIORITY_LABELS: dict[MissingVaccinePriority, str] = {
    MissingVaccinePriority.URGENT: "URGENTE",
    MissingVaccinePriority.DUE_NOW: "DA FARE ORA",
    MissingVaccinePriority.UPCOMING: "IN ARRIVO",
    MissingVaccinePriority.CATCHUP_AVAILABLE: "RECUPERO DISPONIBILE",
    MissingVaccinePriority.CATCHUP_CLOSED: "RECUPERO CHIUSO",
}


# ──────────────────────────────────────────────────────────
# Session State Initialization
# ──────────────────────────────────────────────────────────

def _init_session() -> None:
    today = date.today()
    defaults: dict[str, Any] = {
        "records": [],
        "report": None,
        "kb": None,
        "kb_error": None,
        "engine": None,
        # Patient form defaults
        "pt_name": "",
        "pt_surname": "",
        "pt_birth": today.replace(year=today.year - 30),
        "pt_sex": 0,  # Femmina
        "pt_conditions": [],
        "pt_occupations": [],
        "pt_notes": "",
        "pt_eval_date": today,
        "demo_selector": "Nessuno",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ──────────────────────────────────────────────────────────
# Knowledge Base Loader (cached)
# ──────────────────────────────────────────────────────────

@st.cache_resource
def _load_kb() -> KnowledgeBase | None:
    try:
        return load_knowledge_base(KB_DIR)
    except Exception as exc:
        st.session_state["kb_error"] = str(exc)
        return None


def get_kb() -> KnowledgeBase:
    kb = st.session_state["kb"]
    if kb is None:
        kb = _load_kb()
        st.session_state["kb"] = kb
    if kb is None:
        st.error(f"Errore caricamento Knowledge Base: {st.session_state.get('kb_error', 'sconosciuto')}")
        st.stop()
    return kb  # type: ignore[no-any-return]


def get_engine() -> DeterministicRuleEngine:
    engine = st.session_state["engine"]
    if engine is None:
        engine = DeterministicRuleEngine()
        st.session_state["engine"] = engine
    return engine  # type: ignore[no-any-return]


# ──────────────────────────────────────────────────────────
# Helper: Run analysis
# ──────────────────────────────────────────────────────────

def _run_analysis(person: Person, records: list[VaccinationRecord], eval_date: date) -> ComplianceReport:
    kb = get_kb()
    engine = get_engine()
    return engine.evaluate(person, records, kb, eval_date)


# ──────────────────────────────────────────────────────────
# Sidebar — Patient Data
# ──────────────────────────────────────────────────────────

def _render_patient_form() -> Person | None:
    st.sidebar.header("👤 Dati Paziente")

    # Preload demo: selectbox + load button
    demo_options = {
        "Nessuno": None,
        "👧 Clara (8 anni, libretto completo)": "clara",
        "👶 Luca (4 mesi, inizio vaccinazioni)": "luca",
        "👨 Marco (35 anni, adulto in regola)": "marco",
        "👴 Giovanni (70 anni, diabetico, asplenico)": "giovanni",
    }
    selected_demo_label = st.sidebar.selectbox(
        "📥 Paziente dimostrativo",
        options=list(demo_options.keys()),
        key="demo_selector",
    )
    if st.sidebar.button("Carica paziente demo", type="secondary", use_container_width=True,
                         disabled=(demo_options[selected_demo_label] is None)):
        _load_demo(demo_options[selected_demo_label])
        st.rerun()

    given_name = st.sidebar.text_input("Nome", key="pt_name", placeholder="es. Clara")
    family_name = st.sidebar.text_input("Cognome", key="pt_surname", placeholder="es. Siano")

    today = date.today()
    min_birth = today.replace(year=today.year - 120)
    max_birth = today
    birth_date = st.sidebar.date_input(
        "Data di nascita",
        key="pt_birth",
        min_value=min_birth,
        max_value=max_birth,
        format="DD.MM.YYYY",
    )

    sex_index = st.sidebar.selectbox(
        "Sesso",
        options=[0, 1, 2],
        format_func=lambda i: ["Femmina", "Maschio", "Altro"][i],
        key="pt_sex",
    )
    sex = [Sex.FEMALE, Sex.MALE, Sex.OTHER][sex_index]

    # Clinical conditions
    with st.sidebar.expander("Condizioni cliniche (opzionale)"):
        clinical_conditions: list[ClinicalCondition] = []
        kb = st.session_state.get("kb")
        if kb and kb.risk_groups:
            condition_codes = list(kb.risk_groups.get("clinical_conditions", {}).keys())
            condition_labels = {
                code: kb.risk_groups["clinical_conditions"][code].get("label", code)
                for code in condition_codes
            }
            selected_codes = st.multiselect(
                "Patologie / condizioni",
                options=condition_codes,
                format_func=lambda c: condition_labels.get(c, c),
                help="Seleziona le condizioni cliniche rilevanti",
                key="pt_conditions",
            )
            for code in selected_codes:
                clinical_conditions.append(
                    ClinicalCondition(code=code, label=condition_labels.get(code, code))
                )
        else:
            st.info("Knowledge base non ancora caricata")

    with st.sidebar.expander("Situazioni professionali (opzionale)"):
        occupational: list[str] = []
        kb = st.session_state.get("kb")
        if kb and kb.risk_groups:
            occ_codes = list(kb.risk_groups.get("occupational_and_lifestyle", {}).keys())
            occ_labels = {
                code: kb.risk_groups["occupational_and_lifestyle"][code].get("label", code)
                for code in occ_codes
            }
            occupational = st.multiselect(
                "Professione / stile di vita",
                options=occ_codes,
                format_func=lambda c: occ_labels.get(c, c),
                help="Es. personale sanitario, veterinario, etc.",
                key="pt_occupations",
            )

    notes = st.sidebar.text_area("Note", key="pt_notes", placeholder="Note aggiuntive...", height=68)

    evaluation_date = st.sidebar.date_input(
        "Data valutazione",
        key="pt_eval_date",
        min_value=date(2000, 1, 1),
        max_value=today + timedelta(days=365),
        format="DD.MM.YYYY",
    )
    st.session_state["_eval_date"] = evaluation_date

    if not given_name.strip() or not family_name.strip():
        st.sidebar.warning("Inserire nome e cognome del paziente")
        return None

    return Person(
        given_name=given_name.strip(),
        family_name=family_name.strip(),
        birth_date=birth_date,
        sex=sex,
        clinical_conditions=clinical_conditions,
        occupational_situations=occupational,
        notes=notes.strip() or None,
    )


# ──────────────────────────────────────────────────────────
# Main — Vaccination Records
# ──────────────────────────────────────────────────────────

def _render_records_section(kb: KnowledgeBase) -> None:
    st.header("📋 Vaccinazioni Registrate")

    col_count, col_add = st.columns([1, 3])
    with col_count:
        st.metric("Totale somministrazioni", len(st.session_state.records))

    # Add new record
    st.subheader("➕ Aggiungi somministrazione")

    product_names = [p.name for p in kb.products] if kb else []
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        new_product = st.selectbox(
            "Prodotto",
            options=[""] + product_names,
            format_func=lambda x: "— Seleziona prodotto —" if x == "" else x,
            key="new_product",
        )
    with col2:
        new_date = st.date_input(
            "Data somministrazione",
            value=date.today(),
            min_value=date(1990, 1, 1),
            max_value=date.today() + timedelta(days=30),
            format="DD.MM.YYYY",
            key="new_date",
        )
    with col3:
        new_lot = st.text_input("Lotto (opzionale)", key="new_lot", placeholder="es. A42CB-123A")

    new_notes = st.text_input("Note (opzionale)", key="new_notes", placeholder="Medico, struttura...")

    if st.button("Aggiungi", type="primary", disabled=(new_product == "")):
        record = VaccinationRecord(
            product_name=new_product,
            administration_date=new_date,
            lot_number=new_lot.strip() or None,
            notes=new_notes.strip() or None,
        )
        st.session_state.records.append(record)
        # Clear inputs
        st.session_state.new_product = ""
        st.session_state.new_lot = ""
        st.session_state.new_notes = ""
        st.rerun()

    # List existing records
    if st.session_state.records:
        st.subheader("📄 Registrazioni inserite")
        for i, rec in enumerate(st.session_state.records):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"**{rec.product_name}**")
            with col2:
                st.write(rec.administration_date.strftime("%d.%m.%Y"))
            with col3:
                st.write(rec.lot_number or "—")
            with col4:
                if st.button("🗑️ Rimuovi", key=f"del_{i}"):
                    st.session_state.records.pop(i)
                    st.rerun()
    else:
        st.info("Nessuna vaccinazione registrata. Aggiungi la prima somministrazione qui sopra.")


# ──────────────────────────────────────────────────────────
# Report Display
# ──────────────────────────────────────────────────────────

def _render_report(report: ComplianceReport) -> None:
    st.header("📊 Report di Conformità Vaccinale")

    # ---- Top metrics row ----
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if report.overall_compliance:
            st.success("✅ IN REGOLA")
        else:
            st.error("⚠️ VACCINAZIONI MANCANTI")
    with col2:
        st.metric("Somministrazioni", report.total_records)
    with col3:
        complete_count = sum(1 for s in report.antigen_statuses.values() if s.is_complete)
        total_antigens = len(report.antigen_statuses)
        st.metric("Antigeni completi", f"{complete_count}/{total_antigens}")
    with col4:
        st.metric("Vaccini mancanti", len(report.missing_vaccines))

    # Patient info line
    person = report.person
    st.caption(
        f"Paziente: {person.given_name} {person.family_name} — "
        f"Nato{'a' if person.sex == Sex.FEMALE else ''} il {person.birth_date.strftime('%d.%m.%Y')} "
        f"({person.age_years} anni, {person.age_months} mesi) — "
        f"Valutazione: {report.evaluation_date.strftime('%d.%m.%Y')} — "
        f"Engine: {report.engine_used} v{report.engine_version}"
    )

    st.divider()

    # ---- Tabs ----
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔬 Stato per Antigene",
        "⚠️ Vaccini Mancanti",
        "📅 Calendario Futuro",
        "📝 Dettaglio",
    ])

    with tab1:
        _render_antigen_statuses(report.antigen_statuses)

    with tab2:
        _render_missing_vaccines(report.missing_vaccines)

    with tab3:
        _render_future_plan(report.future_plan)

    with tab4:
        _render_detail(report)


def _render_antigen_statuses(statuses: dict[str, Any]) -> None:
    """Render per-antigen status as a styled table."""
    if not statuses:
        st.info("Nessun antigene valutato.")
        return

    rows: list[dict[str, Any]] = []
    for code, status in sorted(statuses.items()):
        rows.append({
            "Antigene": code,
            "Completo": "✅" if status.is_complete else "❌",
            "Dosi": f"{status.doses_received}/{status.doses_required}",
            "Schema": status.schema_followed or "—",
            "Ultima dose": status.last_dose_date.strftime("%d.%m.%Y") if status.last_dose_date else "—",
            "Prossima dose": status.next_dose_due.strftime("%d.%m.%Y") if status.next_dose_due else "—",
            "Note": "\n".join(status.notes) if status.notes else "",
            "Capitolo UFSP": status.chapter_ref or "—",
        })

    st.dataframe(
        rows,
        use_container_width=True,
        column_config={
            "Antigene": st.column_config.TextColumn(width="small"),
            "Completo": st.column_config.TextColumn(width="small"),
            "Dosi": st.column_config.TextColumn(width="small"),
            "Schema": st.column_config.TextColumn(width="small"),
            "Ultima dose": st.column_config.TextColumn(width="small"),
            "Prossima dose": st.column_config.TextColumn(width="small"),
            "Note": st.column_config.TextColumn(width="medium"),
            "Capitolo UFSP": st.column_config.TextColumn(width="small"),
        },
        hide_index=True,
    )


def _render_missing_vaccines(missing: list[Any]) -> None:
    """Render missing vaccines with priority badges."""
    if not missing:
        st.success("✅ Nessuna vaccinazione mancante rilevata.")
        return

    for mv in sorted(missing, key=lambda m: list(MissingVaccinePriority).index(m.priority)):
        icon = PRIORITY_ICONS.get(mv.priority, "⚪")
        label = PRIORITY_LABELS.get(mv.priority, mv.priority.value)

        if mv.priority == MissingVaccinePriority.CATCHUP_CLOSED:
            st.info(f"{icon} **[{label}] {mv.antigen}**")
        elif mv.priority == MissingVaccinePriority.URGENT:
            st.error(f"{icon} **[{label}] {mv.antigen}**")
        elif mv.priority == MissingVaccinePriority.DUE_NOW:
            st.warning(f"{icon} **[{label}] {mv.antigen}**")
        else:
            st.info(f"{icon} **[{label}] {mv.antigen}**")

        with st.expander(f"Dettagli {mv.antigen}"):
            st.write(f"**Motivo:** {mv.reason}")
            st.write(f"**Schema raccomandato:** {mv.recommended_schedule}")
            if mv.age_window:
                st.write(f"**Finestra d'età:** {mv.age_window[0]}–{mv.age_window[1]} anni")
            if mv.chapter_ref:
                st.write(f"**Riferimento UFSP:** capitolo {mv.chapter_ref}")


def _render_future_plan(plan: list[Any]) -> None:
    """Render future vaccination plan as a timeline."""
    if not plan:
        st.info("Nessun appuntamento futuro previsto.")
        return

    rows: list[dict[str, Any]] = []
    for item in plan:
        age_str = (
            f"{item.target_age_years} anni"
            if isinstance(item.target_age_years, int)
            else f"{item.target_age_years[0]}–{item.target_age_years[1]} anni"
        )
        date_str = item.target_date_estimate.strftime("%d.%m.%Y") if item.target_date_estimate else "da definire"
        rows.append({
            "Antigene": item.antigen,
            "Tipo": item.plan_type,
            "Età target": age_str,
            "Data stimata": date_str,
            "Capitolo UFSP": item.chapter_ref or "—",
        })

    st.dataframe(
        rows,
        use_container_width=True,
        column_config={
            "Antigene": st.column_config.TextColumn(width="small"),
            "Tipo": st.column_config.TextColumn(width="medium"),
            "Età target": st.column_config.TextColumn(width="small"),
            "Data stimata": st.column_config.TextColumn(width="small"),
            "Capitolo UFSP": st.column_config.TextColumn(width="small"),
        },
        hide_index=True,
    )


def _render_detail(report: ComplianceReport) -> None:
    """Render warnings, disclaimer, and raw details."""
    if report.warnings:
        st.subheader("⚠️ Avvisi")
        for w in report.warnings:
            st.warning(w)

    st.subheader("📋 Dati grezzi")
    with st.expander("Persona (JSON)"):
        st.json(report.person.model_dump(mode="json"))

    st.divider()

    st.caption(report.disclaimer)


# ──────────────────────────────────────────────────────────
# Demo Data
# ──────────────────────────────────────────────────────────

def _load_demo(profile: str | None) -> None:
    """Load a demo patient profile into session state."""
    if profile is None:
        return
    demos = {
        "clara": _demo_clara,
        "luca": _demo_luca,
        "marco": _demo_marco,
        "giovanni": _demo_giovanni,
    }
    demos[profile]()


def _demo_clara() -> None:
    """Clara, 8 anni — libretto reale, quasi tutto in regola."""
    st.session_state.pt_name = "Clara"
    st.session_state.pt_surname = "Siano"
    st.session_state.pt_birth = date(2018, 1, 15)
    st.session_state.pt_sex = 0  # Femmina
    st.session_state.pt_conditions = []
    st.session_state.pt_occupations = []
    st.session_state.pt_notes = "Libretto reale. MenB mai fatto, MenACWY 1 sola dose."
    st.session_state.pt_eval_date = date.today()
    st.session_state.records = [
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 3, 21)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2018, 3, 21)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 5, 24)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2018, 5, 24)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 7, 12)),
        VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(2018, 11, 5)),
        VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(2019, 2, 4)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2019, 2, 4)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2019, 10, 15)),
        VaccinationRecord(product_name="Menveo", administration_date=date(2020, 2, 11)),
        VaccinationRecord(product_name="Adacel-Polio", administration_date=date(2024, 4, 23)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 4, 23)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 5, 10)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 11, 11)),
    ]


def _demo_luca() -> None:
    """Luca, 4 mesi — solo prime 2 dosi a 2 mesi, molte finestre aperte."""
    st.session_state.pt_name = "Luca"
    st.session_state.pt_surname = "Bianchi"
    st.session_state.pt_birth = date(2026, 1, 10)
    st.session_state.pt_sex = 1  # Maschio
    st.session_state.pt_conditions = []
    st.session_state.pt_occupations = []
    st.session_state.pt_notes = "Neonato sano. Genitori chiedono consiglio su prosecuzione calendario."
    st.session_state.pt_eval_date = date.today()
    st.session_state.records = [
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2026, 3, 12)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2026, 3, 12)),
        VaccinationRecord(product_name="Rotarix", administration_date=date(2026, 3, 12)),
    ]


def _demo_marco() -> None:
    """Marco, 35 anni — adulto in regola con richiami, FSME completo."""
    st.session_state.pt_name = "Marco"
    st.session_state.pt_surname = "Rossi"
    st.session_state.pt_birth = date(1991, 6, 22)
    st.session_state.pt_sex = 1  # Maschio
    st.session_state.pt_conditions = []
    st.session_state.pt_occupations = []
    st.session_state.pt_notes = "Adulto sano. Ha fatto richiamo dTpa a 25 anni. FSME in ordine."
    st.session_state.pt_eval_date = date.today()
    st.session_state.records = [
        # Infanzia (schema 3+1, nato prima 2019)
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1991, 8, 22)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1991, 10, 22)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1991, 12, 22)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1992, 7, 22)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(1991, 8, 22)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(1991, 10, 22)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(1992, 7, 22)),
        VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(1992, 6, 15)),
        VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(1992, 8, 20)),
        # Richiami
        VaccinationRecord(product_name="Adacel-Polio", administration_date=date(1996, 6, 1)),
        VaccinationRecord(product_name="Boostrix", administration_date=date(2007, 6, 22)),
        VaccinationRecord(product_name="Boostrix", administration_date=date(2016, 6, 22)),
        VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2015, 3, 10)),
        VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2015, 4, 15)),
        VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2016, 4, 10)),
        VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2019, 4, 5)),
        VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2023, 4, 8)),
        VaccinationRecord(product_name="Engerix-B", administration_date=date(1992, 3, 1)),
        VaccinationRecord(product_name="Engerix-B", administration_date=date(1992, 4, 1)),
        VaccinationRecord(product_name="Engerix-B", administration_date=date(1992, 8, 1)),
    ]


def _demo_giovanni() -> None:
    """Giovanni, 70 anni — diabetico, asplenico, necessita vaccinazioni extra."""
    st.session_state.pt_name = "Giovanni"
    st.session_state.pt_surname = "Verdi"
    st.session_state.pt_birth = date(1956, 3, 5)
    st.session_state.pt_sex = 1  # Maschio
    st.session_state.pt_conditions = [
        "diabetes_with_organ_impact",
        "asplenia",
    ]
    st.session_state.pt_occupations = []
    st.session_state.pt_notes = "Diabete tipo 2 con complicanze. Splenectomia 2018. Vive in zona FSME endemica."
    st.session_state.pt_eval_date = date.today()
    st.session_state.records = [
        # Vaccinazioni di base infanzia (parziali, storico)
        VaccinationRecord(product_name="dT", administration_date=date(2006, 5, 10)),
        VaccinationRecord(product_name="dT", administration_date=date(2016, 5, 10)),
        VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2023, 4, 1)),
        VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2023, 5, 1)),
        VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2025, 4, 1)),
        # Influenza stagionale
        VaccinationRecord(product_name="Influvac", administration_date=date(2025, 10, 15)),
        # Pneumococco
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2018, 11, 1)),
    ]


# ──────────────────────────────────────────────────────────
# Main App Entry Point
# ──────────────────────────────────────────────────────────

def main() -> None:
    _init_session()

    st.title("💉 VaxCheck")
    st.caption("Analisi di conformità al calendario vaccinale svizzero UFSP 2026")

    # Load KB (cached, runs once)
    kb = get_kb()
    if st.session_state.get("kb_error"):
        st.error(f"Errore KB: {st.session_state['kb_error']}")
        st.stop()

    # Sidebar — Patient data
    person = _render_patient_form()

    # Main area — Records
    _render_records_section(kb)

    st.divider()

    # Analyze button
    col1, col2 = st.columns([1, 3])
    with col1:
        analyze_clicked = st.button(
            "🔍 Esegui Analisi",
            type="primary",
            disabled=(person is None or len(st.session_state.records) == 0),
            use_container_width=True,
        )

    if not st.session_state.records:
        with col2:
            st.info("👆 Aggiungi le vaccinazioni del paziente, poi clicca 'Esegui Analisi'")

    if analyze_clicked and person is not None and st.session_state.records:
        with st.spinner("Analisi in corso..."):
            eval_date = st.session_state.get("_eval_date", date.today())
            report = _run_analysis(person, st.session_state.records, eval_date)
            st.session_state.report = report

    # Display report
    if st.session_state.report:
        st.divider()
        _render_report(st.session_state.report)


if __name__ == "__main__":
    main()
