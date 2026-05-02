# Knowledge Base — Calendario vaccinale svizzero 2026

Base dati canonica per il sistema di analisi del libretto vaccinale.
Versione: 2026.1 — Fonte: UFSP/CFV, febbraio 2026.

## File

### `vaccines_catalog.yaml`
Catalogo dei vaccini disponibili in Svizzera con mapping nome commerciale → antigeni coperti.
Usato per normalizzare i record estratti dal libretto: "Infanrix hexa" → 6 antigeni separati.

**Sezioni:**
- `products`: lista vaccini con nome, alias, produttore, antigeni, fascia d'età omologata
- `antigen_equivalences`: gruppi di antigeni equivalenti per il rule engine
- `deprecated_products`: vaccini non più raccomandati (Triviraten, PPV23, Zostavax)
- `historical_schemas`: schemi vecchi (3+1 pre-2018) che NON vanno flaggati come errori

### `vaccination_schedule_2026.yaml`
Schema vaccinale strutturato per antigene con regole machine-readable.
Cuore del rule engine.

**Per ogni antigene:**
- `recommendation_level`: base / complementary / risk_group
- `chapter_ref`: riferimento al capitolo del calendario (per spiegazioni)
- `primary_schedule`: dosi attese ed età
- `boosters`: richiami programmati
- `catchup_rules`: regole di recupero per chi è in ritardo
- `contraindications`: controindicazioni assolute

**Sezione finale `age_milestones`:** usata per generare il calendario futuro
personalizzato di un paziente in base alla sua età attuale.

### `risk_groups.yaml`
Mapping condizione clinica / professione / situazione → vaccinazioni aggiuntive.
Tre macro-categorie:
- `clinical_conditions`: malattie croniche (Tabella 5 del calendario)
- `pregnancy_and_neonates`: gravidanza, prematurità, neonati
- `occupational_and_lifestyle`: professioni e situazioni a rischio (Tabella 8)

## Convenzioni antigeni

| Codice | Significato |
|--------|-------------|
| D / d | Difterite full / dose ridotta |
| T | Tetano |
| Pa / pa | Pertosse acellulare full / ridotta |
| IPV | Polio inattivata |
| Hib | H. influenzae b |
| HBV / HAV | Epatite B / A |
| M, O, R, V | Morbillo, Orecchioni, Rosolia, Varicella |
| PCV13/15/20/21 | Pneumococco coniugato (valenza) |
| MenB / MenACWY | Meningococco B / ACWY |
| HPV9 | Papillomavirus 9-valente |
| FSME | Encefalite da zecche |
| RV | Rotavirus |
| HZ | Herpes zoster (Shingrix) |

## Mantenimento

Il calendario UFSP esce ogni anno a febbraio. Procedura di aggiornamento:
1. Bump `metadata.version` (es. 2027.1)
2. Diff con la versione precedente, aggiornare regole modificate
3. Test di regressione su libretti già analizzati
4. Validazione clinica da farmacista/medico

## Validazione

I file YAML sono validati al caricamento. Schema Pydantic in arrivo nella Fase 1.

## Note importanti per il rule engine

- **Mai ricominciare uno schema da zero** se interrotto (vedi tabelle 3-4 del calendario)
- **Schemi storici (3+1) contano come completi** per persone nate ≤2018
- **Le finestre di recupero scadute** vanno comunicate ma non come "errore"
- **PPV23 ricevuto** richiede dose extra con PCV a valenza superiore (intervallo ≥1 anno)
- **Triviraten** invalida la vaccinazione orecchioni → ripetere
