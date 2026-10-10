"""Idempotent seed for the dev database.

1. Creates `users` and `role_assignments` for SEED_HOD_EMAIL (hod) and
   SEED_COMMITTEE_EMAILS (committee_member), reading their IDs from Supabase
   `auth.users` through the database connection.
2. Inserts or updates the approval policies.

Usage (from backend/):  python -m scripts.seed
"""

import sys

from sqlalchemy.orm import Session

from app.config import settings
from app.db import make_engine
from app.models.enums import Role
from app.services.seed_service import SeedUser, lookup_auth_user_ids, seed_policies, seed_users


def main() -> int:
    hod = settings.seed_hod_email.strip().lower()
    committee = settings.seed_committee_email_list
    if not hod or not committee:
        print("Set SEED_HOD_EMAIL and SEED_COMMITTEE_EMAILS in backend/.env first.")
        return 1
    if hod in committee:
        print("SEED_HOD_EMAIL must not also be in SEED_COMMITTEE_EMAILS.")
        return 1

    wanted = [SeedUser(hod, Role.HOD)] + [SeedUser(email, Role.COMMITTEE_MEMBER) for email in committee]
    engine = make_engine(settings.database_url)
    with Session(engine) as db:
        auth_ids = lookup_auth_user_ids(db, [w.email for w in wanted])
        missing = [w.email for w in wanted if w.email not in auth_ids]
        if missing:
            print("These emails are not in Supabase Auth (create them first, or paste their user IDs):")
            for email in missing:
                print(f"  - {email}")
            return 1

        results = seed_users(db, wanted, auth_ids)
        policies_written = seed_policies(db)
        db.commit()

    for r in results:
        print(f"{r.role.value:<17} {r.email:<36} {r.user_id}  {'updated' if r.changed else 'unchanged'}")
    print(f"approval policies written: {policies_written}")
    engine.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
