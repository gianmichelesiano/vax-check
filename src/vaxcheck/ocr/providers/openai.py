import base64
import json
import os
from io import BytesIO

from PIL.Image import Image as PILImage

from vaxcheck.ocr.providers.claude import SYSTEM_PROMPT, USER_PROMPT


class OpenAIProvider:
    """OpenAI GPT-4o vision provider."""

    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self._client = None

    @property
    def name(self) -> str:
        return f"openai/{self.model}"

    @property
    def available(self) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY"))

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as e:
                raise RuntimeError(
                    "openai package non installato. Esegui: pip install openai"
                ) from e
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY non configurata. "
                    "Aggiungi OPENAI_API_KEY=sk-... al file .env per abilitare OCR OpenAI."
                )
            self._client = OpenAI(api_key=api_key)
        return self._client

    def extract(self, image: PILImage) -> dict:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        image_data = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}",
                                "detail": "high",
                            },
                        },
                        {"type": "text", "text": USER_PROMPT},
                    ],
                },
            ],
        )

        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
