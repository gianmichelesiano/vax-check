"""SQLAlchemy ORM models for VaxCheck persistence."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PatientDB(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    given_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    family_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)
    clinical_conditions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    occupational_situations: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    vaccination_records: Mapped[list[VaccinationRecordDB]] = relationship(
        back_populates="patient", cascade="all, delete-orphan",
        order_by="VaccinationRecordDB.administration_date",
    )
    compliance_reports: Mapped[list[ComplianceReportDB]] = relationship(
        back_populates="patient", cascade="all, delete-orphan",
        order_by="ComplianceReportDB.evaluation_date",
    )

    def __repr__(self) -> str:
        return f"<PatientDB {self.id} {self.family_name} {self.given_name}>"


class VaccinationRecordDB(Base):
    __tablename__ = "vaccination_records"

    record_id: Mapped[str] = mapped_column(
        String(36), primary_key=True
    )
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    administration_date: Mapped[date] = mapped_column(Date, nullable=False)
    lot_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    administered_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    patient: Mapped[PatientDB] = relationship(back_populates="vaccination_records")

    def __repr__(self) -> str:
        return f"<VaccinationRecordDB {self.record_id} {self.product_name} {self.administration_date}>"


class ComplianceReportDB(Base):
    __tablename__ = "compliance_reports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evaluation_date: Mapped[date] = mapped_column(Date, nullable=False)
    report_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    engine_used: Mapped[str] = mapped_column(String(50), nullable=False)
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False)
    overall_compliance: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    patient: Mapped[PatientDB] = relationship(back_populates="compliance_reports")

    def __repr__(self) -> str:
        return f"<ComplianceReportDB {self.id} {self.evaluation_date} {'PASS' if self.overall_compliance else 'FAIL'}>"
