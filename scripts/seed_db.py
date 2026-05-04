"""Seed database with demo patients for VaxCheck."""
from datetime import date
from pathlib import Path

from vaxcheck.domain.person import ClinicalCondition, Person, Sex
from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.kb.loader import load_knowledge_base
from vaxcheck.persistence.repository import PatientRepository, RecordRepository, ReportRepository
from vaxcheck.persistence.session import get_engine, init_db, get_session
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine

KB_DIR = Path("kb")

PATIENTS: dict[str, tuple[Person, list[VaccinationRecord]]] = {
    "clara": (
        Person(
            given_name="Clara", family_name="Siano",
            birth_date=date(2018, 1, 15), sex=Sex.FEMALE,
            notes="Libretto reale. MenB mai fatto, MenACWY 1 sola dose.",
        ),
        [
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
        ],
    ),
    "luca": (
        Person(
            given_name="Luca", family_name="Bianchi",
            birth_date=date(2026, 1, 10), sex=Sex.MALE,
            notes="Neonato sano. Genitori chiedono consiglio su prosecuzione calendario.",
        ),
        [
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2026, 3, 12)),
            VaccinationRecord(product_name="Prevenar 13", administration_date=date(2026, 3, 12)),
            VaccinationRecord(product_name="Rotarix", administration_date=date(2026, 3, 12)),
        ],
    ),
    "marco": (
        Person(
            given_name="Marco", family_name="Rossi",
            birth_date=date(1991, 6, 22), sex=Sex.MALE,
            notes="Adulto sano. Ha fatto richiamo dTpa a 25 anni. FSME in ordine.",
        ),
        [
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1991, 8, 22)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1991, 10, 22)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1991, 12, 22)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(1992, 7, 22)),
            VaccinationRecord(product_name="Prevenar 13", administration_date=date(1991, 8, 22)),
            VaccinationRecord(product_name="Prevenar 13", administration_date=date(1991, 10, 22)),
            VaccinationRecord(product_name="Prevenar 13", administration_date=date(1992, 7, 22)),
            VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(1992, 6, 15)),
            VaccinationRecord(product_name="Priorix-Tetra", administration_date=date(1992, 8, 20)),
            VaccinationRecord(product_name="Adacel-Polio", administration_date=date(1996, 6, 1)),
            VaccinationRecord(product_name="Boostrix", administration_date=date(2007, 6, 22)),
            VaccinationRecord(product_name="Boostrix", administration_date=date(2016, 6, 22)),
            VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2015, 3, 10)),
            VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2015, 4, 15)),
            VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2016, 4, 10)),
            VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2019, 4, 5)),
            VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2023, 4, 8)),
            VaccinationRecord(product_name="Engerix-B", administration_date=date(1992, 3, 1)),
            VaccinationRecord(product_name="Engerix-B", administration_date=date(1992, 4, 1)),
            VaccinationRecord(product_name="Engerix-B", administration_date=date(1992, 8, 1)),
        ],
    ),
    "giovanni": (
        Person(
            given_name="Giovanni", family_name="Verdi",
            birth_date=date(1956, 3, 5), sex=Sex.MALE,
            clinical_conditions=[
                ClinicalCondition(code="diabetes_with_organ_impact", label="Diabete con complicanze d'organo"),
                ClinicalCondition(code="asplenia", label="Asplenia"),
            ],
            notes="Diabete tipo 2 con complicanze. Splenectomia 2018. Vive in zona FSME endemica.",
        ),
        [
            VaccinationRecord(product_name="dT", administration_date=date(2006, 5, 10)),
            VaccinationRecord(product_name="dT", administration_date=date(2016, 5, 10)),
            VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2023, 4, 1)),
            VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2023, 5, 1)),
            VaccinationRecord(product_name="FSME-Immun CC", administration_date=date(2025, 4, 1)),
            VaccinationRecord(product_name="Influvac", administration_date=date(2025, 10, 15)),
            VaccinationRecord(product_name="Prevenar 13", administration_date=date(2018, 11, 1)),
        ],
    ),
}


def main():
    init_db()
    kb = load_knowledge_base(KB_DIR)
    engine = DeterministicRuleEngine()

    session = get_session()
    try:
        patient_repo = PatientRepository(session)
        record_repo = RecordRepository(session)
        report_repo = ReportRepository(session)

        for key, (person, records) in PATIENTS.items():
            db_patient = patient_repo.create(person)
            session.flush()

            for rec in records:
                record_repo.add(rec, db_patient.id)

            report = engine.evaluate(person, records, kb)
            report_repo.save(report, db_patient.id)

            print(f"  ✅ {person.given_name} {person.family_name} — {person.age_years}y — {len(records)} records — {'PASS' if report.overall_compliance else 'FAIL'}")

        session.commit()
        print(f"\n✔ Inseriti {len(PATIENTS)} pazienti demo nel database.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
