"""Seed clearly labelled examples once. Does not overwrite existing records."""

import base64
from uuid import uuid4

from .config import Settings
from .repository import SupabaseRepository, payload_hash
from .workflow import seed


def main():
    repo = SupabaseRepository(Settings())
    event = {
        "id": "tech-night",
        "name": "Tech Night",
        "sample": True,
        "memoryVersion": 1,
        "facts": {
            "budgetSen": 150000,
            "quantity": 300,
            "deadline": "2026-10-25",
            "location": "Subang Jaya, Selangor",
        },
        "createdAt": "2026-10-10T10:00:00+08:00",
    }
    text = """# Tech Night — illustrative event proposal
Technology Club welcomes 200 students for an evening technology showcase.
Procurement requirement: 300 cotton tote bags with one-colour club logo printing.
Supplier budget: RM1500 maximum, printing and delivery included. Target RM1350.
Delivery deadline: 2026-10-25
Location: Subang Jaya, Selangor
Artwork proof must be reviewed before production. The organising team chooses the final supplier.
This is sample event data for the hackathon demonstration, not a real booking.
"""
    document = {
        "id": "sample-tech-proposal",
        "eventId": event["id"],
        "name": "Tech Night — sample proposal.md",
        "text": text,
        "originalBase64": base64.b64encode(text.encode()).decode(),
        "size": len(text.encode()),
        "status": "ready",
        "characters": len(text),
        "sample": True,
        "createdAt": event["createdAt"],
    }
    rows = [("event", event), ("document", document)]
    for c in seed()["cases"]:
        c["messages"] = []
        if c["id"] == "case-totes":
            c["eventId"] = event["id"]
            for v in c["vendors"]:
                v.update(quantity=300, validUntil="2026-10-15", executionMode="demo")
        rows.append(("case", c))
    for kind, data in rows:
        if not repo.get(kind, data["id"]):
            repo.save(kind, data, 0, "organiser", str(uuid4()), payload_hash(data))
    snapshot = repo.snapshot()
    print(
        f"Supabase verified: {len(snapshot['cases'])} cases, {len(snapshot['events'])} events, {len(snapshot['documents'])} documents. Existing data preserved."
    )


if __name__ == "__main__":
    main()
