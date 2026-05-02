from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic


class ClaudeProvider:
    """Anthropic-compatible API provider (Claude, DeepSeek, etc.).

    Supports both standard Anthropic API and DeepSeek-compatible endpoints.
    Reads credentials from environment:
    - ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN for auth
    - ANTHROPIC_BASE_URL for custom endpoint (default: api.anthropic.com)
    - ANTHROPIC_MODEL for model name
    """

    def __init__(self, model: str | None = None, api_key: str | None = None, base_url: str | None = None):
        key = api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        if not key:
            raise ValueError(
                "Set ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN, or pass api_key parameter"
            )
        url = base_url or os.environ.get("ANTHROPIC_BASE_URL")
        if url:
            self.client = Anthropic(api_key=key, base_url=url)
        else:
            self.client = Anthropic(api_key=key)
        self.model = model or os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

    def complete(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        for block in response.content:
            if block.type == "text":
                return block.text
        return ""
