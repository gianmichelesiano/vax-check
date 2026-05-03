from fastapi import APIRouter, Depends

from vaxcheck.api.deps import get_kb
from vaxcheck.api.schemas import VaccineProductOut
from vaxcheck.domain.knowledge import KnowledgeBase

router = APIRouter(tags=["catalog"])


@router.get("/catalog/products", response_model=list[VaccineProductOut])
def list_products(kb: KnowledgeBase = Depends(get_kb)):
    return [
        VaccineProductOut(
            name=p.name,
            aliases=p.aliases,
            manufacturer=p.manufacturer,
            antigens=p.antigens,
            notes=p.notes,
        )
        for p in kb.products
    ]


@router.get("/kb/version")
def kb_version(kb: KnowledgeBase = Depends(get_kb)):
    return {"version": kb.version, "date": kb.version}
