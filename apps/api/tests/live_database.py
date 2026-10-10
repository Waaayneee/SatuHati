"""Explicit opt-in integration check against the configured hackathon database.

Creates one labelled disposable event. Never prints environment credentials.
"""

from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from kawteam.config import Settings
from kawteam.repository import SupabaseRepository, payload_hash


def main():
    repo = SupabaseRepository(Settings())
    event_id = "qa-atomic-" + str(uuid4())
    event = {"id": event_id, "name": "QA atomic transaction", "facts": {}, "sample": True}
    repo.save("event", event, 0, "organiser", str(uuid4()), payload_hash(event))
    doc = {
        "id": str(uuid4()),
        "eventId": event_id,
        "name": "qa.txt",
        "text": "Budget RM1000",
        "originalBase64": "cWE=",
        "contentDigest": payload_hash({"text": "same-file"}),
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        uploads = list(
            pool.map(lambda _: repo.upload(doc, {"budgetSen": 100000}, "organiser"), range(2))
        )
    assert uploads[0]["id"] == uploads[1]["id"]
    assert all("originalBase64" not in d and "text" not in d for d in uploads)
    assert repo.get("event", event_id)["memoryVersion"] == 1
    assert len(repo.documents(event_id)) == 1
    user = {"id": str(uuid4()), "role": "user", "body": "Find vendors"}
    with ThreadPoolExecutor(max_workers=2) as pool:
        threads = list(
            pool.map(lambda _: repo.append_message(event_id, user, "organiser"), range(2))
        )
    assert all(len(t["messages"]) == 1 for t in threads)
    from kawteam.main import create_case

    case = create_case(
        {
            "title": "QA disposable request",
            "goal": "Test concurrent finalization",
            "quantity": 300,
            "budgetSen": 100000,
            "targetSen": 90000,
            "deadline": "2026-10-25",
            "location": "Subang Jaya",
        },
        "qa-case-" + str(uuid4()),
        event_id,
    )
    assistant = {
        "id": str(uuid4()),
        "role": "assistant",
        "body": "Saved",
        "inReplyTo": user["id"],
        "caseId": case["id"],
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        final = list(
            pool.map(
                lambda _: repo.append_message(event_id, assistant, "organiser", case), range(2)
            )
        )
    assert all(len(t["messages"]) == 2 for t in final)
    assert repo.get("case", case["id"])["backendRevision"] == 1
    try:
        repo.append_message(event_id, {**user, "body": "Different request"}, "organiser")
        raise AssertionError("Changed idempotency payload accepted")
    except ValueError:
        pass
    wrong = SupabaseRepository(Settings(database_secret="invalid" * 8))
    try:
        wrong.snapshot()
        raise AssertionError("Bad database credential accepted")
    except PermissionError:
        pass
    print(
        "PASS: concurrent uploads, concurrent chat retries, single case, sanitized metadata, invalid credential rejection."
    )
    print("Disposable event:", event_id)


if __name__ == "__main__":
    main()
