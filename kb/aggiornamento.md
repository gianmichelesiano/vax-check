# Come aggiornare il calendario vaccinale

> Da eseguire ogni anno a febbraio quando l'UFSP pubblica il nuovo calendario.
> Tempo stimato: 2-3 ore se nessuna regola strutturale cambia, mezza giornata se ci sono novità importanti.

---

## 0. Prepara il materiale

1. Scarica il nuovo PDF dal sito UFSP:
   `https://www.bag.admin.ch/calendariovaccinale`
2. Apri VS Code nella root del progetto VaxCheck
3. Tieni aperto il PDF e il vecchio calendario a confronto

---

## 1. Aggiorna `vaccines_catalog.yaml`

Controlla se ci sono **nuovi prodotti omologati** o **prodotti ritirati**:

- Nuovo prodotto → aggiungi una voce nella lista `products` con nome, antigeni, fascia età
- Prodotto ritirato → non eliminarlo, spostalo in `deprecated_products` con il motivo

Aggiorna il metadata in cima al file:
```yaml
metadata:
  version: "2027.1"           # ← aggiorna anno
  publication_date: "2027-02-01"
```

---

## 2. Rinomina e aggiorna lo schedule

Rinomina il file:
```bash
mv kb/vaccination_schedule_2026.yaml kb/vaccination_schedule_2027.yaml
```

Apri il file e aggiorna:
- `metadata.version` → `"2027.1"`
- `metadata.publication_date` → data pubblicazione nuovo calendario
- Qualsiasi regola cambiata (intervalli, dosi, finestre catchup)

Le sezioni che cambiano più spesso:
- `COVID` — formulazione aggiornata ogni anno
- `Influenza` — prodotti stagionali
- `RSV` — normativa ancora in evoluzione

Le sezioni che cambiano raramente:
- `DTP`, `IPV`, `Hib`, `HBV` — stabili da anni
- `MOR`, `V` — stabili
- `FSME` — stabili

---

## 3. Aggiorna `risk_groups.yaml` (se necessario)

Cambia raramente. Controlla solo se il PDF menziona nuove condizioni cliniche
o nuove raccomandazioni per gruppi a rischio specifici.

Se non cambia nulla, aggiorna solo il metadata:
```yaml
metadata:
  version: "2027.1"
```

---

## 4. Aggiorna il rule engine (solo se necessario)

Se una **regola strutturale** è cambiata (es. schema da 2+1 a 3+1, nuova finestra
catchup, nuovo antigene), devi anche aggiornare il checker Python corrispondente in:

```
src/vaxcheck/rule_engine/deterministic/checkers/
```

Ogni file corrisponde a un antigene (`dtp.py`, `mor.py`, ecc.).
Se hai dubbi su cosa cambiare, leggi il capitolo corrispondente nel PDF
e confrontalo con il codice del checker.

---

## 5. Testa che tutto funzioni

Esegui i test di regressione:
```bash
pytest tests/ -v
```

I test su Clara Siano devono passare tutti — lei non diventa improvvisamente
non conforme per un cambio di calendario. Se qualcosa rompe, c'è un errore
nell'aggiornamento.

Controlla in particolare:
```bash
pytest tests/ -k "clara" -v
```

---

## 6. Scrivi il CHANGELOG

Apri (o crea) `kb/CHANGELOG.md` e aggiungi in cima:

```markdown
## 2027.1 — febbraio 2027

### Nuovi prodotti
- NomeProdotto (produttore) — antigeni coperti

### Prodotti ritirati
- NomeProdotto — motivo

### Regole aggiornate
- COVID: formulazione aggiornata a XYZ
- (elenco modifiche)

### Nessuna modifica
- DTP, IPV, Hib, HBV, MOR, V, HPV, FSME — invariati
```

Questo permette a Maria Lucia di capire cosa è cambiato senza leggere il PDF.

---

## 7. Commit e deploy

```bash
git add kb/
git commit -m "feat: calendario vaccinale 2027.1 (UFSP febbraio 2027)"
docker compose up --build
```

Verifica che l'app si avvii correttamente e che la versione KB mostrata
nelle Impostazioni sia aggiornata a `2027.1`.

---

## Reminder

Metti un promemoria nel calendario personale per **fine gennaio** di ogni anno
con il testo: *"Controllare nuovo calendario vaccinale UFSP — aggiornare VaxCheck"*.

Il PDF di solito esce nella prima settimana di febbraio.

---

## In futuro (auto-update C2)

Quando implementerai l'aggiornamento automatico (pianificato ma non ancora fatto),
questo processo manuale verrà sostituito da:

1. Tu aggiorni i YAML nel repo pubblico
2. VaxCheck in farmacia si aggiorna da solo al prossimo avvio
3. Maria Lucia vede una notifica "Calendario aggiornato a 2027.1"

Fino ad allora, questa procedura manuale è sufficiente.