from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from vaxcheck.api.deps import get_db, get_engine, get_kb
from vaxcheck.api.schemas import CreateRecordRequest
from vaxcheck.domain.knowledge import KnowledgeBase
from vaxcheck.domain.person import Person
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.ocr.extractor import BookletExtractor
from vaxcheck.ocr.models import ExtractionResult
from vaxcheck.ocr.providers.factory import get_ocr_provider
from vaxcheck.persistence.consent import ConsentRepository
from vaxcheck.persistence.mappers import person_to_domain, record_to_domain
from vaxcheck.persistence.repository import PatientRepository, RecordRepository, ReportRepository
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine

router = APIRouter(tags=["ocr"])


class ConfirmExtractionsRequest(BaseModel):
    patient_id: str
    confirmed_records: list[CreateRecordRequest]


@router.post("/api/ocr/extract", response_model=ExtractionResult)
async def extract_from_image(
    image: UploadFile = File(...),
    patient_id: str | None = None,
    db: Session = Depends(get_db),
    kb: KnowledgeBase = Depends(get_kb),
):
    """Estrae vaccinazioni da foto libretto.

    L'immagine viene anonimizzata prima dell'invio a Claude API.
    Richiede consenso paziente se patient_id fornito.
    """
    if patient_id:
        consent_repo = ConsentRepository(db)
        if not consent_repo.has_consent(patient_id):
            raise HTTPException(
                status_code=403,
                detail="Consenso OCR non registrato per questo paziente. "
                "Richiedi consenso prima di procedere.",
            )

    content = await image.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(400, "Immagine troppo grande (max 10MB)")

    provider = get_ocr_provider()
    if not provider.available:
        raise HTTPException(
            503,
            "OCR non disponibile: nessun provider configurato. "
            "Aggiungi ANTHROPIC_API_KEY, DEEPSEEK_API_KEY, o OPENAI_API_KEY al .env.",
        )

    extractor = BookletExtractor(provider=provider, kb=kb)

    try:
        result = extractor.extract_from_bytes(content)
    except Exception as e:
        raise HTTPException(500, f"Errore estrazione: {str(e)}")

    return result


@router.post("/api/ocr/consent/{patient_id}")
async def record_ocr_consent(
    patient_id: str,
    db: Session = Depends(get_db),
):
    """Registra consenso del paziente all'uso OCR (cloud)."""
    consent_repo = ConsentRepository(db)
    if consent_repo.has_consent(patient_id):
        return {"status": "already_consented"}
    consent_repo.record_consent(patient_id)
    return {"status": "consented"}


@router.post("/api/ocr/confirm")
async def confirm_extractions(
    body: ConfirmExtractionsRequest,
    db: Session = Depends(get_db),
    kb: KnowledgeBase = Depends(get_kb),
    engine: DeterministicRuleEngine = Depends(get_engine),
):
    """Salva i record confermati dall'utente e lancia analisi."""
    patient_repo = PatientRepository(db)
    db_patient = patient_repo.get(body.patient_id)
    if db_patient is None:
        raise HTTPException(404, "Paziente non trovato")

    record_repo = RecordRepository(db)
    saved_records = []
    for rec in body.confirmed_records:
        record = VaccinationRecord(
            product_name=rec.product_name,
            administration_date=rec.administration_date,
            lot_number=rec.lot_number,
        )
        saved = record_repo.add(record, body.patient_id)
        saved_records.append(saved)

    patient = person_to_domain(db_patient)
    all_records = [record_to_domain(r) for r in record_repo.list_for_patient(body.patient_id)]
    report = engine.evaluate(patient, all_records, kb)
    db_report = ReportRepository(db).save(report, body.patient_id)
    db.commit()

    return {
        "added": len(body.confirmed_records),
        "report_id": db_report.id,
        "overall_compliance": report.overall_compliance,
    }
