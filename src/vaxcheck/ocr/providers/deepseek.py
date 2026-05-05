import base64
import json
import os
from io import BytesIO

import anthropic
from PIL.Image import Image as PILImage

from vaxcheck.ocr.providers.claude import SYSTEM_PROMPT, USER_PROMPT


class DeepSeekProvider:
    """DeepSeek vision via Anthropic-compatible API (api.deepseek.com/anthropic)."""

    def __init__(self, model: str = "deepseek-v4-pro"):
        self.model = model
        self._client: anthropic.Anthropic | None = None

    @property
    def name(self) -> str:
        return f"deepseek/{self.model}"

    @property
    def available(self) -> bool:
        return bool(os.environ.get("DEEPSEEK_API_KEY"))

    def _get_client(self) -> anthropic.Anthropic:
        if self._client is None:
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "DEEPSEEK_API_KEY non configurata. "
                    "Aggiungi DEEPSEEK_API_KEY=sk-... al file .env per abilitare OCR DeepSeek."
                )
            self._client = anthropic.Anthropic(
                api_key=api_key,
                base_url="https://api.deepseek.com/anthropic",
            )
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

        text_block = next(b for b in response.content if b.type == "text")
        text = text_block.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
