"""Tests run against TEST_DATABASE_URL (optionally inside TEST_DATABASE_SCHEMA).

Each test runs inside one outer transaction that is rolled back at the end, so the
database (including the append-only audit_log) is left exactly as it was.
"""

from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.config import BACKEND_DIR, settings
from app.db import get_db, make_engine
from app.main import app
from app.services.seed_service import seed_policies
from tests.helpers import TEST_AGENT_TOKEN, TEST_JWT_SECRET, People, make_user


@pytest.fixture(scope="session", autouse=True)
def _test_settings() -> Iterator[None]:
    """Tests mint HS256 tokens with a throwaway secret and use a throwaway agent token."""
    names = (
        "supabase_jwt_mode",
        "supabase_jwt_secret",
        "agent_service_token",
        "anthropic_fallbacks",
        "demo_profile_switch",
    )
    saved = {name: getattr(settings, name) for name in names}
    settings.supabase_jwt_mode = "secret"
    settings.supabase_jwt_secret = TEST_JWT_SECRET
    settings.agent_service_token = TEST_AGENT_TOKEN
    settings.anthropic_fallbacks = ""
    # Off unless a test turns it on, whatever backend/.env says.
    settings.demo_profile_switch = False
    yield
    for name, value in saved.items():
        setattr(settings, name, value)


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url, schema = settings.test_database_url, (settings.test_database_schema or None)
    if not url:
        pytest.exit("TEST_DATABASE_URL is not set in backend/.env", returncode=2)
    if url == settings.database_url and not schema:
        pytest.exit("TEST_DATABASE_URL equals DATABASE_URL; set TEST_DATABASE_SCHEMA to isolate tests", returncode=2)

    test_engine = make_engine(url, schema)
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["target"] = "test"
    config.attributes["engine"] = test_engine
    command.upgrade(config, "head")
    with Session(test_engine) as session:
        seed_policies(session)
        session.commit()
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def db(engine: Engine) -> Iterator[Session]:
    connection = engine.connect()
    outer = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        outer.rollback()
        connection.close()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def people(db: Session) -> People:
    result = People(
        hod=make_user(db, "hod", "hod"),
        cm_a=make_user(db, "committee_member", "member-a"),
        cm_b=make_user(db, "committee_member", "member-b"),
    )
    db.commit()
    return result
