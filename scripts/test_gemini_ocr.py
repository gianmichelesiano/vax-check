#!/usr/bin/env python3
"""Standalone test: Gemini vision OCR on Swiss vaccination booklet."""

import json
import os
import sys
from pathlib import Path

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyA1b7FC_a6S4euZJX2XPfl1F0p4dsqh2ew")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-lite")

IMAGE_PATH = Path(__file__).parent.parent / "clara_vaccini.jpg"

PROMPT = """Estrai tutte le vaccinazioni visibili in questa immagine del libretto vaccinale svizzero.

Per ogni vaccinazione nella tabella estrai:
- product_name: nome esatto del vaccino come scritto (es. "Infanrix hexa", "Priorix-Tetra")
- administration_date: data in formato ISO YYYY-MM-DD. Se non leggibile con certezza, usa null.
- lot_number: numero di lotto se chiaramente visibile, altrimenti null
- confidence: 0.0-1.0 indicante la certezza sulla correttezza dell'estrazione

Formato risposta — SOLO JSON valido, niente testo o markdown:
{
  "vaccinations": [
    {
      "product_name": "Infanrix hexa",
      "administration_date": "2018-03-21",
      "lot_number": "A42CB",
      "confidence": 0.95
    }
  ],
  "warnings": ["testo se ci sono ambiguita generali"]
}

Note:
- Date svizzere spesso DD.MM.YYYY — converti in ISO YYYY-MM-DD
- Il libretto ha colonne con X/checkmarks per antigeni — ignorale
- Estrai solo quello che vedi chiaramente, niente inferenze"""


def run():
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("ERRORE: pip install google-genai")
        sys.exit(1)

    if not IMAGE_PATH.exists():
        print(f"ERRORE: immagine non trovata: {IMAGE_PATH}")
        sys.exit(1)

    print(f"Provider : {MODEL}")
    print(f"Immagine : {IMAGE_PATH}")
    print(f"Dimensione: {IMAGE_PATH.stat().st_size / 1024:.1f} KB")
    print("-" * 60)

    client = genai.Client(api_key=GEMINI_API_KEY)

    image_data = IMAGE_PATH.read_bytes()
    image_part = types.Part.from_bytes(data=image_data, mime_type="image/jpeg")

    import time
    t0 = time.monotonic()
    response = client.models.generate_content(
        model=MODEL,
        contents=[image_part, PROMPT],
    )
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERRORE parsing JSON: {e}")
        print("Raw response:")
        print(response.text)
        sys.exit(1)

    print(f"Tempo risposta: {elapsed_ms}ms")
    print(f"Vaccinazioni trovate: {len(result.get('vaccinations', []))}")
    print()

    for i, v in enumerate(result.get("vaccinations", []), 1):
        conf = v.get("confidence", 0)
        flag = "⚠️ " if conf < 0.8 else "✓ "
        print(f"{flag} [{i}] {v.get('product_name')}")
        print(f"       Data : {v.get('administration_date')}")
        print(f"       Lotto: {v.get('lot_number')}")
        print(f"       Conf : {conf:.0%}")

    if result.get("warnings"):
        print()
        print("Warnings:")
        for w in result["warnings"]:
            print(f"  ! {w}")

    print()
    print("=== RAW JSON ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
