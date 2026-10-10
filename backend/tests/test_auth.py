"""Authentication and actor resolution."""

import time
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from app.auth import tokens
from app.config import settings
from tests.helpers import AGENT_HEADERS, auth, make_user, token_for


def test_missing_and_bad_tokens_are_401(client):
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers={"Authorization": "Bearer not-a-jwt"}).status_code == 401
    expired = token_for(uuid.uuid4(), exp=int(time.time()) - 3600)
    assert client.get("/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    wrong_aud = token_for(uuid.uuid4(), aud="anon")
    assert client.get("/me", headers={"Authorization": f"Bearer {wrong_aud}"}).status_code == 401


def test_unknown_user_and_user_without_role_are_403(client, db):
    assert client.get("/me", headers={"Authorization": f"Bearer {token_for(uuid.uuid4())}"}).status_code == 403
    no_role = make_user(db, None, "no-role")
    db.commit()
    assert client.get("/me", headers=auth(no_role)).status_code == 403


def test_me_returns_roles(client, people):
    body = client.get("/me", headers=auth(people.hod)).json()
    assert (body["roles"], body["primary_role"]) == (["hod"], "hod")
    body = client.get("/me", headers=auth(people.cm_a)).json()
    assert body["primary_role"] == "committee_member"


def test_agent_token(client, people):
    assert client.get("/agent/tools", headers=AGENT_HEADERS).status_code == 200
    assert client.get("/agent/tools", headers={"X-Agent-Token": "wrong"}).status_code == 401
    # The agent is not a person: user endpoints refuse it.
    assert client.get("/missions", headers=AGENT_HEADERS).status_code == 403
    # People cannot use agent endpoints.
    assert client.get("/agent/tools", headers=auth(people.hod)).status_code == 403


def test_empty_configured_agent_token_never_authenticates(client, monkeypatch):
    monkeypatch.setattr(settings, "agent_service_token", "")
    assert client.get("/agent/tools", headers={"X-Agent-Token": ""}).status_code == 401


def test_users_endpoint_is_hod_only(client, people):
    assert client.get("/users", headers=auth(people.cm_a)).status_code == 403
    emails = [u["email"] for u in client.get("/users", headers=auth(people.hod)).json()]
    assert people.cm_a.email in emails


def test_cors_allows_only_frontend_origin(client):
    ok = client.options("/me", headers={"Origin": settings.frontend_origin, "Access-Control-Request-Method": "GET"})
    assert ok.headers.get("access-control-allow-origin") == settings.frontend_origin
    bad = client.options("/me", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in bad.headers


@pytest.fixture
def local_jwks(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    public = jwt.PyJWK.from_dict(
        {**jwt.algorithms.ECAlgorithm.to_jwk(key.public_key(), as_dict=True), "alg": "ES256", "kid": "test"}
    )

    class FakeJWKS:
        def get_signing_key_from_jwt(self, _token):
            return public

    monkeypatch.setattr(settings, "supabase_jwt_mode", "jwks")
    monkeypatch.setattr(tokens, "_jwks_client", FakeJWKS())
    return key


def _claims(**overrides):
    now = int(time.time())
    return {
        "sub": str(uuid.uuid4()),
        "aud": "authenticated",
        "iss": settings.supabase_issuer,
        "role": "authenticated",
        "iat": now,
        "exp": now + 300,
        **overrides,
    }


def test_jwks_mode_accepts_valid_es256_token(local_jwks):
    claims = _claims()
    assert tokens.verify_access_token(jwt.encode(claims, local_jwks, algorithm="ES256"))["sub"] == claims["sub"]


@pytest.mark.parametrize(
    "overrides",
    [{"aud": "anon"}, {"iss": "https://evil.example/auth/v1"}, {"exp": int(time.time()) - 600}, {"role": "anon"}],
)
def test_jwks_mode_rejects_bad_claims(local_jwks, overrides):
    with pytest.raises(tokens.TokenError):
        tokens.verify_access_token(jwt.encode(_claims(**overrides), local_jwks, algorithm="ES256"))


def test_jwks_mode_rejects_forged_signature(local_jwks):
    forger = ec.generate_private_key(ec.SECP256R1())
    with pytest.raises(tokens.TokenError):
        tokens.verify_access_token(jwt.encode(_claims(), forger, algorithm="ES256"))


def test_jwks_mode_rejects_hs256_token(local_jwks):
    with pytest.raises(tokens.TokenError):
        tokens.verify_access_token(jwt.encode(_claims(), "x" * 32, algorithm="HS256"))
