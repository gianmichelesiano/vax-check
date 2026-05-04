# Task: Sezione "Riferimenti vaccinali" — supporto al farmacista

**Priorità:** Media
**Prerequisiti:** Frontend Next.js funzionante, API `/api/kb/version` e `/api/catalog/products` già implementati
**Effort stimato:** 3-4 giorni

---

## Obiettivo

Aggiungere una sezione consultabile nell'app VaxCheck che permette a Maria Lucia
(e qualsiasi farmacista) di consultare rapidamente le informazioni del calendario
vaccinale svizzero UFSP 2026 direttamente durante la consulenza, senza dover
aprire il PDF ufficiale.

La sezione è **read-only** — nessuna modifica ai dati, solo consultazione.
Visibile a tutti gli utenti senza restrizioni.

---

## Dove si trova nell'app

- **Voce di menu:** "Riferimenti" (nuova voce in top nav desktop / bottom nav mobile)
- **URL:** `/riferimenti`
- **Accesso alternativo:** da ogni report, link "Consulta calendario" accanto al `chapter_ref`

---

## Contenuto da mostrare — 4 tab

Tutti i dati vengono dalla knowledge base YAML tramite API.
Nessun dato hardcoded nel frontend.

---

### Tab 1 — Calendario vaccinale

**Fonte:** `vaccination_schedule_2026.yaml` → sezione `antigens`

Mostra la tabella di tutti gli 18 antigeni con:

| Colonna | Fonte YAML | Esempio |
|---------|-----------|---------|
| Nome antigene | `full_name` | "Difterite, Tetano, Pertosse" |
| Tipo raccomandazione | `recommendation_level` | Badge: "Base" / "Complementare" / "Gruppo a rischio" |
| Schema primario | `primary_schedule` | "3 dosi: 2-4-12 mesi" |
| Richiami | `boosters` | "4-7 anni, 11-15 anni, 25 anni..." |
| Capitolo UFSP | `chapter_ref` | "1.1.b/c" (cliccabile → link PDF UFSP) |

Righe raggruppate per tipo:
1. **Vaccinazioni di base** (`base`) — 9 antigeni
2. **Vaccinazioni complementari** (`complementary`) — 7 antigeni
3. **Gruppi a rischio** (`risk_group`) — 2 antigeni

Campo ricerca rapida (filtra per nome antigene).

---

### Tab 2 — Catalogo prodotti

**Fonte:** `vaccines_catalog.yaml` → sezione `products`

Lista dei 48 prodotti omologati in Svizzera, cercabile per nome.

Per ogni prodotto mostrare:
- Nome commerciale + alias se presenti
- Produttore
- Antigeni coperti (badge colorati, es. `D` `T` `Pa` `IPV` `Hib` `HBV`)
- Fascia età omologata (es. "2 mesi – 7 anni")
- Note cliniche se presenti

**Sezione separata: Prodotti deprecati** (3 prodotti)
Evidenziati con banner rosso/ambra e motivo della deprecazione:
- ⚠️ Triviraten — *"Ceppo Rubini orecchioni inefficace; vaccinazioni con questo prodotto vanno ripetute"*
- ⚠️ Pneumovax 23 — *"Non più raccomandato dal 2014; richiede dose recupero con PCV a valenza superiore"*
- ⚠️ Zostavax — *"Vaccino vivo sostituito da Shingrix dal 2022"*

---

### Tab 3 — Gruppi a rischio

**Fonte:** `risk_groups.yaml`

Tre sezioni collassabili (accordion):

**Condizioni cliniche** (33 condizioni)
Per ogni condizione: nome, e lista vaccini aggiuntivi raccomandati.
Esempi: asplenia → MenACWY + MenB + PCV; dialisi → HBV + PCV + Influenza.

**Situazioni occupazionali** (20 situazioni)
Esempi: personale sanitario → HBV + MOR + V + Influenza annuale;
veterinari → Rabbia; zone FSME → FSME.

**Gravidanza e neonati** (5 situazioni)
Esempi: gravidanza → Influenza + COVID (2°-3° trimestre) + dTpa + RSV;
neonato madre HBsAg+ → protocollo HBV specifico.

Ogni sezione ha ricerca rapida per parola chiave.

---

### Tab 4 — Versione KB

**Fonte:** `vaccination_schedule_2026.yaml` → `metadata` + file `kb/CHANGELOG.md`

Mostrare:
- Versione attiva: `2026.1`
- Data pubblicazione UFSP: `2026-02-01`
- Link al PDF ufficiale UFSP
- Contenuto del CHANGELOG (se esiste il file)
- Disclaimer: *"I dati mostrati riflettono il calendario UFSP alla versione indicata.
  Verificare sempre sul sito ufficiale per aggiornamenti recenti."*

---

## API da aggiungere al backend

Aggiungere a `src/vaxcheck/api/routers/catalog.py`:

```
GET /api/kb/full
```

Response:
```json
{
  "metadata": {
    "version": "2026.1",
    "publication_date": "2026-02-01",
    "source": "UFSP/CFV"
  },
  "antigens": [
    {
      "code": "DTP",
      "full_name": "Difterite, Tetano, Pertosse",
      "recommendation_level": "base",
      "chapter_ref": "1.1.b/c, 1.2.a, 1.3.a, 1.4.a, 1.5.a",
      "primary_schedule_summary": "3 dosi: 2-4-12 mesi (schema 2+1)",
      "boosters_summary": "4-7 anni, 11-15 anni, 25 anni, poi ogni 20 anni",
      "raw": { ... }
    }
  ],
  "products": [ ... ],
  "deprecated_products": [ ... ],
  "risk_groups": {
    "clinical_conditions": [ ... ],
    "occupational": [ ... ],
    "pregnancy": [ ... ]
  },
  "changelog": "## 2026.1\n..."
}
```

Il backend legge `kb/CHANGELOG.md` se esiste, ritorna stringa vuota altrimenti.
Aggiungi il campo `primary_schedule_summary` e `boosters_summary` come stringhe
leggibili generate lato backend (non lasciare al frontend il parsing del YAML grezzo).

---

## Componenti frontend da creare

```
frontend/src/
├── app/
│   └── riferimenti/
│       └── page.tsx              # pagina principale con 4 tab
└── components/
    └── kb/
        ├── CalendarioTab.tsx     # Tab 1
        ├── AntigenRow.tsx        # riga singolo antigene
        ├── CatalogoTab.tsx       # Tab 2
        ├── ProductCard.tsx       # card singolo prodotto
        ├── DeprecatedBanner.tsx  # banner prodotti deprecati
        ├── RischiTab.tsx         # Tab 3
        ├── RiskGroupSection.tsx  # accordion per categoria
        └── VersioneTab.tsx       # Tab 4
```

---

## Navigazione

Aggiungere voce "Riferimenti" a:
- **Top nav desktop** (tra "Pazienti" e "Impostazioni")
- **Bottom nav mobile** — sostituisce "Impostazioni" che diventa accessibile
  dal menu "..." o da un link dentro Riferimenti

**Deep link dal report:** ogni `chapter_ref` nel report (es. "cap. 1.1.b") diventa
un link che apre `/riferimenti?tab=calendario&antigen=DTP`.

---

## UX e design

- La pagina è **consultazione rapida**, non documentazione completa.
  Testo conciso, niente paragrafi lunghi.
- Su mobile le tab diventano uno **Select** dropdown (4 tab non ci stanno in riga).
- Il campo ricerca è **sempre visibile** in cima a ogni tab.
- I badge antigeni usano gli stessi colori del resto dell'app
  (verde = base, blu = complementare, grigio = rischio).
- Nessuna funzionalità di modifica — tutto read-only.

---

## Test

- Verifica che tutti i 18 antigeni siano visibili nel Tab 1
- Verifica che tutti i 48 prodotti siano nel Tab 2
- Verifica che i 3 prodotti deprecati abbiano il banner di avviso
- Verifica che la ricerca filtri correttamente in ogni tab
- Verifica il deep link dal report al calendario (`?tab=calendario&antigen=DTP`)
- Verifica che su mobile le tab diventino Select
- Verifica che la versione KB mostrata corrisponda al metadata del file YAML

---

## Note per lo sviluppatore

- I dati cambiano ogni febbraio (aggiornamento calendario). La pagina deve
  sempre riflettere la versione corrente della KB — niente hardcoded.
- Il campo `raw` nell'API è per debug — non mostrarlo nell'UI.
- Il `chapter_ref` può contenere più riferimenti separati da virgola
  (es. `"1.1.b/c, 1.2.a"`). Mostrare come lista di badge separati.
- Il link al PDF UFSP è: `https://www.bag.admin.ch/calendariovaccinale`
- `primary_schedule_summary` e `boosters_summary` devono essere generati
  lato backend in italiano leggibile — non richiedere al frontend di parsare
  la struttura YAML complessa degli schedule.