"""Persistence layer for VaxCheck — SQLAlchemy ORM with SQLite."""

from vaxcheck.persistence.mappers import (
    patient_from_domain,
    person_to_domain,
    record_from_domain,
    record_to_domain,
    report_from_domain,
    report_to_domain,
)
from vaxcheck.persistence.models import (
    ComplianceReportDB,
    PatientDB,
    VaccinationRecordDB,
)
from vaxcheck.persistence.repository import (
    PatientRepository,
    RecordRepository,
    ReportRepository,
)
from vaxcheck.persistence.session import get_engine, get_session, init_db

__all__ = [
    # Models
    "PatientDB",
    "VaccinationRecordDB",
    "ComplianceReportDB",
    # Session
    "get_engine",
    "init_db",
    "get_session",
    # Mappers
    "patient_from_domain",
    "person_to_domain",
    "record_from_domain",
    "record_to_domain",
    "report_from_domain",
    "report_to_domain",
    # Repositories
    "PatientRepository",
    "RecordRepository",
    "ReportRepository",
]
