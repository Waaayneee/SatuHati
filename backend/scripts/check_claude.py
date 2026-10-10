"""Sends one short message to Claude and prints the model name and the first
line of the reply. Never prints the API key.

Usage (from backend/):  python -m scripts.check_claude
"""

import sys

import anthropic

from app.config import settings


def main() -> int:
    if not settings.anthropic_api_key:
        print("ANTHROPIC_API_KEY: NOT SET")
        return 1
    if not settings.anthropic_model:
        print("ANTHROPIC_MODEL: NOT SET")
        return 1

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=60.0)
    try:
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=2048,
            messages=[{"role": "user", "content": "Reply with exactly: KawTeam check OK"}],
        )
    except anthropic.AuthenticationError:
        print("Claude check FAILED: the API key was rejected")
        return 1
    except anthropic.NotFoundError:
        print(f"Claude check FAILED: model {settings.anthropic_model!r} not found")
        return 1
    except anthropic.APIStatusError as exc:
        print(f"Claude check FAILED: HTTP {exc.status_code}")
        return 1
    except anthropic.APIConnectionError:
        print("Claude check FAILED: network error")
        return 1

    text = next((b.text for b in response.content if b.type == "text"), "")
    first_line = text.strip().splitlines()[0] if text.strip() else "(empty reply)"
    print(f"model: {response.model}")
    print(f"reply: {first_line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
