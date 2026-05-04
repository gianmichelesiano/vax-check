from vaxcheck.domain.knowledge import KnowledgeBase


def normalize_product_name(
    raw_name: str,
    kb: KnowledgeBase,
) -> tuple[str | None, float]:
    """Trova il prodotto nel catalogo corrispondente al nome raw estratto dall'OCR.

    Returns: (normalized_name, match_confidence)
    """
    clean = raw_name.strip().lower()

    product = kb.find_product(clean)
    if product:
        return product.name, 1.0

    for p in kb.products:
        if p.name.lower() in clean or clean in p.name.lower():
            return p.name, 0.8
        for alias in p.aliases:
            if alias.lower() in clean or clean in alias.lower():
                return p.name, 0.8

    raw_tokens = set(clean.split())
    for p in kb.products:
        catalog_tokens = set(p.name.lower().split())
        for alias in p.aliases:
            catalog_tokens |= set(alias.lower().split())
        overlap = raw_tokens & catalog_tokens
        if len(overlap) >= 2 and len(overlap) / max(len(raw_tokens), 1) >= 0.5:
            return p.name, 0.6

    return None, 0.0
