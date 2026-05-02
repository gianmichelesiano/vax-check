"""Lightweight schema version tracking and migration runner.

Used instead of Alembic — adequate for a single-machine, single-dev, 3-table schema.
"""

from __future__ import annotations

from sqlalchemy import Column, Connection, Integer, MetaData, Table, text
from sqlalchemy.engine import Engine

SCHEMA_VERSION = 1

_SCHEMA_VERSION_TABLE = Table(
    "_schema_version",
    MetaData(),
    Column("version", Integer, nullable=False),
)


def _ensure_tracking_table(conn: Connection) -> None:
    conn.execute(text("CREATE TABLE IF NOT EXISTS _schema_version (version INTEGER NOT NULL)"))
    result = conn.execute(text("SELECT COUNT(*) FROM _schema_version")).scalar()
    if result == 0:
        conn.execute(text("INSERT INTO _schema_version (version) VALUES (0)"))


def get_schema_version(conn: Connection) -> int:
    _ensure_tracking_table(conn)
    result = conn.execute(text("SELECT version FROM _schema_version")).scalar()
    return int(result)  # type: ignore[arg-type]  # guaranteed non-None by _ensure_tracking_table


def set_schema_version(conn: Connection, version: int) -> None:
    conn.execute(text("UPDATE _schema_version SET version = :v"), {"v": version})


def run_migrations(engine: Engine) -> None:
    with engine.begin() as conn:
        current = get_schema_version(conn)

        if current < 1:
            _migrate_v0_to_v1(conn)
            set_schema_version(conn, 1)

        # future migrations: if current < 2: _migrate_v1_to_v2(conn); set_schema_version(conn, 2)


def _migrate_v0_to_v1(conn: Connection) -> None:
    """Baseline — all tables already created by Base.metadata.create_all().

    This migration just marks version 1. Future schema changes will
    add actual DDL here.
    """
    pass
