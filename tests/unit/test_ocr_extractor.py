from datetime import date
from io import BytesIO

from PIL import Image

from vaxcheck.ocr.extractor import BookletExtractor


class MockClaudeProvider:
    name = "mock"
    available = True

    def extract(self, image):
        return {
            "vaccinations": [
                {
                    "product_name": "Infanrix hexa",
                    "administration_date": "2018-03-21",
                    "lot_number": "A42CB",
                    "confidence": 0.95,
                },
                {
                    "product_name": "Prevenar 13",
                    "administration_date": "2018-03-21",
                    "lot_number": None,
                    "confidence": 0.90,
                },
            ],
            "warnings": [],
        }


def create_dummy_image_bytes():
    img = Image.new("RGB", (800, 1200), color=(255, 255, 255))
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_extract_basic(kb):
    extractor = BookletExtractor(provider=MockClaudeProvider(), kb=kb)
    result = extractor.extract_from_bytes(create_dummy_image_bytes())

    assert result.total_found == 2
    assert result.low_confidence_count == 0
    e0 = result.extractions[0]
    assert e0.product_name_normalized == "Infanrix hexa"
    assert e0.administration_date == date(2018, 3, 21)
    assert e0.lot_number == "A42CB"
    assert e0.needs_review is False


def test_unrecognized_product(kb):
    class MockNoMatchProvider:
        name = "mock"
        available = True
        def extract(self, image):
            return {
                "vaccinations": [
                    {"product_name": "UnknownVax 3000", "administration_date": "2020-01-01", "confidence": 0.9},
                ],
                "warnings": [],
            }

    extractor = BookletExtractor(provider=MockNoMatchProvider(), kb=kb)
    result = extractor.extract_from_bytes(create_dummy_image_bytes())

    assert result.total_found == 1
    assert result.unrecognized_products == ["UnknownVax 3000"]
    assert result.extractions[0].needs_review is True
