from typing import Protocol, runtime_checkable

from PIL.Image import Image as PILImage


@runtime_checkable
class OCRProvider(Protocol):
    def extract(self, image: PILImage) -> dict:
        """Send image to vision model, return raw JSON dict."""
        ...

    @property
    def name(self) -> str: ...

    @property
    def available(self) -> bool:
        """True if provider is configured and reachable."""
        ...
