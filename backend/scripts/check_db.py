"""Runs SELECT 1 against DATABASE_URL and TEST_DATABASE_URL.

Usage (from backend/):  python -m scripts.check_db
"""

import sys

from app.config import settings
from app.db import check_connection, make_engine


def _check(label: str, url: str, schema: str | None = None) -> bool:
    if not url:
        print(f"{label}: NOT SET")
        return False
    where = f" (schema {schema})" if schema else ""
    try:
        engine = make_engine(url, schema)
        ok = check_connection(engine)
        engine.dispose()
    except Exception as exc:  # report the class only, never the URL
        print(f"{label}{where}: FAILED ({type(exc).__name__})")
        return False
    print(f"{label}{where}: {'OK' if ok else 'FAILED'}")
    return ok


def main() -> int:
    dev_ok = _check("DATABASE_URL", settings.database_url)
    test_ok = _check("TEST_DATABASE_URL", settings.test_database_url, settings.test_database_schema or None)
    return 0 if dev_ok and test_ok else 1


if __name__ == "__main__":
    sys.exit(main())
