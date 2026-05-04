import base64
import json
import os
from io import BytesIO

import anthropic
from PIL.Image import Image as PILImage

SYSTEM_PROMPT = """Sei un estrattore di dati da libretti vaccinali svizzeri.
Estrai SOLO i dati visibili nella tabella delle vaccinazioni.
Non inventare mai dati. Se un campo non e leggibile chiaramente, usa null.
Rispondi SOLO con JSON valido, senza testo aggiuntivo, senza markdown."""

USER_PROMPT = """Estrai tutte le vaccinazioni visibili in questa immagine del libretto vaccinale svizzero.

Per ogni vaccinazione nella tabella estrai:
- product_name: nome esatto del vaccino come scritto (es. "Infanrix hexa", "Priorix-Tetra")
- administration_date: data in formato ISO YYYY-MM-DD. IMPORTANTE: se la data non e leggibile con certezza, usa null. Non inventare mai date.
- lot_number: numero di lotto se chiaramente visibile, altrimenti null
- confidence: 0.0-1.0 indicante la certezza sulla correttezza dell'estrazione

Formato risposta:
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

Note importanti:
- Il libretto ha colonne per diversi antigeni con X o checkmarks — ignorale completamente
- Le date svizzere sono spesso in formato DD.MM.YYYY — converti in ISO YYYY-MM-DD
- I nomi prodotto possono essere scritti a mano o a stampa
- Estrai solo quello che vedi chiaramente — niente inferenze"""


class ClaudeProvider:
    def __init__(self, model: str = "claude-sonnet-4-5"):
        self.model = model
        self._client: anthropic.Anthropic | None = None

    @property
    def name(self) -> str:
        return f"claude/{self.model}"

    @property
    def available(self) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    def _get_client(self) -> anthropic.Anthropic:
        if self._client is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY non configurata. "
                    "Aggiungi ANTHROPIC_API_KEY=sk-... al file .env per abilitare OCR."
                )
            self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    def extract(self, image: PILImage) -> dict:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        image_data = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": USER_PROMPT},
                    ],
                }
            ],
        )

        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
