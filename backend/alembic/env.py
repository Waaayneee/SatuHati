from alembic import context
from sqlalchemy import Engine

from app.config import settings
from app.db import make_engine
from app.models import Base

config = context.config
target_metadata = Base.metadata


def _target() -> str:
    """`dev` (default) or `test`, from `alembic -x target=test` or config attributes."""
    target = config.attributes.get("target") or context.get_x_argument(as_dictionary=True).get("target", "dev")
    if target not in ("dev", "test"):
        raise ValueError(f"Unknown target {target!r}. Use dev or test.")
    return target


def _url_and_schema() -> tuple[str, str | None]:
    if _target() == "test":
        if not settings.test_database_url:
            raise RuntimeError("TEST_DATABASE_URL is not set in backend/.env")
        return settings.test_database_url, (settings.test_database_schema or None)
    return settings.database_url, None


def run_migrations_offline() -> None:
    url, schema = _url_and_schema()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=schema,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine: Engine | None = config.attributes.get("engine")
    url, schema = _url_and_schema()
    owns_engine = engine is None
    if engine is None:
        engine = make_engine(url, schema)
    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                version_table_schema=schema,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        if owns_engine:
            engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
