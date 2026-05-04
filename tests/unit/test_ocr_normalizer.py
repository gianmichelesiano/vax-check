from vaxcheck.ocr.normalizer import normalize_product_name


def test_exact_match(kb):
    name, conf = normalize_product_name("Infanrix hexa", kb)
    assert name == "Infanrix hexa"
    assert conf == 1.0


def test_exact_match_case_insensitive(kb):
    name, conf = normalize_product_name("infanrix HEXA", kb)
    assert name == "Infanrix hexa"
    assert conf == 1.0


def test_alias_in_kb_matches_exact(kb):
    """KB has Prevenar13 as alias — match is exact (1.0)."""
    name, conf = normalize_product_name("Prevenar13", kb)
    assert name == "Prevenar 13"
    assert conf == 1.0


def test_partial_match(kb):
    name, conf = normalize_product_name("Infanrix hexa +5", kb)
    assert name == "Infanrix hexa"
    assert conf >= 0.6


def test_unknown_product(kb):
    name, conf = normalize_product_name("VaccinoXYZ sconosciuto", kb)
    assert name is None
    assert conf == 0.0
