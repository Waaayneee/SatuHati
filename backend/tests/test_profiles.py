"""Demo profile switching (X-Profile-Id header, no password)."""

import uuid

import pytest

from app.config import settings
from tests.helpers import AGENT_HEADERS, auth, make_user


def profile(user) -> dict[str, str]:
    return {"X-Profile-Id": str(user.id)}


@pytest.fixture
def switching_on(monkeypatch):
    monkeypatch.setattr(settings, "demo_profile_switch", True)


def test_switching_off_by_default(client, people):
    assert client.get("/profiles").status_code == 404
    assert client.get("/me", headers=profile(people.hod)).status_code == 401


def test_profiles_list_people_with_a_role_hod_first(client, db, people, switching_on):
    no_role = make_user(db, None, "no-role")
    db.commit()
    body = client.get("/profiles").json()
    ids = [p["id"] for p in body]
    assert ids[0] == str(people.hod.id)
    assert {str(people.cm_a.id), str(people.cm_b.id)} <= set(ids)
    assert str(no_role.id) not in ids
    hod = body[0]
    assert (hod["roles"], hod["primary_role"]) == (["hod"], "hod")


def test_profile_header_acts_as_that_person(client, people, switching_on):
    assert client.get("/me", headers=profile(people.hod)).json()["primary_role"] == "hod"
    assert client.get("/me", headers=profile(people.cm_a)).json()["id"] == str(people.cm_a.id)
    # Role rules still apply to the chosen person.
    assert client.get("/users", headers=profile(people.cm_a)).status_code == 403
    assert client.get("/users", headers=profile(people.hod)).status_code == 200


def test_unknown_or_bad_profile_is_refused(client, db, people, switching_on):
    assert client.get("/me", headers={"X-Profile-Id": "not-a-uuid"}).status_code == 401
    assert client.get("/me", headers={"X-Profile-Id": str(uuid.uuid4())}).status_code == 403
    no_role = make_user(db, None, "no-role")
    db.commit()
    assert client.get("/me", headers=profile(no_role)).status_code == 403


def test_bearer_and_agent_token_win_over_profile(client, people, switching_on):
    both = {**auth(people.cm_a), **profile(people.hod)}
    assert client.get("/me", headers=both).json()["id"] == str(people.cm_a.id)
    # The agent stays the agent, even with a person's profile attached.
    assert client.get("/missions", headers={**AGENT_HEADERS, **profile(people.hod)}).status_code == 403


def test_cors_allows_profile_header(client):
    response = client.options(
        "/me",
        headers={
            "Origin": settings.frontend_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Profile-Id",
        },
    )
    assert response.status_code == 200
    assert "x-profile-id" in response.headers.get("access-control-allow-headers", "").lower()
