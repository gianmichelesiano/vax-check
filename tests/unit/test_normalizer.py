from __future__ import annotations

from datetime import date

from vaxcheck.domain.vaccination import VaccinationRecord
from vaxcheck.normalization.normalizer import group_by_antigen, normalize_records


class TestNormalizeRecords:
    def test_infanrix_hexa_yields_6_doses(self, kb):
        records = [VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 3, 21))]
        doses = normalize_records(records, kb)
        antigens = {d.antigen for d in doses}
        assert antigens == {"D", "T", "Pa", "IPV", "Hib", "HBV"}
        assert len(doses) == 6
        for d in doses:
            assert d.administration_date == date(2018, 3, 21)
            assert d.source_product == "Infanrix hexa"

    def test_clara_14_records_yields_correct_count(self, kb, clara_records):
        doses = normalize_records(clara_records, kb)
        # 4x Infanrix hexa = 24, 3x Prevenar 13 = 3, 2x Priorix-Tetra = 8,
        # 1x Menveo = 1, 1x Adacel-Polio = 4, 3x FSME-Immun Junior = 3
        # Total = 24 + 3 + 8 + 1 + 4 + 3 = 43
        assert len(doses) == 43

    def test_unknown_product_no_exception(self, kb):
        records = [
            VaccinationRecord(product_name="MysteryVax Pro Max", administration_date=date(2020, 1, 1)),
            VaccinationRecord(product_name="Infanrix hexa", administration_date=date(2018, 3, 21)),
        ]
        doses = normalize_records(records, kb)
        # Unknown product skipped, Infanrix hexa → 6 doses
        assert len(doses) == 6

    def test_empty_records(self, kb):
        assert normalize_records([], kb) == []


class TestGroupByAntigen:
    def test_groups_and_sorts(self, kb, clara_records):
        doses = normalize_records(clara_records, kb)
        groups = group_by_antigen(doses)
        assert "D" in groups
        assert len(groups["D"]) == 4  # 4 Infanrix hexa (Adacel-Polio has "d" reduced dose)
        # Sorted by date
        dates = [d.administration_date for d in groups["D"]]
        assert dates == sorted(dates)
