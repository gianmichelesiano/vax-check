# VaxCheck — Project Handoff

> Documento di continuità del progetto. Versione finale per migrazione.
>
> **Versione:** 0.4 — 1 maggio 2026
> **Ultima modifica:** Decisione Opzione 1 (granularità antigeni) confermata

---

## 1. Cos'è VaxCheck

Sistema **on-premise** di analisi vaccinale per farmacie svizzere che, dato in input
i dati del paziente e i vaccini ricevuti, produce:

1. **Report di conformità** rispetto al calendario UFSP 2026
2. **Lista vaccini mancanti** con priorità e finestre di recupero
3. **Calendario vaccinale futuro personalizzato** fino ai 65+ anni

**Utente target:** Maria Lucia (moglie di Gianmichele), farmacista in Svizzera.

**NON è:** dispositivo medico, sostituto del medico curante, prescrittore.
È un **ausilio alla consulenza** con disclaimer esplicito.

---

## 2. Vincoli architetturali confermati

### ON-PREMISE OBBLIGATORIO
- Tutto il software gira su un PC della farmacia
- I dati paziente NON escono mai dalla rete locale
- Vincoli legali: nLPD svizzera, art. 321 CP (segreto professionale farmacista)

### Cosa NON va in cloud
- Nome, data nascita, contatti pazienti
- Storico vaccinazioni
- Foto del libretto (futuro OCR)

### Cosa PUÒ uscire (solo in futuro, non MVP)
- File YAML del calendario aggiornato (download da GitHub pubblico)
- Foto libretto **anonimizzata** verso Claude API per OCR (futuro, con consenso)

---

## 3. SCOPE MVP

### DENTRO l'MVP
1. Inserimento manuale dati paziente
2. Inserimento manuale vaccini ricevuti
3. Rule engine DUALE (deterministico + LLM in parallelo)
4. Tre output (conformità, mancanti, calendario futuro)
5. UI Streamlit
6. Persistenza PostgreSQL cifrato

### FUORI MVP — Feature future
- **B1**: OCR Vision per libretto (Claude API anonimizzata)
- **C2**: Auto-update calendario (GitHub + GPG signed tarball)
- Export PDF, storico, reminder, multi-tenant

---

## 4. STRATEGIA RULE ENGINE — Duale

Due implementazioni con stessa interfaccia:

```python
class RuleEngine(Protocol):
    def evaluate(
        self,
        person: Person,
        records: list[VaccinationRecord],
        knowledge_base: KnowledgeBase,
    ) -> ComplianceReport: ...
```

**A. Deterministico (Python puro)** — default in produzione
- 100% riproducibile, auditabile, difendibile legalmente
- Veloce (<100ms), costo zero

**B. LLM (Claude API in dev / Ollama locale in prod opt-in)** — per dev/spiegazioni
- Generazione test cases, validazione KB
- Spiegazioni naturali (post-process su output deterministico)

**Test di parity** obbligatorio: stesso input → output deve coincidere su conformità sì/no e lista mancanti.

---

## 5. DECISIONE GRANULARITÀ ANTIGENI — Opzione 1 (CONFERMATA)

**Scelta:** salvare 1 record per somministrazione (raw) + normalizzare a runtime.

```
DB salva:
  VaccinationRecord(product="Infanrix hexa", date=2018-03-21)

Runtime espande a:
  NormalizedDose(antigen=D, date=2018-03-21, source_product="Infanrix hexa")
  NormalizedDose(antigen=T, date=2018-03-21, source_product="Infanrix hexa")
  NormalizedDose(antigen=Pa, date=2018-03-21, source_product="Infanrix hexa")
  NormalizedDose(antigen=IPV, date=2018-03-21, source_product="Infanrix hexa")
  NormalizedDose(antigen=Hib, date=2018-03-21, source_product="Infanrix hexa")
  NormalizedDose(antigen=HBV, date=2018-03-21, source_product="Infanrix hexa")
```

**Vantaggi:**
- Storage ridotto
- Correzioni catalogo (es. mapping prodotto→antigeni cambia) non richiedono migrazione dati
- Trail di audit chiaro: cosa è stato somministrato letteralmente
- Normalizzazione testabile separatamente

---

## 6. Stack tecnico MVP

| Layer | Tecnologia |
|-------|-----------|
| UI | Streamlit (locale) |
| Backend | FastAPI + Pydantic |
| Rule engine A | Python puro |
| Rule engine B | LLM (Claude/Ollama via interfaccia) |
| DB | PostgreSQL cifrato at-rest |
| KB | YAML + pydantic-settings |
| Deploy | Docker compose locale |
| OS host | Linux mini-PC (NUC i7 32GB) |

---

## 7. Knowledge Base (Fase 0 — COMPLETATA)

Quattro file in `kb/`:
- `vaccines_catalog.yaml` — 48 prodotti svizzeri con mapping antigeni
- `vaccination_schedule_2026.yaml` — 18 antigeni con regole UFSP 2026
- `risk_groups.yaml` — 33 condizioni cliniche + 20 situazioni occupazionali
- `README.md` — documentazione

**Validazione:** testata sul libretto reale di Clara (8 anni, 14 vaccini).

---

## 8. Piano di implementazione MVP

| Fase | Nome | Stato | Effort |
|------|------|-------|--------|
| 0 | Knowledge Base YAML | DONE | 1-2 giorni |
| 1 | Schema Pydantic puri | TODO | 1 giorno |
| 2 | Rule engine A (deterministico) | TODO | 4-5 giorni |
| 3 | Rule engine B (LLM) | TODO | 2-3 giorni |
| 4 | Test parity + validazione | TODO | 2 giorni |
| 5 | Generazione 3 report | TODO | 2-3 giorni |
| 6 | UI Streamlit | TODO | 2-3 giorni |
| 7 | Persistenza PostgreSQL + Docker | TODO | 1-2 giorni |
| 8 | Validazione clinica con Maria Lucia | continua | - |

**MVP target:** ~3 settimane part-time.

---

## 9. Test case di riferimento: Clara Siano

Dati anagrafici fittizi solo per test:
- Nome: Clara Siano
- Nata: 15.01.2018
- Età attuale: 8 anni (al 30.04.2026)

**Vaccinazioni nel libretto:**

| Data | Prodotto |
|------|----------|
| 21.03.2018 | Infanrix hexa |
| 21.03.2018 | Prevenar 13 |
| 24.05.2018 | Infanrix hexa |
| 24.05.2018 | Prevenar 13 |
| 12.07.2018 | Infanrix hexa |
| 05.11.2018 | Priorix-Tetra |
| 04.02.2019 | Priorix-Tetra |
| 04.02.2019 | Prevenar 13 |
| 15.10.2019 | Infanrix hexa |
| 11.02.2020 | Menveo |
| 23.04.2024 | Adacel-Polio |
| 23.04.2024 | FSME-Immun Junior |
| 10.05.2024 | FSME-Immun Junior |
| 11.11.2024 | FSME-Immun Junior |

**Conformità attesa:**
- DTPa-IPV-Hib-HBV completo (schema 3+1)
- MORV completo (2 dosi)
- PCV13 completo (3 dosi)
- MenACWY 1 dose (recupero possibile a 11-15 anni)
- FSME completo (3 dosi)
- Richiamo prescolare 4-7 anni (Adacel-Polio)
- MenB mai fatto, finestra recupero infantile chiusa, recuperabile a 11-15 anni
- Prossimi: HPV (11-14), richiami DTPa+MenACWY+MenB (11-15)

---

## 10. Decisioni prese e rationale

| Decisione | Rationale |
|-----------|-----------|
| KB in YAML | Manutenibile da farmacista |
| Rule engine duale (A+B) | A per produzione, B per dev/validazione |
| Modelli Pydantic puri | Domain non legato a UI |
| **Opzione 1 granularità antigeni** | Storage minimo, correzioni catalogo facili |
| MVP solo manuale, no OCR | Validare prima il rule engine |
| On-premise totale | LPD svizzera + art. 321 CP |
| Streamlit per UI | MVP rapido |
| PostgreSQL cifrato | Multi-utente futuro, robusto |

---

## 11. Profilo utente Gianmichele

- Senior Software Engineer / Tech Lead presso NGFT (Switzerland)
- Stack: FastAPI, NestJS, PostgreSQL/pgvector, CrewAI, PydanticAI, Kafka, Keycloak
- Italiano nativo, comunicazione informale e diretta
- Codice in inglese, spiegazioni in italiano
- Tempo limitato (sere/weekend, famiglia con Maria Lucia, Clara, Michele)
- Mac M4 Max (128GB RAM) per dev
- Per produzione farmacia: mini-PC dedicato da acquistare

---

## 12. Riferimenti

- Calendario vaccinale svizzero 2026 (PDF UFSP)
- UFSP: https://www.bag.admin.ch/calendariovaccinale
- InfoVac: https://www.infovac.ch/it
- nLPD: https://www.fedlex.admin.ch/eli/cc/2022/491/it
- pharmaSuisse: https://www.pharmasuisse.org

---

*Versione finale 0.4 — pronta per implementazione autonoma.*
