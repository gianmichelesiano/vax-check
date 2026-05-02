from __future__ import annotations

import os
from typing import Any

import httpx


class DeepSeekProvider:
    """DeepSeek API provider via OpenAI-compatible /chat/completions endpoint.

    Reads credentials from environment:
    - DEEPSEEK_API_KEY or ANTHROPIC_AUTH_TOKEN for auth
    - DEEPSEEK_MODEL or ANTHROPIC_MODEL for model name
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str = "https://api.deepseek.com",
    ):
        key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        if not key:
            raise ValueError("Set DEEPSEEK_API_KEY, ANTHROPIC_AUTH_TOKEN, or pass api_key parameter")
        self.api_key = key
        self.base_url = base_url.rstrip("/")
        self.model = model or os.environ.get("DEEPSEEK_MODEL") or os.environ.get("ANTHROPIC_MODEL", "deepseek-v4-pro")

    def complete(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
            "thinking": {"type": "disabled"},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        with httpx.Client(timeout=180) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()

        choices = data.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            content = msg.get("content", "")
            if content:
                return content
            # DeepSeek with thinking may return reasoning_content
            reasoning = msg.get("reasoning_content", "")
            if reasoning:
                return reasoning
        return ""
