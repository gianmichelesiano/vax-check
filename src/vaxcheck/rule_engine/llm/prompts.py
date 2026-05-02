from __future__ import annotations

import json
from datetime import date

from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import VaccinationRecord

SYSTEM_PROMPT = """Sei un esperto del calendario vaccinale svizzero UFSP 2026.
Analizzi la conformità vaccinale di un paziente in base ai vaccini ricevuti e alla knowledge base fornita.

Regole inderogabili:
- Rispondi SOLO con JSON valido che corrisponde esattamente allo schema ComplianceReport fornito.
- Usa i chapter_ref dalla knowledge base per giustificare ogni decisione.
- Se sei incerto su una valutazione, aggiungi un warning invece di tirare a indovinare.
- Rispetta gli schemi storici: i nati prima del 2019 possono aver seguito schema 3+1 (4 dosi DTP).
- Mai ricominciare uno schema da zero — continua da dove il paziente ha interrotto.
- Non inventare antigeni non presenti nella KB.
- Per ogni antigene BASE non completo, segnalalo come missing_vaccine con priorità appropriata.
- Il campo age_window nei MissingVaccine deve essere una tupla [età_min, età_max] in anni o null.
"""

SCHEMA_DESCRIPTION = """
Output JSON schema (ComplianceReport):
{
  "overall_compliance": true/false,
  "antigen_statuses": {
    "DTP": {
      "antigen": "DTP",
      "is_complete": true/false,
      "doses_received": N,
      "doses_required": N,
      "schema_followed": "2+1" | "3+1" | null,
      "notes": [...],
      "chapter_ref": "1.1.b/c, 1.2.a, ..."
    },
    ...
  },
  "missing_vaccines": [
    {
      "antigen": "MenB",
      "priority": "urgent" | "due_now" | "upcoming" | "catchup_available" | "catchup_closed",
      "reason": "spiegazione in italiano",
      "recommended_schedule": "descrizione schema raccomandato",
      "chapter_ref": "...",
      "age_window": [min, max] | null
    }
  ],
  "future_plan": [
    {
      "antigen": "HPV",
      "target_age_years": [11, 14] | 65,
      "target_date_estimate": "YYYY-MM-DD" | null,
      "plan_type": "richiamo" | "vaccinazione_base" | "stagionale",
      "chapter_ref": "..."
    }
  ],
  "warnings": ["eventuali warning"]
}
"""


def build_evaluation_prompt(
    person: Person,
    records: list[VaccinationRecord],
    kb: KnowledgeBase,
    evaluation_date: date,
) -> str:
    """Build the full evaluation prompt with KB context and patient data."""

    # Summarize KB antigens (compact, key rules only)
    kb_summary_lines: list[str] = []
    for code, rule in sorted(kb.antigens.items()):
        kb_summary_lines.append(
            f"- {code} ({rule.full_name}): level={rule.recommendation_level.value}, "
            f"chapter={rule.chapter_ref or 'N/A'}"
        )
        if rule.primary_schedule:
            kb_summary_lines.append(f"  primary_schedule: {json.dumps(rule.primary_schedule, default=str)}")
        if rule.boosters:
            kb_summary_lines.append(f"  boosters: {json.dumps(rule.boosters, default=str)}")
        if rule.catchup_rules:
            kb_summary_lines.append(f"  catchup: {json.dumps(rule.catchup_rules, default=str)}")
        if rule.contraindications:
            kb_summary_lines.append(f"  contraindications: {rule.contraindications}")

    kb_text = "\n".join(kb_summary_lines)

    # Summarize products catalog
    products_lines: list[str] = []
    for product in sorted(kb.products, key=lambda p: p.name):
        products_lines.append(f"- {product.name}: antigens={product.antigens}")

    products_text = "\n".join(products_lines)

    # Patient data
    records_lines: list[str] = []
    for r in sorted(records, key=lambda r: r.administration_date):
        records_lines.append(f"- {r.administration_date.isoformat()}: {r.product_name}")

    records_text = "\n".join(records_lines) if records_lines else "(nessun record)"

    clinical_lines: list[str] = []
    for c in person.clinical_conditions:
        clinical_lines.append(f"- {c.code}: {c.label}" + (f" (dal {c.onset_date})" if c.onset_date else ""))

    occupations = ", ".join(person.occupational_situations) if person.occupational_situations else "nessuna"

    prompt = f"""## PAZIENTE

Nome: {person.given_name} {person.family_name}
Data di nascita: {person.birth_date.isoformat()}
Sesso: {person.sex.value}
Età: {person.age_years} anni ({person.age_months} mesi)
Anno di nascita: {person.birth_year}
Condizioni cliniche: {chr(10).join(clinical_lines) if clinical_lines else 'nessuna'}
Situazioni occupazionali/a rischio: {occupations}

## VACCINI RICEVUTI ({len(records)} somministrazioni)

{records_text}

## KNOWLEDGE BASE — REGOLE PER ANTIGENE

{kb_text}

## CATALOGO PRODOTTI → ANTIGENI

{products_text}

## DATA VALUTAZIONE

{evaluation_date.isoformat()}

## ISTRUZIONI

1. Per ogni prodotto somministrato, espandi nei suoi antigeni costituenti usando il catalogo.
2. Per ogni antigene nella KB, valuta se il paziente ha completato lo schema in base a:
   - Anno di nascita (≤2018 = schema 3+1, ≥2019 = schema 2+1 per DTP)
   - Età attuale
   - Dosi ricevute (contando le equivalenze: D e d contano entrambe per difterite, PCV13/15/20/21 per pneumococco, ecc.)
3. Per ogni antigene BASE non completo, genera un MissingVaccine con priorità appropriata.
4. Genera il future_plan con le prossime vaccinazioni attese.
5. overall_compliance = true SOLO SE tutti gli antigeni BASE sono completi.

{SCHEMA_DESCRIPTION}

Rispondi SOLO con il JSON del ComplianceReport. Nessun altro testo."""

    return prompt
