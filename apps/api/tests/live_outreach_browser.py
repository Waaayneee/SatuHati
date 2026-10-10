"""Run controlled outreach UI against saved Supabase state, then restore that sample."""

import subprocess
from pathlib import Path
from uuid import uuid4

from kawteam.config import Settings
from kawteam.repository import SupabaseRepository, payload_hash

repo = SupabaseRepository(Settings())
original = repo.get("case", "case-totes")
try:
    subprocess.run(
        ["node", "tests/outreach-browser.mjs"], cwd=Path(__file__).parents[2] / "web", check=True
    )
    updated = repo.get("case", "case-totes")
    assert updated["selectedVendorId"] == original["selectedVendorId"], (
        "Outreach made an unauthorised decision"
    )
    assert len(updated.get("messages", [])) == len(original.get("messages", [])) + 2
    print("PASS: outreach never changed the human supplier decision.")
finally:
    current = repo.get("case", "case-totes")
    repo.save(
        "case",
        original,
        current["backendRevision"],
        "organiser",
        str(uuid4()),
        payload_hash(original),
    )
    print("Original sample case restored.")
