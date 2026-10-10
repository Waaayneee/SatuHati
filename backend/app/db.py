import re
from collections.abc import Iterator

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

_SCHEMA_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


def make_engine(url: str, schema: str | None = None) -> Engine:
    """Engine for a Supabase session pooler URL. With `schema`, every connection
    uses only that schema (search_path), which keeps tests isolated from dev data."""
    if not url:
        raise RuntimeError("Database URL is not set. Fill DATABASE_URL in backend/.env.")
    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        connect_args={"connect_timeout": 5},
    )
    if schema:
        if not _SCHEMA_RE.match(schema):
            raise ValueError(f"Invalid schema name: {schema!r}")

        @event.listens_for(engine, "connect")
        def _set_search_path(dbapi_connection, _record):  # noqa: ANN001
            autocommit = dbapi_connection.autocommit
            dbapi_connection.autocommit = True
            with dbapi_connection.cursor() as cursor:
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
                cursor.execute(f'SET search_path TO "{schema}"')
            dbapi_connection.autocommit = autocommit

    return engine


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = make_engine(settings.database_url)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)
    return _session_factory


def get_db() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def check_connection(engine: Engine) -> bool:
    with engine.connect() as conn:
        return conn.execute(text("SELECT 1")).scalar_one() == 1


def tables_ready(engine: Engine) -> bool:
    """True when the KawTeam migrations have run (checks one core table on the search path)."""
    with engine.connect() as conn:
        return conn.execute(text("SELECT to_regclass('role_assignments') IS NOT NULL")).scalar_one()
