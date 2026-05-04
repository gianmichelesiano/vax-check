import time
from datetime import date
from io import BytesIO

from PIL import Image

from vaxcheck.kb.loader import KnowledgeBase
from vaxcheck.ocr.anonymizer import anonymize_booklet_image, verify_anonymization
from vaxcheck.ocr.models import ExtractedVaccination, ExtractionResult
from vaxcheck.ocr.normalizer import normalize_product_name
from vaxcheck.ocr.preprocessor import preprocess_booklet_image
from vaxcheck.ocr.providers.base import OCRProvider

CONFIDENCE_THRESHOLD_REVIEW = 0.8


class BookletExtractor:
    def __init__(self, provider: OCRProvider, kb: KnowledgeBase):
        self.provider = provider
        self.kb = kb

    def extract_from_bytes(self, image_bytes: bytes) -> ExtractionResult:
        start = time.monotonic()

        img = Image.open(BytesIO(image_bytes))
        img = preprocess_booklet_image(img)
        img = anonymize_booklet_image(img)

        assert verify_anonymization(img), "Anonimizzazione fallita — blocco invio"

        raw = self.provider.extract(img)

        extractions: list[ExtractedVaccination] = []
        unrecognized: list[str] = []

        for v in raw.get("vaccinations", []):
            raw_name = v.get("product_name") or ""
            normalized, norm_conf = normalize_product_name(raw_name, self.kb)

            raw_date = v.get("administration_date")
            parsed_date: date | None = None
            if raw_date:
                try:
                    parsed_date = date.fromisoformat(raw_date)
                except ValueError:
                    pass

            ocr_confidence = float(v.get("confidence", 0.5))
            final_confidence = (ocr_confidence + norm_conf) / 2

            needs_review = (
                final_confidence < CONFIDENCE_THRESHOLD_REVIEW
                or normalized is None
                or parsed_date is None
            )

            review_reason = None
            if normalized is None:
                review_reason = f"Prodotto '{raw_name}' non trovato nel catalogo"
                unrecognized.append(raw_name)
            elif parsed_date is None:
                review_reason = "Data non leggibile — inserire manualmente"
            elif final_confidence < CONFIDENCE_THRESHOLD_REVIEW:
                review_reason = f"Bassa confidenza ({final_confidence:.0%}) — verificare"

            extractions.append(
                ExtractedVaccination(
                    product_name_raw=raw_name,
                    product_name_normalized=normalized,
                    administration_date=parsed_date,
                    lot_number=v.get("lot_number"),
                    confidence=final_confidence,
                    needs_review=needs_review,
                    review_reason=review_reason,
                )
            )

        low_conf = sum(1 for e in extractions if e.confidence < CONFIDENCE_THRESHOLD_REVIEW)

        return ExtractionResult(
            extractions=extractions,
            total_found=len(extractions),
            low_confidence_count=low_conf,
            unrecognized_products=list(set(unrecognized)),
            warnings=raw.get("warnings", []),
            processing_time_ms=int((time.monotonic() - start) * 1000),
        )
