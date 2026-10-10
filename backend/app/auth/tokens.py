"""Supabase access token verification (JWKS or legacy shared secret)."""

from typing import Any

import jwt

from app.config import settings

ASYMMETRIC_ALGORITHMS = {"ES256", "RS256", "EdDSA"}


class TokenError(Exception):
    pass


_jwks_client: jwt.PyJWKClient | None = None


def _jwks() -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = jwt.PyJWKClient(settings.supabase_jwks_url, cache_keys=True, lifespan=600, timeout=10)
    return _jwks_client


def verify_access_token(token: str) -> dict[str, Any]:
    """Returns the claims of a valid Supabase user access token, else raises TokenError."""
    if not settings.supabase_url:
        raise TokenError("SUPABASE_URL is not configured")
    common: dict[str, Any] = {
        "audience": "authenticated",
        "issuer": settings.supabase_issuer,
        "options": {"require": ["exp", "sub", "aud", "iss"]},
        "leeway": 30,
    }
    try:
        if settings.supabase_jwt_mode == "jwks":
            signing_key = _jwks().get_signing_key_from_jwt(token)
            if signing_key.algorithm_name not in ASYMMETRIC_ALGORITHMS:
                raise TokenError("Unexpected signing algorithm")
            claims = jwt.decode(token, signing_key.key, algorithms=[signing_key.algorithm_name], **common)
        else:
            if not settings.supabase_jwt_secret:
                raise TokenError("SUPABASE_JWT_SECRET is not configured")
            claims = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], **common)
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
    if claims.get("role") != "authenticated":
        raise TokenError("Not a user access token")
    return claims
