from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    """Abstraction for interchangeable LLM providers."""

    def complete(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str: ...
