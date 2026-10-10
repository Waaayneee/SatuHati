"""Step 1.1 check: proves UPDATE, DELETE and TRUNCATE on audit_log fail.

Everything runs inside one transaction that is rolled back, so the probe row
never stays in the append-only table.

Usage (from backend/):  python -m scripts.check_audit_append_only [--target test]
"""

import argparse
import sys

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.config import settings
from app.db import make_engine


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["dev", "test"], default="dev")
    args = parser.parse_args()
    if args.target == "test":
        engine = make_engine(settings.test_database_url, settings.test_database_schema or None)
    else:
        engine = make_engine(settings.database_url)

    all_blocked = True
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            row_id = conn.execute(
                text(
                    "INSERT INTO audit_log (actor, event_type, status) "
                    "VALUES ('system:check', 'system.append_only_probe', 'ok') RETURNING id"
                )
            ).scalar_one()
            for label, sql in [
                ("UPDATE", "UPDATE audit_log SET status = 'tampered' WHERE id = :id"),
                ("DELETE", "DELETE FROM audit_log WHERE id = :id"),
                ("TRUNCATE", "TRUNCATE audit_log"),
            ]:
                savepoint = conn.begin_nested()
                try:
                    conn.execute(text(sql), {"id": row_id})
                    savepoint.rollback()
                    print(f"{label} audit_log: ALLOWED (problem)")
                    all_blocked = False
                except DBAPIError as exc:
                    savepoint.rollback()
                    message = str(exc.orig).splitlines()[0]
                    print(f"{label} audit_log: blocked ({message})")
        finally:
            trans.rollback()
    engine.dispose()
    return 0 if all_blocked else 1


if __name__ == "__main__":
    sys.exit(main())
