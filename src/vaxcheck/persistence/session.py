"""Database engine and session management for SQLite persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from vaxcheck.persistence.models import Base

_DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
DEFAULT_DB_PATH = _DEFAULT_DB_DIR / "vaxcheck.db"

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine(db_path: Path | None = None) -> Engine:
    """Return (cached) SQLite engine with WAL mode and foreign keys enabled."""
    global _engine, _SessionLocal

    if db_path is None:
        db_path = DEFAULT_DB_PATH

    if _engine is None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{db_path.resolve()}"

        _engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=False,
        )

        @event.listens_for(_engine, "connect")
        def _set_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

    return _engine


def init_db(db_path: Path | None = None) -> None:
    """Create all tables and run migrations. Idempotent."""
    from vaxcheck.persistence.schema import run_migrations

    engine = get_engine(db_path)
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)


def get_session() -> Session:
    """Return a new SQLAlchemy Session. Caller must close it."""
    if _SessionLocal is None:
        get_engine()
    assert _SessionLocal is not None
    return _SessionLocal()
