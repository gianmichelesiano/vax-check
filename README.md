# VaxCheck — Analisi Conformità Vaccinale Svizzera

Sistema on-premise per farmacie svizzere. Valuta la conformità al calendario vaccinale UFSP 2026 e genera report personalizzati.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Utilizzo

### Demo con libretto di Clara Siano

```bash
source .venv/bin/activate
python scripts/demo_clara.py
```

Stampa report in italiano con stato conformità, vaccinazioni mancanti e calendario futuro.

### API Python

```python
from datetime import date
from vaxcheck.domain.person import Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.kb.loader import load_knowledge_base
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine
from vaxcheck.reports.formatter import format_report_italian

kb = load_knowledge_base("kb")

person = Person(
    given_name="Mario",
    family_name="Rossi",
    birth_date=date(2020, 3, 15),
    sex=Sex.MALE,
)

records = [
    VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2020, 5, 15)),
    VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2020, 7, 15)),
    VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2021, 3, 15)),
]

engine = DeterministicRuleEngine()
report = engine.evaluate(person, records, kb)

print(format_report_italian(report))
```

### Engine LLM (richiede API key Anthropic o Ollama)

```python
from vaxcheck.rule_engine.llm.engine import LLMRuleEngine
from vaxcheck.rule_engine.llm.providers.claude import ClaudeProvider

llm = LLMRuleEngine(ClaudeProvider())  # usa ANTHROPIC_API_KEY da env
report = llm.evaluate(person, records, kb)
```

Con Ollama locale:

```python
from vaxcheck.rule_engine.llm.providers.ollama import OllamaProvider

llm = LLMRuleEngine(OllamaProvider(base_url="http://localhost:11434", model="qwen2.5:14b"))
```

## Test

```bash
pytest tests/ -v
```

## Validazione qualità codice

```bash
ruff check src/ tests/ scripts/     # linting
mypy --strict src/vaxcheck           # type checking
```

## Struttura

```
vaxcheck/
├── kb/                    # Knowledge base UFSP 2026 (read-only)
├── src/vaxcheck/
│   ├── domain/            # Modelli Pydantic puri
│   ├── kb/                # Loader KB
│   ├── normalization/     # Prodotto → antigeni
│   ├── rule_engine/
│   │   ├── deterministic/ # Engine A: regole Python
│   │   └── llm/           # Engine B: LLM con KB nel context
│   └── reports/           # Formattazione report in italiano
├── tests/
│   ├── unit/              # Test unitari
│   ├── parity/            # Test parità engine A vs B
│   └── fixtures/          # Dati test (libretto Clara)
├── scripts/
│   └── demo_clara.py      # Demo interattiva
└── IMPLEMENTATION_REPORT.md
```

## Requisiti

- Python 3.11+
- Dipendenze: pydantic, pyyaml, anthropic (opzionale), httpx (opzionale)

## Disclaimer

VaxCheck è un ausilio alla consulenza farmacistica e non sostituisce il parere del medico curante. Le decisioni cliniche restano di competenza del medico.
