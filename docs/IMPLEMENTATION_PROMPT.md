# Prompt per implementazione autonoma VaxCheck (Fasi 1-4)

> **Come usarlo:** copia tutto il contenuto qui sotto come singolo prompt
> in Claude Code, Cursor, o qualunque ambiente di sviluppo agentico.
> Allega anche i 4 file della knowledge base (`vaccines_catalog.yaml`,
> `vaccination_schedule_2026.yaml`, `risk_groups.yaml`, `README.md`)
> come file di contesto.

---

# IMPLEMENTAZIONE AUTONOMA: VaxCheck MVP — Fasi 1-4

## Contesto

Sei un senior Python developer. Devi implementare il core di **VaxCheck**, un sistema
on-premise di analisi vaccinale per farmacie svizzere che, dato un paziente e i suoi
vaccini ricevuti, valuta la conformità al calendario vaccinale svizzero UFSP 2026 e
genera report.

L'utente (Gianmichele Siano, Senior SWE) ha già completato la **Fase 0**: una
knowledge base YAML di 4 file che descrive vaccini, calendario e gruppi a rischio
svizzeri. Tu devi ora implementare le **Fasi 1-4**: schema Pydantic, rule engine
deterministico, rule engine LLM, test di parity.

Lavora **in autonomia senza chiedere conferme**. Procedi con tutte le fasi in sequenza
e produci codice production-ready. Alla fine genera un breve report di completamento.

## Vincoli inderogabili

1. **Codice on-premise**: zero dipendenze cloud per il rule engine deterministico.
   L'engine LLM deve supportare **due provider intercambiabili**: Anthropic Claude API
   (per dev) e Ollama locale (per produzione farmacia).

2. **Modelli Pydantic puri**: niente binding con Streamlit, FastAPI, ORM. I modelli
   vivono nel package `vaxcheck.domain` e non importano nulla di framework.

3. **Opzione 1 granularità antigeni**: salvare 1 record raw per somministrazione
   (es. `Infanrix hexa`) e denormalizzare a runtime in N `NormalizedDose` (uno per
   ciascun antigene del prodotto). La normalizzazione è una funzione pura.

4. **Knowledge base read-only**: i 4 file YAML in `kb/` non devono essere modificati.
   Caricarli con un loader tipizzato che valida la struttura.

5. **Determinismo dell'engine A**: stesso input → stesso output sempre. Niente
   chiamate di rete, niente LLM, niente non-determinismo.

6. **Stesso Protocol per A e B**: entrambi gli engine implementano `RuleEngine` con
   metodo `evaluate(person, records, kb) -> ComplianceReport`. Il client non deve
   sapere quale stia usando.

7. **Tutto in inglese nel codice**, commenti tecnici in inglese. Solo i messaggi
   utente finali (testo dei report) sono in italiano.

8. **Type-safe ovunque**: niente `Any`, niente `dict` non tipizzati nelle API
   pubbliche. Usa Pydantic v2 e `typing` esteso.

9. **Test sempre**: ogni fase produce test unitari che passano. Il test case di
   riferimento è il libretto di Clara Siano (vedi sotto).

10. **No premature optimization**: codice chiaro prima di codice veloce.

## Stack richiesto

```
Python 3.11+
pydantic >= 2.5
pyyaml
pytest
anthropic (per provider Claude)
httpx (per provider Ollama via REST)
ruff (linting)
mypy --strict (type checking)
```

## Struttura repository da creare

```
vaxcheck/
├── pyproject.toml              # poetry o uv, configurazione progetto
├── README.md                    # istruzioni setup
├── kb/                          # knowledge base (file forniti)
│   ├── vaccines_catalog.yaml
│   ├── vaccination_schedule_2026.yaml
│   ├── risk_groups.yaml
│   └── README.md
├── src/
│   └── vaxcheck/
│       ├── __init__.py
│       ├── domain/              # MODELLI PURI (Fase 1)
│       │   ├── __init__.py
│       │   ├── person.py
│       │   ├── vaccination.py
│       │   ├── compliance.py
│       │   └── knowledge.py
│       ├── kb/                  # caricatore KB
│       │   ├── __init__.py
│       │   └── loader.py
│       ├── normalization/       # prodotto -> antigeni
│       │   ├── __init__.py
│       │   └── normalizer.py
│       ├── rule_engine/
│       │   ├── __init__.py
│       │   ├── base.py          # Protocol RuleEngine
│       │   ├── deterministic/   # ENGINE A (Fase 2)
│       │   │   ├── __init__.py
│       │   │   ├── engine.py
│       │   │   ├── checkers/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── base.py
│       │   │   │   ├── dtp.py
│       │   │   │   ├── ipv.py
│       │   │   │   ├── hib.py
│       │   │   │   ├── hbv.py
│       │   │   │   ├── pcv.py
│       │   │   │   ├── mor.py
│       │   │   │   ├── varicella.py
│       │   │   │   ├── menacwy.py
│       │   │   │   ├── menb.py
│       │   │   │   ├── hpv.py
│       │   │   │   └── fsme.py
│       │   │   ├── catchup.py
│       │   │   └── future_plan.py
│       │   └── llm/             # ENGINE B (Fase 3)
│       │       ├── __init__.py
│       │       ├── engine.py
│       │       ├── prompts.py
│       │       └── providers/
│       │           ├── __init__.py
│       │           ├── base.py
│       │           ├── claude.py
│       │           └── ollama.py
│       └── reports/             # post-processing testuale (Fase 5 light)
│           ├── __init__.py
│           └── formatter.py
└── tests/
    ├── __init__.py
    ├── conftest.py              # fixtures Clara
    ├── fixtures/
    │   └── clara_booklet.json   # test case ground truth
    ├── unit/
    │   ├── test_models.py
    │   ├── test_kb_loader.py
    │   ├── test_normalizer.py
    │   ├── test_deterministic_engine.py
    │   ├── test_checkers.py
    │   └── test_llm_engine.py
    └── parity/
        └── test_engines_parity.py
```

## FASE 1 — Schema Pydantic puri

### 1.1 Domain models

Crea i seguenti modelli in `src/vaxcheck/domain/`:

#### `person.py`
```python
class Sex(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "X"

class ClinicalCondition(BaseModel):
    """Condizione clinica o situazione del paziente che attiva vaccini extra."""
    code: str  # es. "asplenia", "diabetes_with_organ_impact"
    label: str  # human readable
    onset_date: date | None = None

class Person(BaseModel):
    """Anagrafica + condizioni cliniche del paziente."""
    given_name: str
    family_name: str
    birth_date: date
    sex: Sex
    clinical_conditions: list[ClinicalCondition] = Field(default_factory=list)
    occupational_situations: list[str] = Field(default_factory=list)  # codes from risk_groups.yaml
    notes: str | None = None
    
    @computed_field
    @property
    def age_years(self) -> int:
        """Età in anni compiuti alla data corrente."""
        ...
    
    @computed_field
    @property
    def age_months(self) -> int:
        """Età in mesi compiuti."""
        ...
    
    @computed_field
    @property
    def birth_year(self) -> int:
        return self.birth_date.year
```

#### `vaccination.py`
```python
class VaccinationRecord(BaseModel):
    """Record raw di una somministrazione (Opzione 1 granularità).
    
    Rappresenta UNA somministrazione di UN prodotto in UNA data.
    Sarà denormalizzato a runtime in N NormalizedDose (uno per antigene).
    """
    product_name: str  # match con catalogo, normalizzato
    administration_date: date
    lot_number: str | None = None
    administered_by: str | None = None  # nome medico/struttura
    notes: str | None = None
    record_id: UUID = Field(default_factory=uuid4)


class NormalizedDose(BaseModel):
    """Singola dose di un singolo antigene, derivata da un VaccinationRecord.
    
    Generata a runtime dalla normalizzazione. NON salvata nel DB.
    """
    antigen: str  # es. "D", "Pa", "PCV13"
    administration_date: date
    source_record_id: UUID  # link al VaccinationRecord originale
    source_product: str  # nome prodotto, per audit
    dose_strength: Literal["full", "reduced"] = "full"  # D vs d, Pa vs pa
```

#### `compliance.py`
```python
class ComplianceLevel(str, Enum):
    BASE = "base"           # raccomandazione di base
    COMPLEMENTARY = "complementary"
    RISK_GROUP = "risk_group"


class AntigenStatus(BaseModel):
    """Stato di un singolo antigene per un paziente."""
    antigen: str
    is_complete: bool
    doses_received: int
    doses_required: int
    schema_followed: str | None = None  # es. "2+1", "3+1", "catchup"
    last_dose_date: date | None = None
    next_dose_due: date | None = None
    notes: list[str] = Field(default_factory=list)
    chapter_ref: str | None = None  # riferimento calendario UFSP


class MissingVaccinePriority(str, Enum):
    URGENT = "urgent"           # già in ritardo significativo
    DUE_NOW = "due_now"         # da fare nei prossimi 3 mesi
    UPCOMING = "upcoming"       # entro 12 mesi
    CATCHUP_AVAILABLE = "catchup_available"
    CATCHUP_CLOSED = "catchup_closed"


class MissingVaccine(BaseModel):
    antigen: str
    priority: MissingVaccinePriority
    reason: str  # spiegazione human-readable
    recommended_schedule: str  # es. "1 dose tra 11-15 anni"
    chapter_ref: str | None = None
    age_window: tuple[int, int] | None = None  # in anni


class FuturePlanItem(BaseModel):
    antigen: str
    target_age_years: int | tuple[int, int]
    target_date_estimate: date | None = None
    plan_type: str  # "richiamo", "vaccinazione_base", "stagionale"
    chapter_ref: str | None = None


class ComplianceReport(BaseModel):
    """Output finale del rule engine. Stesso shape per A e B."""
    person: Person
    evaluation_date: date
    total_records: int
    
    # Status per antigene
    antigen_statuses: dict[str, AntigenStatus]
    
    # Tre output principali
    overall_compliance: bool  # tutto in regola?
    missing_vaccines: list[MissingVaccine]
    future_plan: list[FuturePlanItem]
    
    # Metadata
    engine_used: Literal["deterministic", "llm"]
    engine_version: str
    warnings: list[str] = Field(default_factory=list)  # edge cases, ambiguità
    
    # Disclaimer obbligatorio
    disclaimer: str = (
        "VaxCheck è un ausilio alla consulenza farmacistica e non sostituisce "
        "il parere del medico curante. Le decisioni cliniche restano di "
        "competenza del medico."
    )
```

#### `knowledge.py`
```python
class VaccineProduct(BaseModel):
    """Singolo prodotto dal catalogo."""
    name: str
    aliases: list[str] = Field(default_factory=list)
    manufacturer: str | None = None
    antigens: list[str]
    age_range: dict[str, Any] | None = None
    notes: str | None = None


class AntigenRule(BaseModel):
    """Regole per un antigene dallo schedule 2026."""
    antigen_code: str
    full_name: str
    recommendation_level: ComplianceLevel
    chapter_ref: str | None = None
    primary_schedule: dict[str, Any]
    boosters: list[dict[str, Any]] = Field(default_factory=list)
    catchup_rules: dict[str, Any] | None = None
    contraindications: list[str] = Field(default_factory=list)
    raw: dict[str, Any]  # per accesso completo se serve


class KnowledgeBase(BaseModel):
    """Knowledge base completa caricata."""
    version: str
    products: list[VaccineProduct]
    products_by_name: dict[str, VaccineProduct]  # case-insensitive lookup
    antigens: dict[str, AntigenRule]
    age_milestones: list[dict[str, Any]]
    risk_groups: dict[str, Any]
    raw_catalog: dict[str, Any]
    raw_schedule: dict[str, Any]
    raw_risk_groups: dict[str, Any]
    
    def find_product(self, name: str) -> VaccineProduct | None:
        """Lookup case-insensitive con fallback su alias."""
        ...
    
    def get_antigen_rule(self, antigen: str) -> AntigenRule | None:
        ...
```

### 1.2 KB loader

In `src/vaxcheck/kb/loader.py`, implementa `load_knowledge_base(kb_dir: Path) -> KnowledgeBase`
che:
- Legge i 3 file YAML
- Valida la struttura
- Costruisce indici case-insensitive per i prodotti
- Ritorna un `KnowledgeBase` Pydantic immutabile

### 1.3 Test fase 1

In `tests/unit/test_models.py`:
- Test creazione `Person` con calcolo età
- Test serializzazione/deserializzazione di tutti i modelli
- Test `Person.age_years` su date di confine (compleanno oggi, ieri, domani)

In `tests/conftest.py`, definisci la fixture `clara`:
```python
@pytest.fixture
def clara() -> Person:
    return Person(
        given_name="Clara",
        family_name="Siano",
        birth_date=date(2018, 1, 15),
        sex=Sex.FEMALE,
        clinical_conditions=[],
    )

@pytest.fixture
def clara_records() -> list[VaccinationRecord]:
    return [
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
```

Salva anche `tests/fixtures/clara_booklet.json` con la stessa info per uso da CLI/script.

### 1.4 Normalizer

In `src/vaxcheck/normalization/normalizer.py`:

```python
def normalize_records(
    records: list[VaccinationRecord],
    kb: KnowledgeBase,
) -> list[NormalizedDose]:
    """Espande ogni VaccinationRecord in N NormalizedDose, una per antigene.
    
    Esempio: Infanrix hexa -> 6 NormalizedDose (D, T, Pa, IPV, Hib, HBV).
    
    Se un prodotto non è nel catalogo, registra un warning ma non interrompe.
    """
```

Test in `tests/unit/test_normalizer.py`:
- 1 record `Infanrix hexa` → 6 doses con stessa data
- 14 records di Clara → 51 doses totali (verifica conta esatta)
- Prodotto sconosciuto → warning, non eccezione

---

## FASE 2 — Rule engine deterministico

### 2.1 Protocol e tipi base

In `src/vaxcheck/rule_engine/base.py`:

```python
class RuleEngine(Protocol):
    """Interfaccia comune ai due engine (deterministico e LLM)."""
    
    @property
    def name(self) -> str: ...
    
    @property
    def version(self) -> str: ...
    
    def evaluate(
        self,
        person: Person,
        records: list[VaccinationRecord],
        kb: KnowledgeBase,
        evaluation_date: date | None = None,
    ) -> ComplianceReport: ...
```

### 2.2 Checker base

In `src/vaxcheck/rule_engine/deterministic/checkers/base.py`:

```python
class AntigenChecker(ABC):
    """Base per i checker di un singolo antigene."""
    
    antigen_code: ClassVar[str]
    
    @abstractmethod
    def check(
        self,
        person: Person,
        doses: list[NormalizedDose],  # già filtrate per antigene
        rule: AntigenRule,
        evaluation_date: date,
    ) -> AntigenStatus: ...
    
    @abstractmethod
    def find_missing(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[MissingVaccine]: ...
    
    @abstractmethod
    def plan_future(
        self,
        person: Person,
        status: AntigenStatus,
        rule: AntigenRule,
        evaluation_date: date,
    ) -> list[FuturePlanItem]: ...
```

### 2.3 Checker concreti

Implementa **almeno** questi checker (uno per antigene/gruppo):

- `DTPChecker` (Difterite-Tetano-Pertosse) — gestisce schemi 2+1 e 3+1, richiami pediatrici e adulti
- `IPVChecker` (Polio)
- `HibChecker` (Haemophilus influenzae b) — finestra catchup chiusa a 5 anni
- `HBVChecker` (Epatite B)
- `PCVPediatricChecker` (Pneumococco bambini)
- `MORChecker` (Morbillo-Orecchioni-Rosolia)
- `VaricellaChecker`
- `MenACWYChecker`
- `MenBChecker`
- `HPVChecker`
- `FSMEChecker`

**Linee guida implementative:**

1. Ogni checker conta le dosi del proprio antigene per il paziente
2. Determina lo schema applicabile in base all'anno di nascita (2+1 vs 3+1)
3. Confronta dosi ricevute vs attese → `is_complete`
4. Identifica eventuali mancanti con priorità appropriata
5. Genera plan futuro basato su `age_milestones` della KB
6. Riferimento al `chapter_ref` sempre presente nei status/missing

**Casi edge da gestire esplicitamente:**

- Schema misto storico (es. paziente nato 2018 con schema 3+1)
- Catchup window scaduta (es. MenB > 5 anni → priority=CATCHUP_CLOSED)
- Dose extra non penalizzata (paziente sovra-vaccinato)
- Vaccinazione fatta troppo presto rispetto a min_age_first_dose

### 2.4 Catchup logic

In `src/vaxcheck/rule_engine/deterministic/catchup.py`:

```python
def calculate_catchup_doses(
    antigen: str,
    person: Person,
    doses_received: int,
    rule: AntigenRule,
    evaluation_date: date,
) -> int:
    """Ritorna numero di dosi mancanti per catchup, basato su tabelle UFSP."""
```

### 2.5 Future plan

In `src/vaxcheck/rule_engine/deterministic/future_plan.py`:

```python
def generate_future_plan(
    person: Person,
    antigen_statuses: dict[str, AntigenStatus],
    kb: KnowledgeBase,
    evaluation_date: date,
    horizon_years: int = 80,
) -> list[FuturePlanItem]:
    """Genera calendario futuro fino ai 65+ anni basato su age_milestones."""
```

### 2.6 Engine principale

In `src/vaxcheck/rule_engine/deterministic/engine.py`:

```python
class DeterministicRuleEngine:
    """Engine A: regole codificate in Python, 100% riproducibile."""
    
    name = "deterministic"
    version = "0.1.0"
    
    def __init__(self) -> None:
        self.checkers: dict[str, AntigenChecker] = {
            "DTP": DTPChecker(),
            "IPV": IPVChecker(),
            # ... tutti gli altri
        }
    
    def evaluate(
        self,
        person: Person,
        records: list[VaccinationRecord],
        kb: KnowledgeBase,
        evaluation_date: date | None = None,
    ) -> ComplianceReport:
        eval_date = evaluation_date or date.today()
        
        # 1. Normalizza
        doses = normalize_records(records, kb)
        
        # 2. Raggruppa per antigene
        doses_by_antigen = group_by_antigen(doses)
        
        # 3. Checker per ogni antigene
        statuses = {}
        missing = []
        for antigen_code, checker in self.checkers.items():
            rule = kb.get_antigen_rule(antigen_code)
            if not rule:
                continue
            relevant_doses = doses_by_antigen.get(antigen_code, [])
            status = checker.check(person, relevant_doses, rule, eval_date)
            statuses[antigen_code] = status
            missing.extend(checker.find_missing(person, status, rule, eval_date))
        
        # 4. Future plan
        future = generate_future_plan(person, statuses, kb, eval_date)
        
        # 5. Compliance complessiva
        overall = all(
            s.is_complete for s in statuses.values()
            if kb.get_antigen_rule(s.antigen).recommendation_level == ComplianceLevel.BASE
        )
        
        return ComplianceReport(
            person=person,
            evaluation_date=eval_date,
            total_records=len(records),
            antigen_statuses=statuses,
            overall_compliance=overall,
            missing_vaccines=missing,
            future_plan=future,
            engine_used="deterministic",
            engine_version=self.version,
        )
```

### 2.7 Test fase 2

In `tests/unit/test_deterministic_engine.py`:

**Test obbligatori per il caso Clara:**
1. `test_clara_dtp_complete()` — DTPa-IPV-Hib-HBV completi
2. `test_clara_mor_complete()` — MOR 2 dosi
3. `test_clara_varicella_complete()` — Varicella 2 dosi (da Priorix-Tetra)
4. `test_clara_pcv_complete()` — PCV13 3 dosi
5. `test_clara_menacwy_partial_catchup_open()` — 1 dose, catchup aperto a 11-15
6. `test_clara_menb_missing_catchup_closed()` — 0 dosi, finestra chiusa
7. `test_clara_fsme_complete()` — 3 dosi
8. `test_clara_overall_compliance()` — tutto base completo
9. `test_clara_future_plan_includes_hpv()` — HPV nel piano (11-14 anni)
10. `test_clara_future_plan_includes_adolescent_boosters()` — DTPa+MenACWY+MenB

**Test edge cases:**
- Paziente con 0 vaccini
- Paziente molto anziano (75 anni)
- Schema 2+1 vs 3+1 in base ad anno di nascita
- Dose somministrata prima dell'età minima

---

## FASE 3 — Rule engine LLM

### 3.1 Provider abstraction

In `src/vaxcheck/rule_engine/llm/providers/base.py`:

```python
class LLMProvider(Protocol):
    """Astrazione per provider LLM intercambiabili."""
    
    def complete(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str: ...
```

### 3.2 Provider Claude

In `src/vaxcheck/rule_engine/llm/providers/claude.py`:

```python
class ClaudeProvider:
    """Provider Anthropic Claude API. Solo per dev/test, NON in produzione farmacia."""
    
    def __init__(self, model: str = "claude-sonnet-4-5", api_key: str | None = None):
        self.client = Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self.model = model
    
    def complete(self, prompt, system=None, max_tokens=4096, temperature=0.0):
        ...
```

### 3.3 Provider Ollama

In `src/vaxcheck/rule_engine/llm/providers/ollama.py`:

```python
class OllamaProvider:
    """Provider Ollama locale. Default per produzione on-premise."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:14b"):
        self.base_url = base_url
        self.model = model
    
    def complete(self, prompt, system=None, max_tokens=4096, temperature=0.0):
        # POST a /api/chat con httpx
        ...
```

### 3.4 Prompts

In `src/vaxcheck/rule_engine/llm/prompts.py`, definisci il prompt template che:

1. Spiega il ruolo (esperto vaccinazioni svizzere)
2. Include la knowledge base completa nel context (catalogo + schedule + risk_groups)
3. Mostra i dati del paziente e i record
4. Chiede output JSON strict che matcha lo schema `ComplianceReport`
5. Include esempi few-shot per i casi tricky

```python
SYSTEM_PROMPT = """Sei un esperto del calendario vaccinale svizzero UFSP 2026.
Analizzi la conformità di un paziente in base ai vaccini ricevuti e alla knowledge base.

Regole inderogabili:
- Rispondi SOLO con JSON valido che matcha lo schema fornito
- Usa i chapter_ref dalla knowledge base per giustificare ogni decisione
- Se sei incerto, marca la valutazione in `warnings` invece di tirare a indovinare
- Rispetta gli schemi storici: chi è nato prima del 2019 può aver fatto schema 3+1
- Non inventare antigeni non presenti nella KB
"""

def build_evaluation_prompt(
    person: Person,
    records: list[VaccinationRecord],
    kb: KnowledgeBase,
    evaluation_date: date,
) -> str: ...
```

### 3.5 Engine LLM

In `src/vaxcheck/rule_engine/llm/engine.py`:

```python
class LLMRuleEngine:
    """Engine B: usa LLM con KB nel context."""
    
    name = "llm"
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.version = f"0.1.0-{provider.__class__.__name__}"
    
    def evaluate(self, person, records, kb, evaluation_date=None):
        eval_date = evaluation_date or date.today()
        prompt = build_evaluation_prompt(person, records, kb, eval_date)
        response = self.provider.complete(prompt, system=SYSTEM_PROMPT, temperature=0.0)
        
        # Parse JSON robusto
        report_json = extract_json(response)
        
        # Costruisci ComplianceReport con engine_used="llm"
        return ComplianceReport(
            ...,
            engine_used="llm",
            engine_version=self.version,
        )
```

### 3.6 Test fase 3

In `tests/unit/test_llm_engine.py`:

- Test con **mock provider** che ritorna risposta predefinita (no chiamate reali)
- Test parsing JSON robusto (provider che torna markdown, prefissi, ecc.)
- Test che l'output è un `ComplianceReport` valido
- Skip test reali se `ANTHROPIC_API_KEY` non disponibile

---

## FASE 4 — Test parity

### 4.1 Test parity

In `tests/parity/test_engines_parity.py`:

```python
@pytest.mark.parametrize("test_case", load_test_cases())
def test_engines_agree(test_case, kb):
    """Engine A e B devono concordare su dimensioni critiche."""
    person = test_case.person
    records = test_case.records
    
    det_engine = DeterministicRuleEngine()
    llm_engine = LLMRuleEngine(provider=MockProvider(test_case.expected_llm_response))
    
    report_a = det_engine.evaluate(person, records, kb)
    report_b = llm_engine.evaluate(person, records, kb)
    
    # Conformità sì/no per ogni antigene base
    for antigen in get_base_antigens(kb):
        assert report_a.antigen_statuses[antigen].is_complete == \
               report_b.antigen_statuses[antigen].is_complete, \
               f"Disagreement on {antigen} completion"
    
    # Lista mancanti (set di antigeni)
    missing_a = {m.antigen for m in report_a.missing_vaccines}
    missing_b = {m.antigen for m in report_b.missing_vaccines}
    assert missing_a == missing_b, f"Disagreement on missing: {missing_a ^ missing_b}"
```

### 4.2 Test cases per parity

Crea almeno 5 test cases in `tests/fixtures/`:
1. Clara (8 anni, libretto reale)
2. Neonato 4 mesi (solo prime 2 dosi)
3. Adulto 35 anni completamente vaccinato
4. Anziano 70 anni con condizioni a rischio
5. Persona mai vaccinata, 25 anni (caso recovery massivo)

---

## DELIVERABLE FINALE

Quando hai finito tutte le fasi:

1. **Report di completamento** in `IMPLEMENTATION_REPORT.md`:
   - Cosa è stato implementato
   - Test passati / falliti / skipped
   - Decisioni di design prese in autonomia (con motivazione)
   - Edge cases noti non ancora coperti
   - Prossimi step suggeriti per Fasi 5-7

2. **Coverage**: `pytest --cov=vaxcheck` → idealmente >80% sul package `vaxcheck`

3. **Lint**: `ruff check src/ tests/` → zero errori

4. **Type check**: `mypy --strict src/vaxcheck` → zero errori

5. **CLI demo**: uno script `scripts/demo_clara.py` che:
   - Carica la KB
   - Costruisce Clara
   - Esegue entrambi gli engine
   - Stampa i 3 report (conformità, mancanti, futuro) in italiano leggibile
   - Mostra eventuali divergenze tra A e B

## Stile di lavoro

- Lavora **in modo agentico**: leggi i file YAML della KB, sviluppa, testa, itera
- **Non chiedere conferme** durante l'implementazione: prendi decisioni motivate e
  documentale nel report finale
- Se incontri ambiguità nella KB, marca con `# TODO clinical review` e prosegui
- Commit logici: 1 fase = 1 commit (o gruppo di commit logici)
- README finale con istruzioni `setup`, `test`, `demo` chiare

## Ricorda sempre

- **On-premise prima di tutto**: niente dipendenze cloud nel deterministico
- **Modelli puri**: `vaxcheck.domain` non importa nulla di framework
- **Disclaimer obbligatorio** in ogni `ComplianceReport`
- **Test passano sempre prima di avanzare di fase**
- **Ground truth = libretto di Clara**: ogni decisione si valida contro Clara

Buon lavoro. Quando finisci, presenta il report di completamento e attendi feedback
prima di proseguire con le fasi 5-7 (UI Streamlit + persistenza PostgreSQL).
