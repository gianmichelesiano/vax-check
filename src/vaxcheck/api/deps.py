from functools import lru_cache
from pathlib import Path

from vaxcheck.persistence.session import get_session
from vaxcheck.kb.loader import load_knowledge_base
from vaxcheck.rule_engine.deterministic.engine import DeterministicRuleEngine


def get_db():
    with get_session() as session:
        yield session


@lru_cache
def get_kb():
    return load_knowledge_base(Path("kb"))  # language from KB_LANGUAGE env var or "IT"


@lru_cache
def get_engine():
    return DeterministicRuleEngine()
