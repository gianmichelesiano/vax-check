class OllamaProvider:
    """
    STUB — Not implemented in MVP.

    Implement when analysis volume justifies dedicated GPU hardware.
    Recommended model: Qwen2.5-VL:7b (requires 8GB VRAM).

    Same OCRProvider interface — swap without modifying rest of code.
    """

    @property
    def name(self) -> str:
        return "ollama/not-implemented"

    @property
    def available(self) -> bool:
        return False

    def extract(self, image) -> dict:
        raise NotImplementedError(
            "OllamaProvider non ancora implementato. "
            "Usa ClaudeProvider o inserimento manuale."
        )
