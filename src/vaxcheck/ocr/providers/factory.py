import os

from vaxcheck.ocr.providers.base import OCRProvider


def get_ocr_provider() -> OCRProvider:
    """Select OCR provider via OCR_PROVIDER env var.

    Values: claude (default), deepseek, openai
    Falls back to next available if preferred not configured.
    """
    preferred = os.environ.get("OCR_PROVIDER", "claude").lower()

    if preferred == "deepseek":
        from vaxcheck.ocr.providers.deepseek import DeepSeekProvider
        p = DeepSeekProvider()
        if p.available:
            return p

    if preferred == "openai":
        from vaxcheck.ocr.providers.openai import OpenAIProvider
        p = OpenAIProvider()
        if p.available:
            return p

    # default / fallback
    from vaxcheck.ocr.providers.claude import ClaudeProvider
    return ClaudeProvider()
