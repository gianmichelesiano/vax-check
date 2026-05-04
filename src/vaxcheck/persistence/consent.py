from __future__ import annotations

from sqlalchemy.orm import Session

from vaxcheck.persistence.models import OCRConsentDB


class ConsentRepository:
    def __init__(self, session: Session):
        self.session = session

    def has_consent(self, patient_id: str) -> bool:
        return (
            self.session.query(OCRConsentDB)
            .filter_by(patient_id=patient_id, revoked=False)
            .first()
            is not None
        )

    def record_consent(self, patient_id: str) -> OCRConsentDB:
        consent = OCRConsentDB(patient_id=patient_id)
        self.session.add(consent)
        self.session.commit()
        return consent

    def revoke_consent(self, patient_id: str) -> None:
        self.session.query(OCRConsentDB).filter_by(patient_id=patient_id).update(
            {"revoked": True}
        )
        self.session.commit()
