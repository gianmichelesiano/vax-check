from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from vaxcheck.domain.person import Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.kb.loader import load_knowledge_base


@pytest.fixture(scope="session")
def kb():
    kb_dir = Path(__file__).resolve().parent.parent / "kb"
    return load_knowledge_base(kb_dir)


@pytest.fixture
def clara() -> Person:
    return Person(
        given_name="Clara",
        family_name="Siano",
        birth_date=date(2018, 1, 15),
        sex=Sex.FEMALE,
        clinical_conditions=[],
    )


@pytest.fixture
def clara_records() -> list[VaccinationRecord]:
    return [
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 3, 21)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2018, 3, 21)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 5, 24)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2018, 5, 24)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 7, 12)),
        VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(2018, 11, 5)),
        VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(2019, 2, 4)),
        VaccinationRecord(product_name="Prevenar 13", administration_date=date(2019, 2, 4)),
        VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2019, 10, 15)),
        VaccinationRecord(product_name="Menveo", administration_date=date(2020, 2, 11)),
        VaccinationRecord(product_name="Adacel-Polio", administration_date=date(2024, 4, 23)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 4, 23)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 5, 10)),
        VaccinationRecord(product_name="FSME-Immun Junior", administration_date=date(2024, 11, 11)),
    ]
