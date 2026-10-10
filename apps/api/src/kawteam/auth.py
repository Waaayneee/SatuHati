import base64
import hashlib
import hmac
import json
import time

ROLES = {"organiser", "teammate", "observer"}


def issue_session(role: str, workspace: str, secret: str, now: int | None = None) -> str:
    if role not in ROLES:
        raise ValueError("Unknown demo profile")
    claims = {"role": role, "workspace": workspace, "exp": (now or int(time.time())) + 86400}
    body = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def verify_session(token: str, workspace: str, secret: str, now: int | None = None) -> str:
    try:
        body, signature = token.split(".")
        expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("Invalid session")
        claims = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if claims["workspace"] != workspace or claims["exp"] <= (now or int(time.time())):
            raise ValueError("Expired or wrong-workspace session")
        if claims["role"] not in ROLES:
            raise ValueError("Unknown role")
        return claims["role"]
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid session") from error
